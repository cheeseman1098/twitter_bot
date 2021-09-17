#%%
import tweepy
import time 
import json
import pandas as pd
# %%
CONSUMER_KEY = "dTaeqdz0o0hUJMQor85t8Uv3J"
CONSUMER_SECRET = "6cxeZfGMxpZ0IIfrrUe17tMxJBtWzFOHFqKWAChIIk3WwLbx3t"
ACCESS_TOKEN = "1381993715879804932-g5gAk5EC5nkIpF2HkrFkISqSkwrhvl"
ACCESS_TOKEN_SECRET = "c1BpKABw5Pxrw86d5CeitNs6TMLldtOdY5DVAlF6njJvx"
callback_uri = "oob" 

# list of queries to send to API when serching for new tweets
QUERIES = [
    "hoop earrings",
    "jewellery",
    "new earrings",
    "bead earrings"
    ]

# set up OAuth for Twitter API
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
# rename for ease of use
api = tweepy.API(auth)
#%%
def get_trigger_words() -> list:
    '''returns list of words to be avoided loaded from trigger_words.txt'''
    trigger_words = list() #list of words to filter from tweets
    trigger_handle = open("trigger_words.txt")
    for word in trigger_handle: #loads filter words from trigger_words.txt
        word = word.rstrip().lower()
        trigger_words.append(word)
    return trigger_words
#%%
def get_last_seen() -> str: 
    '''returns value stored in last_seen_id.txt'''
    fhand = open("last_seen_id.txt")
    return fhand.read()
#%%
def update_last_seen(tweet: int) -> None:
    '''saves the input tweet's ID on to file last_seen_id.txt'''
    f = open("last_seen_id.txt")
    last_id = int(f.read())
    f.close()
    if last_id >= tweet: return
    fhand = open("last_seen_id.txt","w")
    fhand.write(str(tweet))
    fhand.close()
#%%
def filter_tweets(tweets: list) -> list:
    '''filters out a list of tweets containing trigger words and returns the clean list'''
    print("Filtering tweets...")
    for count, tweet in enumerate(tweets):
        if tweet_ok(tweet) == False: tweets.pop(count)
    return tweets
#%%
def tweet_ok(in_tweet: tweepy.Status) -> bool: 
    '''returns False if tweet contains a trigger word, True otherwise'''
    text = in_tweet.text.lower()
    bio = in_tweet.user.description.lower()
    for trigger in get_trigger_words():
        if not text.lower().find(trigger) == -1:
            return False
        if not bio.lower().find(trigger) == -1:
            return False
    return True
#%%
def get_new_tweets(query: str, num_results=90) -> tweepy.SearchResults: 
    '''searches for new tweets with set parameters and returns a list of tweet objects'''
    print("Fetching new tweets...")
    search_query = '"{}" -filter:retweets filter:safe'.format(query)
    return api.search(q=search_query, result_type="recent", lang="en", since_id=get_last_seen(), count=num_results)
#%%
def clean_data(tweet_data: dict) -> dict:
    '''performs various checks on data and returns clean dict'''
    print("Cleaning retrieved tweets...")
    # getting rid of duplicates
    seen_tweets = [] # list to track what ID's have appeared already 
    for count, tweet_id in enumerate(tweet_data["tweet_id"]):
        if tweet_id in seen_tweets:
            print("Found duplicate. Removing...")
            for key in tweet_data:
                tweet_data[key].pop(count)
            continue
        seen_tweets.append(tweet_id)
    
    # checking for empty data 
    if len(tweet_data["tweet_id"]) == 0:
        print("No new tweets were found.")
    
    print("Finished cleaning tweets.")
    
    return tweet_data
#%%
def main() -> None:
    # get current time and date 
    td = time.gmtime(time.time())
    
    tweet_id = []
    user_id = []
    user_name = []
    user_location = []
    user_verified = []
    user_followers = []
    user_following = []
    retweets = []
    favorites = []
    liked = []
    fetched_at = []
    from_query = []
    
    for query in QUERIES:
        
        new_tweets = get_new_tweets(query)
        new_filtered_tweets = filter_tweets(new_tweets)
        
        for tweet in new_filtered_tweets:
            tweet_id.append(tweet.id)
            user_id.append(tweet.user.id)
            user_name.append(tweet.user.screen_name)
            user_location.append(tweet.user.location)
            user_verified.append(tweet.user.verified)
            user_followers.append(tweet.user.followers_count)
            user_following.append(tweet.user.friends_count)
            retweets.append(tweet.retweet_count)
            favorites.append(tweet.favorite_count)
            liked.append(False)
            fetched_at.append("{d}/{m}/{y}".format(d=td[2], m=td[1], y=td[0]))
            from_query.append(query)
    
    new_filtered_tweets_dict = {
        "user_id": user_id,
        "tweet_id": tweet_id,
        "user_name": user_name,
        "user_location": user_location,
        "user_verified": user_verified,
        "user_followers": user_followers,
        "user_following": user_following,
        "retweets": retweets,
        "favorites": favorites,
        "liked": liked,
        "fetched_at": fetched_at,
        "from_query": from_query
        }
    
    # check retrieved data is clean 
    new_filtered_tweets_dict = clean_data(new_filtered_tweets_dict)

    # like tweets
    for i in range(len(new_filtered_tweets_dict["liked"])):
        tweet = new_filtered_tweets_dict["tweet_id"][i]
        update_last_seen(tweet)
        if new_filtered_tweets_dict["liked"][i] == False:
            try:
                print("Liking tweet {}".format(tweet))
                api.create_favorite(tweet)
                new_filtered_tweets_dict["liked"][i] = True
            except tweepy.TweepError:
                print("Tweet already liked.")
                new_filtered_tweets_dict["liked"][i] = True
    
    # save clean new tweets data to a data frame
    new_tweets_df = pd.DataFrame(new_filtered_tweets_dict, columns=["tweet_id", "user_id", "user_name", "user_location", "user_verified", "user_followers", "user_following", "retweets", "favorites", "liked", "fetched_at", "from_query"])
    
    # load tweets database on to a data frame
    print("Opening database...")
    tweet_records_old = pd.read_csv("tweet_records.csv", index_col=0)
    
    # append new tweets data to old records
    tweet_records_updated = pd.concat([tweet_records_old, new_tweets_df], ignore_index=True)
    
    # save tweets data on tweet_records.csv
    print("Updating database...")
    tweet_records_updated.to_csv("tweet_records.csv")
    
if __name__ == "__main__":
    print("Starting bot...")
    main()
    print("Finished. Shutting down.")

#%%
# limits_raw = api.rate_limit_status()
# limits_formatted = json.dumps(limits_raw, indent=2)
# print(limits_formatted)