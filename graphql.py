import click
from dotenv import load_dotenv
import os
import requests
import json
from datetime import datetime, timedelta


query = """
{
  viewer {
    zones(filter: {zoneTag: "ZONETAG"}) {
      httpRequests1dGroups(limit: 10,
                           filter: {date_geq: "STARTDATE",
                                    date_leq: "ENDDATE"},
                           orderBy: [date_ASC]) {
        sum {
          bytes
          requests
          pageViews
          threats
        }
        uniq {
          uniques
        }
        dimensions {
          date
        }
      }
    }
  }
}
"""


@click.command()
@click.option('--start',
              default=str(datetime.now().date() - timedelta(days=7)),
              help='Start date, defaults to a week ago')
@click.option('--end',
              default=str(datetime.now().date() - timedelta(days=1)),
              help='End date, defaults to yesterday')
def hello(start, end):
    result = retrieve_data(start, end)
    print(json.dumps(result))


def retrieve_data(start=str(datetime.now().date() - timedelta(days=7)),
                  end=str(datetime.now().date() - timedelta(days=1))):
    load_dotenv()
    url = 'https://api.cloudflare.com/client/v4/graphql'
    headers = {'Content-Type': 'application/json',  # necessary?
               'X-Auth-Email': os.getenv('CF_EMAIL'),
               'X-Auth-Key': os.getenv('CF_KEY')}
    data = query.replace('{', '{{') \
                .replace('}', '}}') \
                .replace('ZONETAG', '{}')  \
                .replace('STARTDATE', '{}')  \
                .replace('ENDDATE', '{}')  \
                .format(os.getenv('CF_ZONE'), start, end)
    r = requests.post(url, headers=headers, json={'query': data})
    return r.json()


if __name__ == '__main__':
    hello()
