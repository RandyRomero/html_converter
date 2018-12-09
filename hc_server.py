# -*- coding: utf-8 -*- 

import asyncio
from aiohttp import web
import aiotask_context as context
import hashlib


async def get_raw_html(request):
	md5 = request.match_info.get('md5', None)

	html = context.get(md5, None)
	if not html:
		return web.Response(text='There is no data for this key', status=404)

	return web.Response(text=html)


async def generate(request):
	text = await request.text()
	md5 = hashlib.md5(text.encode('utf-8')).hexdigest()
	context.set(md5, text)
	return web.Response(text=text)


def main():
	loop = asyncio.get_event_loop()
	loop.set_task_factory(context.task_factory)
	app = web.Application()
	app.router.add_get('/raw/{md5}', get_raw_html)
	app.router.add_post('/generate', generate)

	web.run_app(app)

if __name__ == '__main__':
	main()