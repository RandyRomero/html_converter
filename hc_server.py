# -*- coding: utf-8 -*- 

from aiohttp import web

async def generate(request):
	text = await request.text()
	return web.Response(text=text)


async def hello(request):
	name = request.match_info.get('name', 'Anonymous')
	text = "Hello, " + name
	return web.Response(text=text)


def main():
	app = web.Application()
	app.router.add_get('/hello/{name}', hello)
	app.router.add_post('/generate', generate)

	web.run_app(app)

if __name__ == '__main__':
	main()