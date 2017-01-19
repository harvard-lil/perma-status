import requests
from datetime import datetime
from dateutil import tz


def lookup(url):
    r = requests.get(url)
    data = r.json()
    return (data['objects'], data['meta']['next'])


url = "https://api.perma.cc/v1/public/archives/"
objects = []

(objs, next_url) = lookup(url)

now = datetime.now(tz=tz.tzutc())

for obj in objs:
    timestamp = datetime.strptime(obj['creation_timestamp'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=tz.tzutc())
    delta = now - timestamp
    triplet = (timestamp, delta.seconds, obj['queue_time'], obj['capture_time'])
    objects.append(triplet)

print("most recent capture was {seconds} seconds ago".format(seconds=objects[0][1]))
print("most recent completed capture was {seconds} seconds ago".format(seconds=filter(lambda x: x[3] is not None, objects)[0][1]))
print("twentieth capture ago was {seconds} seconds ago".format(seconds=objects[-1][1]))

queue_times = [x[2] for x in objects if x[2] is not None]
print("mean queue time over the last twenty captures is {mean:.2f} seconds".format(mean=sum(queue_times) / float(len(queue_times))))
capture_times = [x[3] for x in objects if x[3] is not None]
print("mean capture time over the last twenty captures is {mean:.2f} seconds".format(mean=sum(capture_times) / float(len(capture_times))))

print("number of unfinished captures in the last twenty is {number}".format(number=len([x for x in objects if x[3] is None])))
