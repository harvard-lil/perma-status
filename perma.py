import requests
from datetime import datetime
from dateutil import tz


def lookup(url):
    """
    Helper function for iterating through the Perma API
    """
    r = requests.get(url)
    data = r.json()
    if data["objects"]:
        return (data["objects"], data["meta"]["next"])
    else:
        return([], None)

def get_objects(limit, offset):
    """
    Return the last <limit> objects from the public Perma API,
    starting at <offset>
    """
    base = 'https://api.perma.cc/v1/public/archives'
    url = f'{base}?limit={limit}&offset={offset}'
    objects = []

    (objs, next_url) = lookup(url)

    now = datetime.now(tz=tz.tzutc())
    last = now
    for obj in objs:
        timestamp = datetime.strptime(
            obj["creation_timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ"
        ).replace(tzinfo=tz.tzutc())
        delta = (now - timestamp).total_seconds()
        if last == now:
            interval = None
        else:
            interval = (last - timestamp).total_seconds()
        last = timestamp
        user_upload = False
        for capture in obj["captures"]:
            if capture["user_upload"]:
                user_upload = True
        objects.append(
            (
                timestamp,
                delta,
                obj["queue_time"],
                obj["capture_time"],
                interval,
                user_upload,
            )
        )
    return objects


def get_counts(days):
    """
    Get the number of captures per day for a given sequence of days
    """
    counts = dict.fromkeys(days, 0)
    next_url = "https://api.perma.cc/v1/public/archives/"
    objects = []

    while next_url:
        (objs, next_url) = lookup(next_url)
        objects = objects + objs
        if objs[-1]["creation_timestamp"] < min(days):
            break

    for obj in objects:
        day = str(obj["creation_timestamp"][0:10])
        if day in days:
            counts[day] += 1

    return counts
