# -*- coding: utf-8 -*- 

import aiohttp
import asyncio
import aiofiles


async def get_md5(session, url):
    async with session.get(url) as response:
        return await response.text()


async def convert_html_to_pdf(session, url, data):
    async with session.post(url, data=data) as response:
        print(response.status)
        if response.status == 200:
            async with aiofiles.open('file.pdf', 'wb') as file:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    await file.write(chunk)
        return await response.release()


async def main():
    async with aiohttp.ClientSession() as session:

        url = 'http://docs.aiohttp.org/en/stable/client_advanced.html'
        async with session.get(url) as response:
            if response.status == 200:
                file = await response.read()
                # headers = {'content-type': 'application/html'}
                await convert_html_to_pdf(session, 'http://localhost:8181/generate', data=file)
            else:
                print(f'Server returned {response.status} status code')


        # test that server can return html by md5 key
        # response = await get_md5(session, 'http://localhost:8181/raw/44c8ce76fb92401953f0b122182929ab')


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
