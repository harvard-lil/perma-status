import argparse
import os
from datetime import datetime, timedelta
import requests
import pygal
from jinja2 import Template
import csv


parser = argparse.ArgumentParser()
parser.add_argument("--url", help="Cloudflare API URL", default=os.environ.get('CLOUDFLARE_API_URL', None))
parser.add_argument("--email", help="Cloudflare API email address", default=os.environ.get('CLOUDFLARE_API_EMAIL', None))
parser.add_argument("--key", help="Cloudflare API key", default=os.environ.get('CLOUDFLARE_API_KEY', None))
parser.add_argument("--html", help="Output filename for HTML")
parser.add_argument("--csv", help="Output filename for CSV")
args = parser.parse_args()

# tidied is for easier consumption by R / ggplot2
tidied = [['type', 'date', 'count']]

today = datetime.today()
days = map(lambda d: d.strftime('%Y-%m-%d'),
           [today + timedelta(days=i) for i in range(-7,0)])

# cloudflare stats
# check that the args are not None?
url = args.url
headers = {
    "Content-Type": "application/json",
    "X-Auth-Key": args.key,
    "X-Auth-Email": args.email
    }
    
r = requests.get(args.url, headers=headers)
data = r.json()

output = { u'uniques':   [],
           u'threats':   [],
           u'bandwidth': [],
           u'pageviews': [],
           u'requests':  [],}

for day in data['result']['timeseries']:
    for key in output.keys():
        try:
            output[key].append(day[key]['all'])
            for idx, val in enumerate(days):
                tidied.append([key, val, output[key][idx]])
        except:
            pass

def cloudflare_formatter(x):
    """
    This is dodgy. Only will work while number of requests is low.
    Make the cut-off dependent on the data....
    """
    if x > 100000:
        return "%dM" % (round(x) / 1024 / 1024,)
    else:
        return "%d" % x

cloudflare = pygal.Line(disable_xml_declaration=True, height=200, value_formatter=cloudflare_formatter, x_label_rotation=20, max_scale=10)
today = datetime.today()
cloudflare.x_labels = map(lambda d: d.strftime('%a %Y-%m-%d'),
                     [today + timedelta(days=i) for i in range(-7,0)])
for key in output:
    if key != 'bandwidth':
        cloudflare.add(key, output[key])

cloudflare.add('bandwidth', output['bandwidth'], secondary=True)


# perma captures
counts = dict.fromkeys(days, 0)

def lookup(url):
    r = requests.get(url)
    data = r.json()
    return (data['objects'], data['meta']['next'])

url = "https://api.perma.cc/v1/public/archives/"
objects = []

while True:
    (objs, next_url) = lookup(url)
    objects = objects + objs
    if objs[-1]["creation_timestamp"] < min(days):
        break
    else:
        url = "https://api.perma.cc%s" % (next_url,)

for obj in objects:
    day = str(obj["creation_timestamp"][0:10])
    if day in days:
        counts[day] += 1

captures = pygal.Line(disable_xml_declaration=True, height=200, x_label_rotation=20)
today = datetime.today()
captures.x_labels = map(lambda d: d.strftime('%a %Y-%m-%d'),
                     [today + timedelta(days=i) for i in range(-7,0)])

captures.add('captures', [ counts[day] for day in days ])

for weekday in days:
    tidied.append(['captures', weekday, counts[weekday]])

tpl = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8"/>
    <title>Perma.cc status</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="//fonts.googleapis.com/css?family=Raleway:400,300,600" rel="stylesheet" type="text/css">
    <link rel="stylesheet" href="css/normalize.css">
    <link rel="stylesheet" href="css/skeleton.css">
    <link href="images/favicon.ico" rel="shortcut icon" type="image/x-icon">
  </head>
  <body>
    <div class="section charts">
      <div class="container">
        <h3><a href="https://perma.cc/">perma.cc</a> is up!</h3>
        <div class="row">
          <h5>perma captures this week</h5>
            <figure>
              {{ captures }}
            </figure>
        </div>
        <div class="row">
          <h5>cloudflare stats this week</h5>
            <figure>
              {{ cloudflare }}
            </figure>
        </div>
      </div>
    </div>
  </body>
</html>
'''

template = Template(tpl)

# replace the "Pygal" title, since pygal doesn't allow you to omit it
if args.html:
    with open(args.html, 'w') as f:
        f.write(template.render(captures=captures.render(show_legend=True).replace('<title>Pygal</title>', '<title>Perma captures</title>'), cloudflare=cloudflare.render(show_legend=True).replace('<title>Pygal</title>', '<title>Cloudflare stats</title>')).encode('utf-8'))

if args.csv:
    with open(args.csv, 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(tidied)
