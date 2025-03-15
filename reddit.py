import asyncio
import datetime
import json
from threading import Lock
from utils import *
from commentUtils import *
import pandas as pd
from  patchright.async_api import async_playwright,Page
import random

PATTERNS = ["https://www.reddit.com/r/"]
globalCommunityLinks=[]
globalLinks =[]
globalCommentNum =0
actualGlobalCommentNum = 0
finished_df = pd.DataFrame()
data_lock = Lock()
globalLinkLock =Lock()
globalCommentNumLock = Lock()
actualglobalCommentNumLock = Lock()
thread_data = []
thread_data_lock =Lock()
community_thread_title_url ={}
community_thread_title_url_lock = Lock()


async def CommunityLinkScrapper(search:str,max_scrolls=3):
    """
    This function, given the search parameter(variable), will scrape community urls given the search
    """
    search = search.title()
    search = search.strip()
    search = search.replace(" ","+")
    global globalCommunityLinks

    async with async_playwright() as p:
        browser =  await p.chromium.launch(
                channel="chrome",                   
                headless=False
            
            )
        page = await browser.new_page()
        
        scroll_pause_time=2
        await page.set_viewport_size({"width": 1280,"height": 720})
        page.set_default_timeout(31536000)
        await page.goto(f"https://www.reddit.com/search/?q={search}&type=communities")
        await asyncio.sleep(1)
        previous_height = await page.evaluate("document.body.scrollHeight")
        scroll_count = 0

        while scroll_count < max_scrolls:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            links = await page.query_selector_all('a[class="absolute inset-0"]')
            hrefs = [await link.get_attribute("href") for link in links if await link.get_attribute("href") ]
            
            for href in hrefs:
                if href not in globalCommunityLinks:
                    
                    globalCommunityLinks.append(href)
            await asyncio.sleep(scroll_pause_time)
            new_height = await page.evaluate("document.body.scrollHeight")

            if new_height == previous_height:
                break

            previous_height = new_height
            scroll_count += 1
            

        if scroll_count >= max_scrolls:
            print("Reached maximum scroll limit.")
            
        await asyncio.sleep(3)
        
        
        print(globalCommunityLinks)
        print(len(globalCommunityLinks))
        await browser.close()


def communityArticleLinksConfig(num_scrapers=3,globalCommunityLinksLimit=2,max_scrolls=1):
    """
    This function configures everything to do with scrolling , scraping  and limiting how many community article urls are taken given on the search parameter(variable) and the subsequent articles within those communities 
    """
    global globalCommunityLinks
    if globalCommunityLinksLimit >= len(globalCommunityLinks):
        print(f"Community Links Found: {len(globalCommunityLinks)}")
        
    else:
        globalCommunityLinks = globalCommunityLinks[:globalCommunityLinksLimit]
        print(f"Community Links Found: {len(globalCommunityLinks)}")
    
      
    num_links = len(globalCommunityLinks)
    print("Community Links:")
    print(globalCommunityLinks)
    print("-"*100)
    links_per_scraper = num_links // num_scrapers  
    globalCommunityUrls = []
    for i in range(num_scrapers):
        # For the last scraper, take all remaining links to cover any remainder
        if i == num_scrapers - 1:
            slice_links = globalCommunityLinks[i * links_per_scraper:]
        else:
            slice_links = globalCommunityLinks[i * links_per_scraper: (i + 1) * links_per_scraper]
        globalCommunityUrls.append((slice_links,max_scrolls))
    linkTasks = [asyncio.create_task(articleLinkScraper(*arg)) for arg in globalCommunityUrls]
    return linkTasks
    

async def articleLinkScraper(urls,max_scrolls=1,filters="top/?t=all"):
    """
    The article link scraper, will collect all urls given the community and the number of scrolls defined
    """
    global globalLinks
    async with async_playwright() as p:
        browser =  await p.chromium.launch(
                channel="chrome",                   
                headless=False
            
            )
        page = await browser.new_page()
        max_scrolls=max_scrolls
        scroll_pause_time=2
        await page.set_viewport_size({"width": 1280,"height": 720})
        page.set_default_timeout(31536000)
        for url in urls:
            await page.goto("https://www.reddit.com"+url+filters)
            await asyncio.sleep(1)
            previous_height = await page.evaluate("document.body.scrollHeight")
            scroll_count = 0

            while scroll_count < max_scrolls:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                links = await page.query_selector_all('a[slot="full-post-link"]')
                hrefs = [await link.get_attribute("href") for link in links if await link.get_attribute("href") ]
                
                for href in hrefs:
                    if href not in globalLinks:
                        
                        with globalLinkLock:
                            globalLinks.append(href)
                await asyncio.sleep(scroll_pause_time)
                new_height = await page.evaluate("document.body.scrollHeight")

                if new_height == previous_height:
                    break

                previous_height = new_height
                scroll_count += 1
                

            if scroll_count >= max_scrolls:
                print("Reached maximum scroll limit.")
                
            await asyncio.sleep(3)
            
            
            print(globalLinks)
            print(len(globalLinks))
        await browser.close()


async def redScraper(now=datetime.datetime.now()):
    """
    This is the actual reddit scraper(redScraper), and will take all the links/urls within the globalLinks variable, and will scrape the comments until the variable is empty
    """
    global globalLinks
    async with async_playwright() as p:
        global globalCommentNum
        global actualGlobalCommentNum
        browser =  await p.chromium.launch(
                channel="chrome",                   
                headless=False
            )
        
        scrapedUrls = []
        
       
        page = await browser.new_page()
        await page.set_viewport_size({"width": 900,"height": 600})

        page.set_default_timeout(31536000)
        print(f"articles to scrape - {len(globalLinks)}")
        while len(globalLinks) >=1:
            with globalLinkLock:
                url =globalLinks[0]
                globalLinks.remove(url)
            url = "https://www.reddit.com"+url
            await page.goto(url)
            title = await page.locator('h1[slot="title"]').inner_text()
            community = await page.locator('span[class="flex flex-none subreddit-name neutral-content font-bold text-12 whitespace-nowrap"]').inner_text()
            commentNum = await page.locator("div.shreddit-post-container.flex.gap-sm.flex-row.items-center.flex-nowrap.justify-start.h-2xl.mt-md.px-md.xs\:px-0 > button > span > span:nth-child(2)").inner_text()
            try : 
                commentNum = int(commentNum)
            except:
                commentNum = 0
            print(f"Reported Comments: {commentNum}")
            with globalCommentNumLock:
                globalCommentNum +=commentNum
                
            
            
            await smooth_scroll_to_end(page=page)
            await asyncio.sleep(6)
            await scroll_to_end(page=page)
            await page.wait_for_load_state("load",timeout=60000)
            
            #Paginate Comments
            while  await page.get_by_text("View more comments").first.is_visible():
                await scroll_to_end(page=page)
                # Query all buttons within the container

                await process_buttons(page)
                await asyncio.sleep(0.5)
                await scroll_to_end(page=page)
                
                try: 
                    await page.get_by_text("View more comments").first.click(timeout=1500)

                except:
                    pass
                await asyncio.sleep(random.uniform(2.5,5.7))
                
                # Get all comment elements on the page
            
            #Click More reply comments
            await process_buttons(page)
            #Click Archived Comments
            await process_archived_comments(page)
            #Click More reply comments again(For the Last time)
            await process_buttons(page)

            

            data = await process_comments(page)

            
            thread_comments = {
                "title":title,
                "community":community,
                "url":url,
                "comments":data
            }
            comments_scraped = len(thread_comments["comments"])
            thread_comments["comments"] = nest_comments(thread_comments["comments"])
            #Creating a index of Communities-Thread Titles and urls
            with community_thread_title_url_lock:
                if community not in community_thread_title_url:
                    community_thread_title_url[community] = [{"title":title,"url":url,"num_of_comments":comments_scraped}]

                else:
                    community_thread_title_url[community].append({"title": title, "url": url,"num_of_comments":comments_scraped})
                
            with thread_data_lock:
                thread_data.append(thread_comments)
            
            
            with actualglobalCommentNumLock:
                actualGlobalCommentNum += comments_scraped
            
            scrapedUrls.append(url)
            
            
            if commentNum>0:
                disparity = round(((commentNum-comments_scraped)/commentNum)*100,2)
                print(f"Comments Actually Scraped(All): {comments_scraped} , Reported: {commentNum}. Disparity:{disparity}, Top Level Comments: {len(thread_comments['comments'])} ")
            #print(thread_comments)
            print(community_thread_title_url)
            print(comments_scraped)
            with globalLinkLock:
                print(f"links left :{len(globalLinks)}")
            
        finshedTime = datetime.datetime.now()
        print(finshedTime-now)
        
        
        await browser.close()
    
    
        
    
async def main():
    global actualGlobalCommentNum
    global globalLinks

    #The first links have the most comments/ were the first to be scraped.
    globalLinks.reverse()

    #Search Reddit Communities Based on Text
    search = "Science"

    #How many articles would you like to Scrape?
    article_limit = 3
    #How many browser instances(redScrapers) would you like to instantiate ?
    num_of_scrapers =1

    #Scrapes all communities based on key words and max_scrolls
    await asyncio.gather(asyncio.create_task(CommunityLinkScrapper(search,max_scrolls=1)))

    #Scrapes Reddit Community Posts/Articles
    await asyncio.gather(*communityArticleLinksConfig(num_scrapers=1,max_scrolls=3,globalCommunityLinksLimit=1))

    #Scrape Reddit Community-Article Comments    
    globalLinks = globalLinks[:article_limit]
    now = datetime.datetime.now()
    tasks = [ redScraper(now=now) for _ in range(0,num_of_scrapers)]
    await asyncio.gather(*tasks)
    print(actualGlobalCommentNum)

    #Community name - Article name - Comments in json
    with open("threads.json", "w") as file:
        json.dump(thread_data, file, indent=4)
    #Community name - Article name - Comments num in json(index)
    with open("index.json", "w") as file:
        json.dump(community_thread_title_url, file, indent=4)
        
        
        
        
if __name__ == "__main__":
    asyncio.run(main())
   