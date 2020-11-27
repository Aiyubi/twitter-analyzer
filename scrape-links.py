import database_model as db
from database_model import Politician, Tweet, Hashtag, Link, LinkCategory
from functools import lru_cache
import concurrent.futures
import requests
from sqlalchemy import distinct
import re
import tldextract


session = db.get_session()

links = session.query(Link).filter_by(base_url=None).order_by(Link.link_original).all()

CHUNKSIZE = 100
CONNECTIONS = 100
TIMEOUT = 5


def load_url(url, timeout):
    url2 = format_url(url)
    # TODO set a useragent
    r = requests.head(url2, timeout=timeout, allow_redirects=True)

    if r:
        link_followed = r.url
        base_url = extract_domain(link_followed)
    else:
        link_followed = None
        base_url = extract_domain(url)
    return url, link_followed, base_url


@lru_cache(maxsize=None)
def extract_domain(url):
    return tldextract.extract(url).domain


def format_url(url):
    if not re.match('(?:http|ftp|https)://', url):
        return 'https://{}'.format(url)
    return url


def chunks(lst):
    for i in range(0, len(lst), CHUNKSIZE):
        yield lst[i:i + CHUNKSIZE]


urls = [x[0] for x in session.query(distinct(Link.link_original)).all()]

chunks_of_urls = chunks(urls)
for num, chunk_urls in enumerate(chunks_of_urls):
    print(num*CHUNKSIZE, '/', len(links))

    link_translation = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
        future_to_url = {executor.submit(load_url, url, TIMEOUT):url for url in chunk_urls}

        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                f_res = future.result()
                link_translation.append(f_res)
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, requests.exceptions.ReadTimeout):
                pass
            except Exception as e:
                # TODO dont catch every exception
                print(type(e))
                print(str(e))
                pass
    for link_o, link_f, domain in link_translation:
        l_obj = LinkCategory(
            link_original=link_o,
            link_followed=link_f,
            base_url=domain
        )
        session.add(l_obj)
    session.commit()

