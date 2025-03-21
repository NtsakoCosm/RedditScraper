# Reddit Community Comment Scraper

This project is an asynchronous Reddit scraper that collects community URLs based on a search query, scrapes article links from those communities, and then gathers comments from each article. The final output is saved as two JSON files:
- **threads.json**: Contains details about each thread (title, community, URL, and nested comments).
- **index.json**: Maps communities to their threads along with the reported number of comments.

## Table of Contents
- [Features](#features)
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Usage](#usage)
- [Structure](#structure)

## Features
- **Community URL Scraping:** Searches Reddit communities based on a keyword.
- **Article Link Extraction:** Gathers article URLs from each community page.
- **Comment Scraping:** Visits each article and scrapes all available comments.
- **Asynchronous Execution:** Uses Python's `asyncio` along with Playwright's asynchronous API to manage multiple concurrent browser instances.
- **Thread-Safe Data Handling:** Uses threading locks to ensure safe updates to shared global variables.
- **JSON Output:** Saves scraped thread data and an index mapping communities to threads in JSON format.

## Dependencies
- Python 3.7+
- [asyncio](https://docs.python.org/3/library/asyncio.html)
- [datetime](https://docs.python.org/3/library/datetime.html)
- [json](https://docs.python.org/3/library/json.html)
- [pandas](https://pandas.pydata.org/)
- [threading](https://docs.python.org/3/library/threading.html)
- [Playwright](https://playwright.dev/python/docs/intro) (via `patchright.async_api` in this example)
- [random](https://docs.python.org/3/library/random.html)

## Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/NtsakoCosm/RedditScraper.git
   cd RedditScraper


## Usage

The script performs the following steps:

Community URL Scraping: Searches for communities matching a specific keyword (default is "Science") and collects community URLs.
Article Link Extraction: From the collected community URLs, it extracts article links.
Comment Scraping: Visits each article URL to scrape comments.
Output Generation: Saves the thread details and an index in threads.json and index.json, respectively.


## Structure

├── README.md
├── reddit.py           # Contains the main scraping code.
├── utils.py                 # Utility functions for scrolling and browser actions.
├── commentUtils.py          # Utility functions for processing comments.