import database_model as db
from database_model import Politician, Tweet, Hashtag, Link, LinkCategory
import matplotlib.pyplot as plt
from sqlalchemy import func
session = db.get_session()

data = session.query(LinkCategory.base_url,func.count()).group_by(LinkCategory.base_url).all()
data = sorted(data,key = lambda i:i[1], reverse=True)[:50]
data = sorted(data,key = lambda i:i[1], reverse=False)

domain_names = [val[0] for val in data]
num_used = [val[1] for val in data]
x_pos = [*range(len(domain_names))]
#plt.figure(dpi=1200)

plt.barh(x_pos, num_used)
plt.yticks(x_pos, domain_names)

plt.show()
