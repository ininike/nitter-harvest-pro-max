from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from .utils.webdriver import start_webdriver
from .utils.html_element import HTML
from .utils.get_comments import get_comments, convert_nitter_image_to_twitter
import asyncio

html = HTML()

DOMAIN = "https://nitter.net"
TWITTER_IMG_DOMAIN = "https://pbs.twimg.com"

def profile_tweets(username: str, limit: int = 100, driver_limit: int = 10, comment_limit: int = 20) -> list:
    """
    Scrape tweets from a user's profile on nitter.poast.org.

    This function uses Selenium WebDriver to navigate to a user's profile page on nitter.poast.org
    and scrape their tweets. It continuously loads more tweets until it reaches the specified limit
    or there are no more tweets to load.

    Args:
        username (str): The Twitter username of the profile to scrape (without the @ symbol).
        limit (int, optional): The maximum number of tweets to scrape. Defaults to 100.

    Returns:
        list[dict]: A list of dictionaries, each containing information about a single tweet.
                    Each dictionary has the following keys:
                    - 'time': The timestamp of the tweet (str)
                    - 'tweet': The text content of the tweet (str)

    Raises:
        Exception: If an error occurs during the scraping process. The error message is printed.

    Note:
        - This function requires a working internet connection.
        - The scraping process may take some time depending on the number of tweets requested.
        - The function uses Selenium WebDriver, which must be properly set up in the environment.
        - The HTML class from .utils.html_element is used for locating elements on the page.
    """
    
    driver = start_webdriver()
    driver.get(f'{DOMAIN}/{username}')
    print(f"=== Redirecting to {username}'s tweets profile ===")
    
    results = {
        "tweets": [],
    }
    
    try:
        while len(results['tweets']) < limit:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, html.tweet_container))
            )
            
            soup = BeautifulSoup(driver.page_source, 'lxml')
            
            if not results.get("profile_data"):
                # Extract profile data only once
                results["profile_data"] = {
                    "full_name": soup.select_one(html.profile_full_name).text.strip() 
                                  if soup.select_one(html.profile_full_name) else "",
                    "username": soup.select_one(html.profile_username).text.strip().replace("@", "")
                                if soup.select_one(html.profile_username) else "",
                    "bio": soup.select_one(html.profile_bio).text.strip() 
                           if soup.select_one(html.profile_bio) else "",
                    "location": soup.select_one(html.profile_location).text.strip() 
                                if soup.select_one(html.profile_location) else "",
                    "join_date": soup.select_one(html.profile_join_date).text.strip().replace("Joined", "").strip() 
                                 if soup.select_one(html.profile_join_date) else "",
                    "tweets": stat_cleaner(
                                soup.select_one(html.profile_tweets).text.strip() 
                              ) if soup.select_one(html.profile_tweets) else "0",
                    "following": stat_cleaner(
                                   soup.select_one(html.profile_following).text.strip() 
                                 ) if soup.select_one(html.profile_following) else "0",
                    "followers": stat_cleaner(
                                   soup.select_one(html.profile_followers).text.strip() 
                                 ) if soup.select_one(html.profile_followers) else "0",
                    "likes": stat_cleaner(
                               soup.select_one(html.profile_likes).text.strip() 
                             ) if soup.select_one(html.profile_likes) else "0",
                    "profile_image": convert_nitter_image_to_twitter(
                                       soup.select_one(html.profile_image)["src"]
                                     ).replace(f"/pic/pbs.twimg.com/", f"{TWITTER_IMG_DOMAIN}/") 
                                     if soup.select_one(html.profile_image) else "",
                    "banner_image": convert_nitter_image_to_twitter(
                                      soup.select_one(html.profile_banner_image)["src"]
                                    ).replace(f"/pic/", "") 
                                    if soup.select_one(html.profile_banner_image) else ""
                }
                
            new_tweets = []
            
            # Process tweets
            for tweet in soup.find_all('div', class_=html.tweet_container):
                # Extract tweet details
                tweet_images = [convert_nitter_image_to_twitter(img["src"]) for img in tweet.select(html.images)]
                
                # Get the tweet link as a unique identifier
                tweet_link_element = tweet.select_one(".tweet-link")
                if not tweet_link_element:
                    continue

                tweet_link = DOMAIN + tweet_link_element["href"]

                # Extract tweet metadata
                retweeted_by = tweet.select_one(html.retweeted_by)
                replying_to = tweet.select_one(html.replying_to)

                # Extract author information
                author_avatar = tweet.select_one(html.author_avatar)
                author_fullname = tweet.select_one(html.author_fullname)
                author_username = tweet.select_one(html.author_username)

                # Build tweet data object
                tweet_data = {
                    "content": tweet.select_one(html.tweet_text).text.strip() if tweet.select_one(html.tweet_text) else "",
                    "date": tweet.select_one(html.tweet_time).text.strip() if tweet.select_one(html.tweet_time) else "",
                    "likes": stat_cleaner(
                        tweet.select_one(html.likes).parent.text.strip() if tweet.select_one(html.likes) else "0"
                    ),
                    "comments": stat_cleaner(
                        tweet.select_one(html.comments).parent.text.strip() if tweet.select_one(html.comments) else "0"
                    ),
                    "retweets": stat_cleaner(
                        tweet.select_one(html.retweets).parent.text.strip() if tweet.select_one(html.retweets) else "0"
                    ),
                    "tweet_link": tweet_link,
                    "images": tweet_images,
                    "retweeted_by": retweeted_by.text.strip() if retweeted_by else None,
                    "is_retweet": bool(retweeted_by),
                    "is_reply": bool(replying_to),
                    "replying_to": replying_to.text.strip() if replying_to else None,
                    "author": {
                        "avatar": convert_nitter_image_to_twitter(author_avatar["src"]) if author_avatar else "",
                        "fullname": author_fullname.text.strip() if author_fullname else "",
                        "username": author_username.text.strip() if author_username else ""
                    }
                }
                
                new_tweets.append(tweet_data)
            
            results['tweets'].extend(new_tweets)
            
            if len(results['tweets']) >= limit:
                results['tweets'] = results['tweets'][:limit]
                break
            
            try:
                load_more_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, html.load_more_button))
                )
                driver.execute_script("arguments[0].click();", load_more_button)
            except:
                break
            
            print(f"Tweets scraped: {len(results['tweets'])}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        driver.quit()
    
    print("=== Done! ===")
    print(f"Successfully scraped {len(results['tweets'])} tweets")
    
    print("=== Fetching Comments ===")
    results['tweets'] = asyncio.run(get_comments(results['tweets'], driver_limit= driver_limit, comment_limit=comment_limit))
    print("=== Done! ===")
    
    return results

def stat_cleaner(stat: str):
        return stat.replace(",", "")