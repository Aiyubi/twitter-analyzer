import csv
import twint
import pandas
import logging
import matplotlib.pyplot as plt
import arrow
from sqlalchemy import func

import database_model as db
from database_model import Politician, Tweet, Hashtag

logging.basicConfig(level="ERROR")

def get_csv_data(csv_filename):
    list_of_people = []
    with open(csv_filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            list_of_people.append(row)
    return list_of_people


def get_tweets(twitter_handle):
    c = twint.Config()
    c.Username = twitter_handle
    c.Pandas = True
    c.Hide_output = True
    #c.Limit = 200
    twint.run.Search(c)
    return twint.storage.panda.Tweets_df


def get_hashtag_count(tweet_df):
    hashtags = {}
    for tags in tweet_df['hashtags']:
        for tag in tags:
            if tag not in hashtags:
                hashtags[tag] = 1
            else:
                hashtags[tag] += 1
    hashtags = {k: v for k, v in sorted(hashtags.items(), key=lambda x: x[1], reverse=True)}
    return hashtags

def plot_hashtags(party,dict_hashtags):
    dict_hashtags = list(dict_hashtags.items())[:30]

    keys = [x[0] for x in dict_hashtags]
    values = [x[1] for x in dict_hashtags]

    plt.bar(keys,values)
    plt.xticks(rotation=45, ha='right')
    plt.title(party)
    plt.xlabel('hashtag')
    plt.ylabel('frequency')
    plt.show()

import multidict as multidict
from wordcloud import WordCloud

def plot_wordcloud(dict_hshtags):
    plt.figure(dpi=600)
    fullTermsDict = multidict.MultiDict()
    for key, value in dict_hshtags.items():
        fullTermsDict.add(key, value)
    wc = WordCloud(background_color="white")
    wc.generate_from_frequencies(fullTermsDict)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.show()


def process_politician(name, party, twitter_handle):
    session = db.get_session()
    pol = Politician(name=name, party=party, twitter_handle=twitter_handle)
    session.add(pol)
    tweets = get_tweets(twitter_handle)
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
        pol.tweets.append(t)
        for hashtag in tweet["hashtags"]:
            h = Hashtag(tag=hashtag[1:])
            t.hashtags.append(h)
            session.add(h)
    session.commit()

def fill_database():
    csv_filename = "data-de.csv"
    list_of_people = get_csv_data(csv_filename)
    #print(list_of_people[0])
    for politician in list_of_people:
        process_politician(politician['name'],politician['party'],politician['twitter handle'])

def get_list_of_partys():
    session = db.get_session()
    partys = []
    for value in session.query(db.Politician.party).distinct():
        partys.append(value[0])
    return partys

def get_frequency_of_partys_hashtags():
    session = db.get_session()

    politicians = session.query(db.Politician).all()


    hashtag_uses = {}
    for politician in politicians:
        if politician.party not in hashtag_uses:
            hashtag_uses[politician.party] = {}
        for tweet in politician.tweets:
            for hashtag in tweet.hashtags:
                hashtag = hashtag.tag
                if hashtag not in hashtag_uses[politician.party]:
                    hashtag_uses[politician.party][hashtag] = 1
                else:
                    hashtag_uses[politician.party][hashtag] += 1

    for party in hashtag_uses:
        hashtag_uses[party] = {k: v for k, v in sorted(hashtag_uses[party].items(), key=lambda x: x[1], reverse=True) if v > 20}

    print (hashtag_uses)
    return hashtag_uses
    '''
    hashtag_uses = session.query(db.Politician.party,db.Hashtag.tag,func.count())\
        .select_from(db.Politician,db.Tweet,db.Hashtag)\
        .group_by(db.Politician.party,db.Hashtag.tag)\
        .all()

    result_dict = {}
    for party,tag,frequency in hashtag_uses:
        if party not in result_dict:
            result_dict[party] = {}
        result_dict[party][tag] = frequency

    # sorting by frequency descending
    for party in result_dict:
        result_dict[party] = {k: v for k, v in sorted(result_dict[party].items(), key=lambda x: x[1], reverse=True) if v > 20}

    return result_dict
    '''

def generate_plots():
    frequency_data = get_frequency_of_partys_hashtags()

    for party, frequencys in frequency_data.items():
        if frequencys:
            plot_hashtags(party,frequencys)
            plot_wordcloud(frequencys)



if __name__ == "__main__":
    fill_database()
    generate_plots()
    #get_frequency_of_partys_hashtags()


    '''
    df = get_tweets("Timon_Gremmels")
    ht = get_hashtag_count(df)
    #print(ht)
    ht = {k:v for k,v in ht.items() if v >= 5}
    plot_hashtags(ht)
    plot_wordcloud(ht)
    '''