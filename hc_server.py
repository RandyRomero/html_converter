# -*- coding: utf-8 -*- 

import logging
from aiohttp import web
import hashlib
from set_up_logging import get_logger

logger = get_logger(__name__)

async def make_request(session, url):
    async with session.get(url) as response:
        print('wtf')
        return await response


async def get_pdf(md5):
    logger.debug('Trying to connect to arachnysdocker...')
    # async with aiohttp.ClientSession() as session:
    #     url = f'http://0.0.0.0:5432/convert?auth=arachnys-weaver&url=http://0.0.0.0:8080/raw/{md5}/'
    #     print('Looks like it works')
    #     some_result = await make_request(session, url)
    #     return some_result
    return "That's your response"


async def get_raw_html(request):
    logger.debug('Got request to return html by its md5...')
    md5 = request.match_info.get('md5', None)

    html = request.app['htmls'][md5]
    if not html:
        logger.debug('There is no entry for your md5 key.')
        return web.Response(text='There is no data for this key', status=404)

    logger.debug('Returning queried html as a string...')
    return web.Response(text=html)


async def generate(request):
    logger.debug('Got request to generate pdf...')
    text = await request.text()

    logger.debug('Getting md5 from a given html...')
    md5 = hashlib.md5(text.encode('utf-8')).hexdigest()

    # store html by its md5
    logger.debug('Saving the html in app by its md5...')
    request.app['htmls'][md5] = text

    pdf = await get_pdf(md5)

    logger.debug('Returning pdf to the user...')
    return web.Response(body=pdf, content_type='application/pdf')


def main():
    logger.debug('Server initializing...')
    app = web.Application()
    app['htmls'] = {}
    app.router.add_get('/raw/{md5}', get_raw_html)
    app.router.add_post('/generate', generate)

    web.run_app(app)


if __name__ == '__main__':
    main()