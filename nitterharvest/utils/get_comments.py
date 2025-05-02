from .webdriver import start_webdriver
import asyncio
from bs4 import BeautifulSoup
from .html_element import HTML
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor

TWITTER_IMG_DOMAIN = "https://pbs.twimg.com"

html = HTML()

async def get_comments(list: list, driver_limit: int, comment_limit: int) -> list:
    """
    Get comments from all tweets using concurrent drivers.
    """
    if driver_limit > len(list):  # If there are more drivers than tweets, set driver_limit to the number of tweets
        driver_limit = len(list)

    # Create a thread pool executor
    with ThreadPoolExecutor(max_workers=driver_limit) as executor:
        # Start drivers in threads
        drivers = await asyncio.gather(
            *[asyncio.to_thread(start_webdriver) for _ in range(driver_limit)]
        )

        # Split the tweets into groups for each driver
        task_groups = split_evenly(list, driver_limit)

        # Process tweets concurrently using threads
        tweet_groups_with_comments = await asyncio.gather(
            *[
                asyncio.to_thread(
                    worker, task_groups[i], drivers[i], comment_limit
                )
                for i in range(driver_limit)
            ]
        )

    # Recombine the results into a single list
    tweets_with_comments = recombine_parts(tweet_groups_with_comments)
    return tweets_with_comments
    
def worker(tweets, driver, comment_limit: int) -> list:
    """
    Worker function to get comments for a list of tweets using a single driver.
    """
    print(f"=== Processing {len(tweets)} tweets comments with driver {driver} ===")
    
    results = []
    for tweet in tweets:
        driver.get(tweet['tweet_link'])
        tweet['comments'] = []
        
        try:
            while len(tweet['comments']) < comment_limit:  # Fixed this line
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, html.tweet_container))
                )

                soup = BeautifulSoup(driver.page_source, 'lxml')
                comments = extract_comments(soup)
                tweet['comments'].extend(comments)
                                
                if len(tweet['comments']) >= comment_limit:
                    tweet['comments'] = tweet['comments'][:comment_limit]
                    break
                try:
                    load_more_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, html.load_more_button))
                    )
                    driver.execute_script("arguments[0].click();", load_more_button)
                except:
                    break
                
            results.append(tweet)
            
        except Exception as e:
            print(f"Error processing tweet: {e}")
    driver.quit()  # Close the driver after processing the tweets
    return results
    
def extract_comments(soup):
    """
    Extract comments from the soup object.
    """
    comments = [
        {
            "content": comment.select_one(html.tweet_text).text.strip() if comment.select_one(html.tweet_text) else "",
            "date": comment.select_one(html.tweet_time).text.strip() if comment.select_one(html.tweet_time) else "",
            "author": {
                "avatar": convert_nitter_image_to_twitter(comment.select_one(html.author_avatar)["src"]) if comment.select_one(html.author_avatar) else "",
                "fullname": comment.select_one(html.author_fullname).text.strip() if comment.select_one(html.author_fullname) else "",
                "username": comment.select_one(html.author_username).text.strip() if comment.select_one(html.author_username) else ""
            },
        } for comment in soup.select(html.comment_container)
    ]
    return comments

async def async_wrapper(func):
    return func()

def split_evenly(items: list, num_parts: int) -> list[list]:
    """
    Split a tweets equally amongst the drivers.
    """
    
    # Calculate the base size and remainder
    base_size = len(items) // num_parts
    remainder = len(items) % num_parts
    
    result = []
    start = 0
    
    for i in range(num_parts):
        # The first 'remainder' parts get an extra item
        part_size = base_size + (1 if i < remainder else 0)
        end = start + part_size
        result.append(items[start:end])
        start = end
    
    return result

def recombine_parts(parts: list) ->list:
    """
    Recombine a list of sublists back into a single list in the original order.
    """
    return [item for sublist in parts for item in sublist]

def convert_nitter_image_to_twitter(nitter_url: str) -> str:
        """Convert Nitter image URLs to Twitter image URLs."""
        if not nitter_url:
            return ""
        if "/pic/" in nitter_url:
            decoded_url = unquote(nitter_url)
            return decoded_url.replace("/pic/", f"{TWITTER_IMG_DOMAIN}/")
        return nitter_url