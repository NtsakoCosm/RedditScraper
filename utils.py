import asyncio
from  patchright.async_api import Page


async def smooth_scroll_to_end(page: Page, scroll_step: int = 100, delay: float = 0.1, pause: float = 2.0):
    # Get the initial page height
    previous_height = await page.evaluate("() => document.body.scrollHeight")
    while True:
        # Scroll down gradually in small steps
        for offset in range(0, previous_height, scroll_step):
            await page.evaluate(f"() => window.scrollTo(0, {offset})")
            await asyncio.sleep(delay)
        # Pause to allow new content to load
        await asyncio.sleep(pause)
        # Get the new page height after scrolling
        new_height = await page.evaluate("() => document.body.scrollHeight")
        # If the height hasn't changed, assume we've reached the bottom
        if new_height == previous_height:
            break
        previous_height = new_height

async def scroll_to_end(page:Page):
    # Get the initial page height
    previous_height = await page.evaluate("() => document.body.scrollHeight")
    while True:
        # Scroll down to the bottom of the page
        await page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
        2
        # Allow time for new content to load
        await asyncio.sleep(2)
        # Get the new page height after scrolling
        new_height = await  page.evaluate("() => document.body.scrollHeight")
        # If the height hasn't changed, assume we've reached the bottom
        if new_height == previous_height:
            break
        previous_height = new_height
