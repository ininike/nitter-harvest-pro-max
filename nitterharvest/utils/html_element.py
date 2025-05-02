from dataclasses import dataclass


@dataclass(frozen=True)
class HTML:
    load_more_button:str = "//div[@class='show-more']"
    
    search_field:str = "//input[@name='q']"
    search_button:str = "//button[@type='submit']"
    
    tweet_container:str = "timeline-item"
    tweet_text:str = ".tweet-content"
    tweet_username:str = ".username"
    tweet_time:str = ".tweet-date"
    likes:str = ".icon-heart"
    comments:str = ".icon-comment"
    retweets:str = ".icon-retweet"
    tweet_link:str = ".tweet-link"
    images:str = ".attachment.image img"
    retweeted_by:str = ".retweet-header div"
    replying_to:str = ".tweet-body .replying-to a"
    author_avatar:str = ".tweet-avatar img"
    author_fullname:str = ".fullname"
    author_username:str = ".username"
    
    profile_full_name:str = ".profile-card-fullname"
    profile_username:str = ".profile-card-username"
    profile_bio:str = ".profile-bio p"
    profile_location:str = ".profile-location span:nth-of-type(2)"
    profile_join_date:str = ".profile-joindate span"
    profile_tweets:str = ".posts .profile-stat-num"
    profile_following:str = ".following .profile-stat-num"
    profile_followers:str = ".followers .profile-stat-num"
    profile_likes:str = ".likes .profile-stat-num"
    profile_image:str = ".profile-card-avatar img"
    profile_banner_image:str = ".profile-banner img"
    
    comment_container:str = ".reply"
    