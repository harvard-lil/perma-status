import requests
from datetime import datetime
from dateutil import tz
import argparse
import sys
import csv

parser = argparse.ArgumentParser()
parser.add_argument("--limit", help="How many captures to check", default=20, type=int)
parser.add_argument(
    "--offset", help="How many captures back to start", default=0, type=int
)
args = parser.parse_args()


def lookup(url):
    r = requests.get(url)
    data = r.json()
    return (data["objects"], data["meta"]["next"])


url = "https://api.perma.cc/v1/public/archives?limit={limit}&offset={offset}".format(
    limit=args.limit, offset=args.offset
)
objects = []

(objs, next_url) = lookup(url)

now = datetime.now(tz=tz.tzutc())
last = now
while True:
    for obj in objs:
        timestamp = datetime.strptime(
            obj["creation_timestamp"], "%Y-%m-%dT%H:%M:%SZ"
        ).replace(tzinfo=tz.tzutc())
        delta = (now - timestamp).total_seconds()
        if last == now:
            interval = None
        else:
            interval = (last - timestamp).total_seconds()
        last = timestamp
        objects.append(
            (
                obj["creation_timestamp"],
                delta,
                obj["queue_time"],
                obj["capture_time"],
                interval,
                obj["guid"],
            )
        )
    if len(objects) >= args.limit:
        break
    else:
        url = "https://api.perma.cc" + next_url
        (objs, next_url) = lookup(url)

fieldnames = ["timestamp", "delta", "queue_time", "capture_time", "interval", "guid"]
csvwriter = csv.writer(sys.stdout)
csvwriter.writerow(fieldnames)
for row in objects:
    csvwriter.writerow(row)
