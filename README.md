# nitter-harvest

A Python library for scraping data from Nitter.net, a Twitter mirror site. Uses Selenium and BeautifulSoup for efficient data extraction.

## Setup

1. Install Firefox and geckodriver. [Tutorial](https://www.youtube.com/watch?v=4NxqmX6F6po)
2. Clone this repository

## Usage

Create a new Python file or Jupyter notebook in the same directory as the `nitter-harvest` folder.

Or use the main.py file created already

### Profile Scraper

```python
from nitterharvest.profileScrapper import profile_tweets

tweets = profile_tweets(username='elonmuskADO', limit=10, driver_limit=3, comment_limit=10)
```

### Topic/Hashtag Scraper

```python
from nitterharvest.searchScrapper import search_tweets

query = "elonmusk"
tweets = search_tweets(query=query, limit=50)
```

Both functions return a list of dictionaries containing tweet data:
