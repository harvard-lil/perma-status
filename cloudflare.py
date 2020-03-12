import click
from dotenv import load_dotenv
import os
import requests
import json
from datetime import datetime, timedelta


# this is a GraphQL query for Cloudflare's new analytics API.
# See https://developers.cloudflare.com/analytics/graphql-api/
# and https://graphql.org/
query = """
{
  viewer {
    zones(filter: {zoneTag: "REPLACE"}) {
      httpRequests1dGroups(limit: 10,
                           filter: {date_geq: "REPLACE",
                                    date_leq: "REPLACE"},
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


def days_ago(n):
    """ Helper function for default args """
    return str(datetime.now().date() - timedelta(days=n))


a_week_ago = days_ago(7)
yesterday = days_ago(1)


@click.command()
@click.option('--start',
              default=a_week_ago,
              help='Start date, defaults to a week ago')
@click.option('--end',
              default=yesterday,
              help='End date, defaults to yesterday')
def print_data(start, end):
    result = retrieve_data(start, end)
    print(json.dumps(result))


def retrieve_data(start=a_week_ago,
                  end=yesterday):
    load_dotenv()
    url = 'https://api.cloudflare.com/client/v4/graphql'
    headers = {'Content-Type': 'application/json',  # necessary?
               'X-Auth-Email': os.getenv('CF_EMAIL'),
               'X-Auth-Key': os.getenv('CF_KEY')}
    data = query.replace('{', '{{') \
                .replace('}', '}}') \
                .replace('REPLACE', '{}')  \
                .format(os.getenv('CF_ZONE'), start, end)
    r = requests.post(url, headers=headers, json={'query': data})
    return r.json()


if __name__ == '__main__':
    print_data()
