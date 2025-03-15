import asyncio
import random
import re
from  patchright.async_api import Page

def nest_comments(comments):
    # Create a mapping from thingid to comment
    comment_by_id = {}
    for comment in comments:
        # Initialize each comment with an empty list for replies.
        comment['replies'] = []
        comment_by_id[comment['thingid']] = comment

    nested_comments = []
    for comment in comments:
        parent_id = comment['parentid']
        if parent_id is None:
            # Top-level comment
            nested_comments.append(comment)
        else:
            # Find the parent and add this comment to its 'replies'
            parent_comment = comment_by_id.get(parent_id)
            if parent_comment:
                parent_comment['replies'].append(comment)
            else:
                # If the parent is not found, it can be treated as top-level
                nested_comments.append(comment)
    return nested_comments

async def click_button(button, index):
    try:
        await button.evaluate("""
            node => {
                node.classList.remove('invisible');
                node.style.visibility = 'visible';
            }
        """)
        await button.evaluate("""
            node => {
                node.dispatchEvent(new MouseEvent('click', {
                    bubbles: true,
                    cancelable: true,
                    view: window
                }));
            }
        """)
        await asyncio.sleep(random.uniform(0.5, 1.5))
        # Optionally remove the button on successful click
        await button.evaluate("node => node.remove()")
    except Exception as e:
        print(f"Error clicking button {index}: {e}")
        # Remove the button to avoid infinite loop even on error
        try:
            await button.evaluate("node => node.remove()")
        except Exception as e_remove:
            print(f"Error removing button {index} after failure: {e_remove}")

async def process_buttons(page:Page):
    while len(await page.query_selector_all("div.inline-block.ml-px button")) > 0:
        

        buttons = await page.query_selector_all("div.inline-block.ml-px button")
        print(f"Found {len(buttons)} buttons.")
        batch_size = 20
        for start in range(0, len(buttons), batch_size):
            
            batch = buttons[start:start+batch_size]
            tasks = [click_button(button, i) for i, button in enumerate(batch, start=start)]
            
            # Execute all button clicks in the batch concurrently
            await asyncio.gather(*tasks)

            # Wait until network is relatively idle before starting the next batch
            await asyncio.sleep(random.uniform(0.5, 1.5))

async def click_archived_button(button, index):
    """Click an archived comment button with error handling."""
    try:
        await button.evaluate("""
            node => {
                node.classList.remove('invisible');
                node.style.visibility = 'visible';
            }
        """)
        await button.evaluate("""
            node => {
                node.dispatchEvent(new MouseEvent('click', {
                    bubbles: true,
                    cancelable: true,
                    view: window
                }));
            }
        """)
        await asyncio.sleep(random.uniform(0.5, 1.5))
        # Optionally remove the button on successful click
        await button.evaluate("node => node.remove()")
    except Exception as e:
        print(f"Error clicking button {index}: {e}")
        # Remove the button to avoid infinite loop even on error
        try:
            await button.evaluate("node => node.remove()")
        except Exception as e_remove:
            print(f"Error removing button {index} after failure: {e_remove}")

async def process_archived_comments(page):
    """Process clicking archived comment buttons in batches."""
    selector = "details > summary > div.flex.justify-center > button"

    while len(await page.query_selector_all(selector)) > 0:
        end_buttons = await page.query_selector_all(selector)

        batch_size = 20
        for start in range(0, len(end_buttons), batch_size):
            batch = end_buttons[start:start+batch_size]
            tasks = [click_archived_button(button, i) for i, button in enumerate(batch, start=start)]

            # Execute clicks concurrently within the batch
            await asyncio.gather(*tasks)

            # Wait for a random time before the next batch
            await asyncio.sleep(random.uniform(0.5, 1.5))

async def extract_comment_data(element):
    """Extract data from a single comment element."""
    author = await element.get_attribute("author")
    depth_str = await element.get_attribute("depth")
    depth = int(depth_str) if depth_str else 0
    score = await element.get_attribute("score")
    thingid = await element.get_attribute("thingid")
    parentid = await element.get_attribute("parentid")  # None for top-level comments

    # Extract the text content of the comment
    child = await element.query_selector("div[slot='comment']")
    comment_text = await child.inner_text() if child else ""

    # Use the entire element's text to search for a timestamp
    full_text = await element.inner_text()
    timestamp_match = re.search(r'\b(\d+[hd] ago)\b', full_text)
    timestamp = timestamp_match.group(1) if timestamp_match else ""

    return {
        "author": author,
        "depth": depth,         # 0 for top-level, 1+ for replies
        "thingid": thingid,
        "parentid": parentid,   # parent comment's ID (if any)
        "timestamp": timestamp,
        "comment": comment_text,
        "score": score,
    }

async def process_comments(page):
    """Process all comment elements concurrently using asyncio.gather."""
    comment_elements = await page.locator("shreddit-comment").element_handles()
    print(f"Found {len(comment_elements)} comments.")
    # Create a list of tasks for each comment extraction
    tasks = [extract_comment_data(element) for element in comment_elements]
    
    # Wait for all tasks to complete concurrently
    data = await asyncio.gather(*tasks)
    return data
