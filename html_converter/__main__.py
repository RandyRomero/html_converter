"""
html_converter

Usage:
html_converter [-h | --help]
html_converter [--server-host=<s_host>] [--server-port=<s_port>]
               [--athenapdf-host=<a_host>] [--athenapdf-port=<a_port>]

Options:
-h  --help                  Show this screen
--server-host=<s_host>  Specify host for this app [default: 127.0.0.1]
--server-port=<s_port>  Specify port for this app [default: 8181]
--athenapdf-host=<a_host>  Specify host where this app will be looking for
                           Athenapdf [default: 127.0.0.1]
--athenapdf-port=<a_port>  Specify port where this app will be looking for
                           Athenapdf [default: 8080]

"""

import aiohttp
from aiohttp import web
from uuid import uuid4
from typing import NamedTuple
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from docopt import docopt  # type: ignore

from html_converter.set_up_logging import get_logger

logger = get_logger(__name__)


# namedtuple to store command line arguments
class Commands(NamedTuple):
    name: str
    s_host: str
    s_port: str
    a_host: str
    a_port: str


async def get_pdf(uuid: str, addresses: Commands) -> bytes:
    """
    Connects to Athenapdf microservice in order to get pdf file from
    a given html file and returns it back to a client

    :param uuid: key for getting html file from this app
    :param addresses: namedtuple with html files stored by uuid
    :return: pdf file as bytes
    """

    url = (f"http://{addresses.a_host}:{addresses.a_port}"
           "/convert?auth=arachnys-weaver&url=http://"
           f"{addresses.s_host}:{addresses.s_port}/raw/{uuid}")

    async with aiohttp.ClientSession() as session:
        logger.debug('Trying to connect to Athenapdf with url: %s', url)
        async with session.get(url) as response:
            response.raise_for_status()
            logger.debug('Got the pdf file from Athenapdf')
            raw_pdf = await response.content.read()
            return raw_pdf


async def get_raw_html(request: Request) -> Response:
    """
    Getting stored html file from instance of this app by uuid as a key
    :param request: request of the client which we need to get access to
                    instance of this app
    :return: web.Response either with a corresponding html file or with
             error message
    """

    logger.debug('Got request to return html by uuid...')

    # Getting uuid from the request
    uuid = request.match_info.get('uuid', None)

    # Getting html file from instance of this app by uuid key
    html = request.app['htmls'].get(uuid, None)
    if not html:
        logger.error('There is no entry for your uuid key.')
        return web.Response(text='There is no data for this key', status=404)

    logger.debug('Returning queried html as a string...')
    return web.Response(body=html, content_type='text/html')


async def generate(request: Request) -> Response:
    """
    The function gets html file from a request as a text,
    generates uuid and store this html file by the uuid in the application
    context, calls another function to get pdf file from html,
    and returns the pdf file

    :param request: request object with html file to be processed
    :return: web.Response object with either pdf file as bytes or with error
             message
    """

    logger.debug('Got request to generate pdf...')

    # Getting client's html file as a string
    text = await request.text()

    logger.debug('Saving the html in app by unique uuid...')
    uuid = str(uuid4())
    request.app['htmls'][uuid] = text

    try:
        response = await get_pdf(uuid, request.app['addresses'])

    except aiohttp.ClientResponseError as e:
        error_message = f"Athenapdf returned an error ({e})"
        logger.error(error_message)
        return web.Response(text=error_message, status=500)

    except aiohttp.client_exceptions.ClientConnectorError as e:
        error_message = ("The app cannot connect to the Athenapdf, "
                         "check whether it's alive and on the right "
                         f"host and port. Reason: {e}")
        logger.error(error_message)
        return web.Response(text=error_message, status=500)

    del request.app['htmls'][uuid]

    logger.debug('Returning pdf to the user...')
    return web.Response(body=response, status=200,
                        content_type='application/pdf')


def main() -> None:
    """
    Parsing command line arguments, creating app instance, store ports and
    hosts in the application context
    to be used later, register views, run app

    :return: None
    """
    logger.info('Server initializing...')

    # parsing command line arguments
    arguments = docopt(__doc__)

    app = web.Application()

    # make storage that is available for the whole app for storing html files
    # by uuids
    app['htmls'] = {}

    # adding commands to namedtuple
    commands = Commands('commands',
                        s_host=arguments['--server-host'],
                        s_port=arguments['--server-port'],
                        a_host=arguments['--athenapdf-host'],
                        a_port=arguments['--athenapdf-port']
                        )

    app['addresses'] = commands

    app.router.add_get('/raw/{uuid}', get_raw_html)
    app.router.add_post('/generate', generate)

    web.run_app(app, host=arguments['--server-host'],
                port=arguments['--server-port'])


if __name__ == '__main__':
    main()
