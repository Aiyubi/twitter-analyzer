import requests
import httplib2
from bs4 import BeautifulSoup, SoupStrainer
import arrow
import database_model as db

http = httplib2.Http()

members_of_bundestag = requests.get('https://www.abgeordnetenwatch.de/api/v2/candidacies-mandates?parliament_period=111&range_end=999').json()['data']

session = db.get_session()


def get_twitter_handle(member):
    status, response = http.request(member['politician']['abgeordnetenwatch_url'])
    for link in BeautifulSoup(response, parse_only=SoupStrainer('a')):
        if link.has_attr('href') and 'twitter' in link['href']:

            # this will remove some of the common adjustments to the url
            twitter_handle = link['href'].replace(r'https://twitter.com/','')\
                                        .replace(r'https://www.twitter.com/','')\
                                        .replace('twitter.com/','')\
                                        .replace('http://www.twitter.com/','')\
                                        .replace('?lang=de', '')

            if twitter_handle == "a_watch":
                twitter_handle = None

            print(member['politician']['label'], twitter_handle)

            return twitter_handle


for member in members_of_bundestag:
    politician = db.Politician(
        name=member['politician']['label'],
        fraction=member['fraction_membership'][0]['fraction']['label'].replace(r' (Bundestag)', '') if 'fraction_membership' in member else None,
        twitter_handle=get_twitter_handle(member),
        start_date=arrow.get(member['start_date']),
        end_date=arrow.get(member['end_date'])
    )
    session.add(politician)
    session.commit()