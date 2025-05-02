from nitterharvest.profileScrapper import profile_tweets

tweets = profile_tweets(username='elonmuskADO', limit=10, driver_limit=3, comment_limit=10)

print(tweets)