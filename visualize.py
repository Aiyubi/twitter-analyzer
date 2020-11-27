import csv
import pandas
import logging
import matplotlib.pyplot as plt
import arrow
from sqlalchemy import func

import database_model as db
from database_model import Politician, Tweet, Hashtag

import multidict as multidict
from wordcloud import WordCloud

logging.basicConfig(level="ERROR")


def analyze_number_of_tweets(session):
    tweet_amount = []
    for politician in session.query(Politician).all():
        color = fraction2color(politician.fraction)
        tweet_amount.append( (len(politician.tweets), color ,politician.name) )

    # sort
    tweet_amount = sorted(tweet_amount,key=lambda x:x[0])

    # only people with tweets
    tweet_amount = [x for x in tweet_amount if x[0] > 0]

    tweet_amount = tweet_amount[::-1]

    tweet_amount = tweet_amount[:30]

    for index,row in enumerate(tweet_amount):
        plt.bar(row[2],row[0],color=row[1])

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f'output/most-tweets.svg', format="svg")


def get_frequency_of_partys_hashtags():
    session = db.get_session()

    hashtags = session.query(Hashtag).all()

    hashtag_uses = {}

    total_hashtags = len(hashtags)
    scanned_hashtags = 0
    print()
    for h in hashtags:
        fraction = h.tweet.politician.fraction
        tag = h.tag

        if fraction not in hashtag_uses:
            hashtag_uses[fraction] = {}

        if tag not in hashtag_uses[fraction]:
            hashtag_uses[fraction][tag] = 1
        else:
            hashtag_uses[fraction][tag] += 1

        scanned_hashtags += 1

        if scanned_hashtags % 100 == 0:
            print(f"Scanned Hashtags: {scanned_hashtags}/{total_hashtags}\r", end="")

    print(f"Scanned Hashtags: {scanned_hashtags}/{total_hashtags}\r")

    for fraction in hashtag_uses:
        hashtag_uses[fraction] = {k: v for k, v in sorted(hashtag_uses[fraction].items(), key=lambda x: x[1], reverse=True) if v > 20}

    return hashtag_uses


def plot_hashtags(party,dict_hashtags):
    plt.figure()
    dict_hashtags = list(dict_hashtags.items())[:30]

    keys = [x[0] for x in dict_hashtags]
    values = [x[1] for x in dict_hashtags]

    plt.bar(keys,values)
    plt.xticks(rotation=45, ha='right')
    plt.title(party)
    plt.xlabel('hashtag')
    plt.ylabel('frequency')

    #plt.show()
    partyname = party.replace('/', '')
    plt.tight_layout()
    plt.savefig(f'output/{partyname}.svg', format="svg")
    plt.close()


def plot_wordcloud(party,dict_hshtags):
    plt.figure(dpi=600)
    fullTermsDict = multidict.MultiDict()
    for key, value in dict_hshtags.items():
        fullTermsDict.add(key, value)
    wc = WordCloud(background_color="white", width=1600, height=800)
    wc.generate_from_frequencies(fullTermsDict)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")

    partyname=party.replace('/','')
    plt.tight_layout()
    plt.savefig(f'output/{partyname}-wc.svg',format="svg")
    #plt.show()
    plt.close()


def fraction2color(fraction):
    decode_matrix = {
        'fraktionslos': 'grey',
        'SPD': 'red',
        'FDP': 'yellow',
        'DIE LINKE': 'purple',
        'DIE GRÜNEN': 'green',
        'CDU/CSU': 'black',
        'AfD': 'blue'
    }
    return decode_matrix.get(fraction,'grey')


def plot_hashtag_usage_over_time(tag):
    plt.figure()
    session = db.get_session()
    hashtags = session.query(db.Hashtag).filter(func.lower(db.Hashtag.tag)==tag.lower()).all()

    position = {
        'AfD': 1,
        'FDP': 2,
        'CDU/CSU': 3,
        'SPD': 4,
        'DIE GRÜNEN': 5,
        'DIE LINKE': 6
    }

    for ht in hashtags:
        fraction = ht.tweet.politician.fraction
        tweet_time = ht.tweet.date
        plt.plot_date(tweet_time,position.get(fraction,0),color=fraction2color(fraction))

    plt.title('Use of hashtag: '+tag)
    plt.yticks(list(position.values()),list(position.keys()))
    plt.tight_layout()
    plt.savefig(f'output/hashtag-{tag}.svg', format="svg")
    plt.close()


def get_all_hashtag_frequency():
    session = db.get_session()
    hash_frequencys = session.query(Hashtag.tag,func.count()).group_by(Hashtag.tag).all()
    hash_frequencys = sorted(hash_frequencys, key=lambda x: x[1], reverse=True)
    return hash_frequencys


def plot_top_hashtags():
    plt.figure()
    hash_frequencys = get_all_hashtag_frequency()
    hash_frequencys = hash_frequencys[:30]

    keys = [x[0] for x in hash_frequencys]
    values = [x[1] for x in hash_frequencys]

    plt.bar(keys, values)
    plt.xticks(rotation=45, ha='right')
    plt.title("Hashtags used by all partys")
    plt.xlabel('hashtag')
    plt.ylabel('frequency')

    # plt.show()
    plt.tight_layout()
    plt.savefig(f'output/all_hashtags.svg', format="svg")
    plt.close()


def plot_top_x_hashtags():
    hash_frequencys = get_all_hashtag_frequency()
    top_hashtags = hash_frequencys[:100]
    for ht in top_hashtags:
        plot_hashtag_usage_over_time(ht[0])


def export_fraction_hachtag_usage():
    fraktionen = [ 'AfD','FDP','CDU/CSU','SPD','DIE GRÜNEN','DIE LINKE','fraktionslos']
    hashtags = ['afd','afdimbundestag','afdwirkt','fdp','csu','cdu','spd','gruenen','grüne','grünen','linke','dielinke','jamaika','groko']

    result = {}
    csv_columns = ['hashtag']

    for fraktion in fraktionen:
        csv_columns.append(fraktion)

    for ht in hashtags:
        result[ht] = get_number_fraktion_hachshtag_use(ht)
        result[ht]['hashtag'] = ht

        for fraktion in fraktionen:
            if fraktion not in result[ht]:
                result[ht][fraktion] = 0

    with open("output/fraktionenHT_usage.csv",'w+', newline='') as csvfile:
        writer = csv.DictWriter(csvfile,fieldnames=csv_columns)
        writer.writeheader()
        for data in result.values():
            writer.writerow(data)


def get_number_fraktion_hachshtag_use(ht):
    result={}
    matching_hashtags = session.query(Hashtag).filter(Hashtag.tag==ht).all()
    for mh in matching_hashtags:
        fraktion = mh.tweet.politician.fraction
        if not fraktion in result:
            result[fraktion] = 1
        else:
            result[fraktion] += 1
    return result


if __name__ == "__main__":

    session = db.get_session()

    export_fraction_hachtag_usage()
    '''
    analyze_number_of_tweets(session)

    frequency_data = get_frequency_of_partys_hashtags()
    for party, frequencys in frequency_data.items():
        if frequencys:
            plot_hashtags(party,frequencys)
            plot_wordcloud(party,frequencys)

    plot_top_hashtags()
    plot_top_x_hashtags()
    '''

