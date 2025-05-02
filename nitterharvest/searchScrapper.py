from .utils.webdriver import start_webdriver
from .utils.html_element import HTML
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from .utils.get_comments import convert_nitter_image_to_twitter
from bs4 import BeautifulSoup

html = HTML()

TWITTER_IMG_DOMAIN = "https://pbs.twimg.com"

def search_users(query: str, limit: int = 100) -> list:
    """
    Scrape users based on a search query from nitter.poast.org.

    This function uses Selenium WebDriver to navigate to nitter.poast.org's search page,
    enter a search query, and scrape the resulting users. It continuously loads more users
    until it reaches the specified limit or there are no more users to load.

    Args:
        query (str): The search query (hashtag, topic, or general search term).
        limit (int, optional): The maximum number of users to scrape. Defaults to 100.

    Returns:
        list[dict]: A list of dictionaries, each containing information about a single tweet.
                    Each dictionary has the following keys:
                    - 'time': The timestamp of the tweet (str)
                    - 'tweet': The text content of the tweet (str)
                    - 'username': The username of the tweet author (str)

    Raises:
        Exception: If an error occurs during the scraping process. The error message is printed.

    Note:
        - This function requires a working internet connection.
        - The scraping process may take some time depending on the number of users requested.
        - The function uses Selenium WebDriver, which must be properly set up in the environment.
        - The HTML class from .utils.html_element is used for locating elements on the page.
    """
    
    driver = start_webdriver() 
    driver.get(f"https://nitter.net/search?f=users&q={query}") 
    print(f"=== searching... {query} ===")
    
    users_corpus = []
    try:
        
        while True:
            load_more_button = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, html.load_more_button))) 
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Track usernames to avoid duplicates
            processed_usernames = set()
                        
            # Process each user result
            for user in soup.select(".timeline-item"):
                # Skip "show more" items and users without avatars
                if "show-more" in user.get("class", []):
                    continue

                avatar_img = user.select_one(".profile-result .tweet-avatar img")
                if not avatar_img:
                    continue

                # Get username for deduplication
                username_element = user.select_one(".username")
                if not username_element:
                    continue

                username = username_element.text.strip().replace("@", "")

                # Skip if we've already processed this user
                if username in processed_usernames:
                    continue
                processed_usernames.add(username)

                # Extract user data
                user_data = {
                    "profile_image_url": convert_nitter_image_to_twitter(avatar_img["src"]),
                    "full_name": user.select_one(".fullname").text.strip() if user.select_one(".fullname") else "",
                    "username": username,
                    "bio": user.select_one(".tweet-content").text.strip() if user.select_one(
                        ".tweet-content") else "",
                } 
                users_corpus.append(user_data)
                
            load_more_button.click()
            print(f"users scraped: {len(users_corpus)}")
            
            if len(users_corpus) >= limit:
                print("=== done! ===")
                
                print(f"success scrapping {len(users_corpus)} users")
                break
    
    except Exception as _:
        print("Finished loading all content or an error occurred:", str(_))
        
    
    return users_corpus