# -*- coding: utf-8 -*- 

import aiohttp
import asyncio


async def get_md5(session, url):
	async with session.get(url) as response:
		return await response.text()


async def send_html(session, url, payload):
	async with session.post(url, data=payload) as response:
		return await response.text()


async def main():
	async with aiohttp.ClientSession() as session:

		# test that server gets html
		payload	 = ['<h1>I am your HTML</h1>', '<p>There is some text</p>', '<a href="www.example.com">click</a>']
		for p in payload:
			html = await send_html(session, 'http://localhost:8080/generate', p)
			print(html)

		# test that server can return html by md5 key
		html_by_md5 = await get_md5(session, 'http://localhost:8080/raw/b9b876fed08883de8203d1076f8db0bd')
		print(html_by_md5)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
