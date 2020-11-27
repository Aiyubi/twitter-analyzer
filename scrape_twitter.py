import database_model as db
from database_model import Politician, Tweet, Hashtag
import sqlalchemy

import twint
import arrow

def get_tweets(twitter_handle,since,until):
    c = twint.Config()
    c.Username = twitter_handle
    c.Pandas = True
    c.Hide_output = True
    #c.Retries_count = 1
    c.Retweets = True
    if since:
        c.Since = since.format('YYYY-MM-DD 00:00:00')
    else:
        c.Since = '2017-09-24 00:00:00'
    if until:
        c.Until = until.format('YYYY-MM-DD 23:59:59')
    #c.Limit = 200
    twint.run.Search(c)
    return twint.storage.panda.Tweets_df


def fill_database():
    session = db.get_session()

    politicians =session.query(Politician).all()

    counter = 0
    for politician in politicians:
        counter += 1
        print(counter, politician.twitter_handle)
        if len(politician.tweets):
            print("already scaned, skiping")
            continue

        if not politician.twitter_handle:
            continue

        tweets = get_tweets(politician.twitter_handle,politician.start_date,politician.end_date)

        try:
            for index, tweet in tweets.iterrows():
                # print(tweet)
                t = Tweet(
                        id = tweet["id"],
                        date = arrow.get(tweet["date"]),
                        text = tweet["tweet"],
                        nlikes = tweet["nlikes"],
                        nreplie = tweet["nreplies"],
                        nretweets = tweet["nretweets"]
                )
                session.add(t)
                politician.tweets.append(t)
                for hashtag in tweet["hashtags"]:
                    h = Hashtag(tag=hashtag[1:])
                    t.hashtags.append(h)
                    session.add(h)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            session.rollback()
            continue


if __name__ == "__main__":
    fill_database()
