"""Web entry point for pygbag (https://pygame-web.github.io): EchoSketch in the browser.

Build with:  python3 tools/build_web.py     (writes build/web/)
The desktop game still starts with `python3 -m echosketch`; nothing here changes it.
"""
import asyncio

import pygame  # noqa: F401  (must be imported here so pygbag loads pygame)

from echosketch.main import App


async def main():
    await App().run_web()


asyncio.run(main())
