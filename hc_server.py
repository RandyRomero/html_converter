# -*- coding: utf-8 -*- 

import aiohttp
from aiohttp import web
import hashlib
from set_up_logging import get_logger


logger = get_logger(__name__)


async def get_pdf(md5):
    async with aiohttp.ClientSession() as session:
        url = f'http://127.0.0.1:8080/convert?auth=arachnys-weaver&url=http://127.0.0.1:8181/raw/{md5}'
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

    pdf_raw_file = await get_pdf(md5)
    if pdf_raw_file == 1:
        return web.Response(text="Athenapdf converter can't handle this request right now", status=404)

    del request.app['htmls'][md5]
    assert request.app['htmls'].get(md5, None) == None, "The html string haven't been removed!"

    logger.debug('Returning pdf to the user...')
    return web.Response(body=pdf_raw_file, status=200, content_type='application/pdf')


def main():
    logger.debug('Server initializing...')
    app = web.Application()
    app['htmls'] = {}
    app.router.add_get('/raw/{md5}', get_raw_html)
    app.router.add_post('/generate', generate)

    web.run_app(app, host='127.0.0.1', port='8181')


if __name__ == '__main__':
    main()

# https://stackoverflow.com/questions/24319662/from-inside-of-a-docker-container-how-do-i-connect-to-the-localhost-of-the-mach