# -*- coding: utf-8 -*-

"""
Not a real test file for some test framework, just a simple aiohttp client to check main application with.
"""

import aiohttp
import asyncio
import aiofiles #type: ignore
import sys
import os
from aiohttp.client import ClientSession

# Perhaps there is a better way to import a script from another directory
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'html_converter'))

from set_up_logging import get_logger

logger = get_logger(__name__)

async def convert_html_to_pdf(session: ClientSession, url: str, data: bytes) -> None:
    """
    Tests ability of server to serve its main and sole purpose: receive an html file and return
    its pdf version back

    :param session: session object of aiohttp
    :param url: address of the server which is being tested
    :param data: an html file as bytes
    :return: None
    """

    async with session.post(url, data=data) as response:
        logger.debug(f'status code: {response.status}')
        if response.status == 200:
            async with aiofiles.open('file.pdf', 'wb') as file:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    await file.write(chunk)
        else:
            print(await response.text())

async def main() -> None:
    """
    Function that performs some test tasks for __main__.py
    :return: None
    """

    async with aiohttp.ClientSession() as session:
        # url = 'http://docs.aiohttp.org/en/stable/client_advanced.html'
        url = 'https://www.ferra.ru/'
        async with session.get(url) as response:
            if response.status == 200:
                file = await response.read()
                await convert_html_to_pdf(session, 'http://localhost:8181/generate', data=file)
            else:
                print(f'Server returned {response.status} status code')

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
