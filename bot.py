#%%
import tweepy
import webbrowser
import time 
import re
import json
# %%
consumer_key = "dTaeqdz0o0hUJMQor85t8Uv3J"
consumer_secret = "6cxeZfGMxpZ0IIfrrUe17tMxJBtWzFOHFqKWAChIIk3WwLbx3t"
access_token = "1381993715879804932-g5gAk5EC5nkIpF2HkrFkISqSkwrhvl"
access_token_secret = "c1BpKABw5Pxrw86d5CeitNs6TMLldtOdY5DVAlF6njJvx"
callback_uri = "oob" 

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)
#%%
trigger_words = list() #list of words to filter from tweets
trigger_handle = open("trigger_words.txt")
for word in trigger_handle: #loads filter words from trigger_words.txt
    word = word.rstrip().lower()
    trigger_words.append(word)
#%%
def get_last_seen(): #returns value stored in last_seen_id.txt
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
def tweet_ok(in_tweet): #returns False if tweet contains a trigger word, True otherwise
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
