# -*- coding: utf-8 -*- 

import aiohttp
import asyncio


async def fetch(session, url):
	payload = '<h1>I am your HTML<h1>'
	async with session.post(url, data=payload) as response:

		return await response.text()


async def main():
	async with aiohttp.ClientSession() as session:
		html = await fetch(session, 'http://localhost:8080/generate')
		print(html)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
