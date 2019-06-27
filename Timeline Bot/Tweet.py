__author__ = "Tiago Cruz de França"
__copyright__ = "Copyright 2018, UFRRJ"
__credits__ = ["Tiago França"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago França, Edu Mangabeira"
__email__ = "tcruz.franca@gmail.com"
__status__ = "Test"
class Tweet(object):
    
    def __init__(self, id_tweet,text,amount_of_comments,amount_of_likes, amount_of_retweets,created_at,screen_name, publisher_id, publisher_screen_name,snapshot_id,snapshot_timestamp,impression_order):
        '''
            @attributes:
                id_tweet: The tweet's Id.
                tweet_text: The catched up text.
                retweet_count: The amout of times the tweet was republished.
                tweet_created_at: The data when the message was published.                
                bot_screen_name: The user's Twitter name. E.g. @botPalestrinha
                publisher_screen_name: the author of the tweet.                                   
        
        '''
        self.id_tweet = id_tweet
        self.tweet_text = text
        self.tweet_amount_of_comments = amount_of_comments#
        self.tweet_amount_of_likes = amount_of_likes
        self.retweet_count = amount_of_retweets
        self.tweet_created_at = created_at
        self.bot_screen_name = screen_name
        self.publisher_id = publisher_id
        self.publisher_screen_name = publisher_screen_name
        self.snapshot_id = snapshot_id
        self.snapshot_timestamp = snapshot_timestamp
        self.impression_order = impression_order
         
