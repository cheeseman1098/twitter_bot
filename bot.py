#%%
import tweepy
import webbrowser
import time 
import re
import json
import pandas as pd
# %%
CONSUMER_KEY = "dTaeqdz0o0hUJMQor85t8Uv3J"
CONSUMER_SECRET = "6cxeZfGMxpZ0IIfrrUe17tMxJBtWzFOHFqKWAChIIk3WwLbx3t"
ACCESS_TOKEN = "1381993715879804932-g5gAk5EC5nkIpF2HkrFkISqSkwrhvl"
ACCESS_TOKEN_SECRET = "c1BpKABw5Pxrw86d5CeitNs6TMLldtOdY5DVAlF6njJvx"
callback_uri = "oob" 

#set up OAuth for Twitter API
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
#rename for easy use
api = tweepy.API(auth)
#%%
def get_trigger_words():
    '''returns list of words to be avoided loaded from trigger_words.txt'''
    trigger_words = list() #list of words to filter from tweets
    trigger_handle = open("trigger_words.txt")
    for word in trigger_handle: #loads filter words from trigger_words.txt
        word = word.rstrip().lower()
        trigger_words.append(word)
    return trigger_words
#%%
def get_last_seen(): 
    '''returns value stored in last_seen_id.txt'''
    fhand = open("last_seen_id.txt")
    return fhand.read()
#%%
def update_last_seen(tweet):
    f = open("last_seen_id.txt")
    last_id = int(f.read())
    f.close()
    if last_id >= tweet.id: return
    fhand = open("last_seen_id.txt","w")
    fhand.write(str(tweet.id))
    fhand.close()
#%%
def tweet_ok(in_tweet): 
    '''returns False if tweet contains a trigger word, True otherwise'''
    text = in_tweet.text.lower()
    for trigger in trigger_words:
        if not text.lower().find(trigger) == -1:
            return False
    return True
#%%
def get_new_tweets(): #search for new tweets with set parameters
    print("Fetching new tweets...")
    return api.search(q='"hoop earrings" -filter:retweets filter:safe', result_type="recent", lang="en", since_id=get_last_seen(), count=90)
#%%
def fav_tweets():
    for tweet in get_new_tweets():
        update_last_seen(tweet)
        if tweet_ok(tweet) == False: continue
        api.create_favorite(tweet.id)
# %%
limits_raw = api.rate_limit_status()
limits_formatted = json.dumps(limits_raw, indent=2)
print(limits_formatted)
#%%
print("Starting bot...")
while True:
    fav_tweets()
    print("Sleeping... zzz...")
    time.sleep(60)
# %%
test_tweet = api.search(q='"new earrings"', count=1, lang='en')
raw_tweet = json.loads(test_tweet)
test_tweet_formatted = json.dumps(raw_tweet, indent=2)
print(test_tweet_formatted)
# %%
for tweet in test_tweet:
    print(tweet.user.screen_name)
liked_tweets = []
#%%
test_tweets = api.search(q="kanye", count=2)
data = list()
for tweet in test_tweets:
    new_tweet = dict()
    new_tweet["tweet_id"] = tweet.id
    new_tweet["user_id"] = tweet.user.id
    new_tweet["user_name"] = tweet.user.screen_name
    new_tweet["user_location"] = tweet.user.location
    new_tweet["user_verified"] = tweet.user.verified
    new_tweet["user_followers"] = tweet.user.followers_count
    new_tweet["user_following"] = tweet.user.friends_count
    new_tweet["retweets"] = tweet.retweet_count
    #new_tweet["replies"] = tweet.reply_count
    new_tweet["favorites"] = tweet.favorite_count
    new_tweet["liked"] = False
    data.append(new_tweet)
#%%
record = pd.DataFrame(data)
#%%
record = record.append(data)
#%%
record.to_csv("tweet_records.csv")