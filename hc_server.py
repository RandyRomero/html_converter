# -*- coding: utf-8 -*- 

"""
hc_server

Usage:
hc_server.py  [-h | --help]
hc_server.py  [--server-host=<s_host>] [--server-port=<s_port>] [--athenapdf-host=<a_host>] [--athenapdf-port=<a_port>]


Options:
-h  --help                  Show this screen
--server-host=<s_host>   Specify host for this app [default: 127.0.0.1].
--server-port=<s_port>   Specify port for this app [default: 8181]
--athenapdf-host=<a_host>   Specify host where this app will be looking for Athenapdf [default: 127.0.0.1]
--athenapdf-port=<a_port>   Specify port where this app will be looking for Athenapdf [default: 8080]

"""


import aiohttp
from aiohttp import web
import hashlib
from set_up_logging import get_logger
from docopt import docopt


logger = get_logger(__name__)


async def get_pdf(md5, addresses):
    async with aiohttp.ClientSession() as session:
        server_host = addresses['s_host']
        server_port = addresses['s_port']
        athenapdf_host = addresses['a_host']
        athenapdf_port = addresses['a_port']

        url = (f'http://{server_host}:{server_port}/convert?auth=arachnys-'
               f'weaver&url=http://{athenapdf_host}:{athenapdf_port}/raw/{md5}')

        logger.debug('Trying to connect to Athenapdf with url: %s', url)
        async with session.get(url) as response:
            if response.status == 200:
                logger.debug('Got the pdf file from Athenapdf')
                raw_pdf = await response.content.read()
                return raw_pdf
            else:
                logger.error('Athenapdf converter responded with status code: %d\nMessage: %s',
                             response.status, await response.text())
                return 1


async def get_raw_html(request):
    logger.debug('Got request to return html by its md5...')

    # Getting md5 key from the request
    md5 = request.match_info.get('md5', None)

    html = request.app['htmls'].get(md5, None)
    if not html:
        logger.error('There is no entry for your md5 key.')
        return web.Response(text='There is no data for this key', status=404)

    logger.debug('Returning queried html as a string...')
    return web.Response(body=html, content_type='text/html')


async def generate(request):
    logger.debug('Got request to generate pdf...')
    text = await request.text()

    logger.debug('Getting md5 from a given html...')
    md5 = hashlib.md5(text.encode('utf-8')).hexdigest()

    # store html by its md5
    logger.debug('Saving the html in app by its md5...')
    request.app['htmls'][md5] = text

    pdf_raw_file = await get_pdf(md5, request.app['addresses'])
    if pdf_raw_file == 1:
        return web.Response(text="Athenapdf converter can't handle this request right now", status=404)

    del request.app['htmls'][md5]
    assert request.app['htmls'].get(md5, None) == None, "The html string haven't been removed!"

    logger.debug('Returning pdf to the user...')
    return web.Response(body=pdf_raw_file, status=200, content_type='application/pdf')


def main():
    print('Server initializing...')

    # parsing command line arguments
    arguments = docopt(__doc__)

    app = web.Application()

    # make storage that is available for the whole app for storing html files by theirs md5 keys
    app['htmls'] = {}

    app['addresses'] = {'s_host': arguments['--server-host'],
                        's_port': arguments['--server-port'],
                        'a_host': arguments['--athenapdf-host'],
                        'a_port': arguments['--athenapdf-port']}

    app.router.add_get('/raw/{md5}', get_raw_html)
    app.router.add_post('/generate', generate)

    web.run_app(app, host=arguments['--server-host'], port=arguments['--server-port'])


if __name__ == '__main__':
    main()