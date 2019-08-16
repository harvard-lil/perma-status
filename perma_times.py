import requests
from datetime import datetime
from dateutil import tz


def lookup(url):
    r = requests.get(url)
    data = r.json()
    return (data["objects"], data["meta"]["next"])


def get_objects(limit, offset):
    url = "https://api.perma.cc/v1/public/archives?limit={limit}&offset={offset}".format(
        limit=limit, offset=offset
    )
    objects = []

    (objs, next_url) = lookup(url)

    now = datetime.now(tz=tz.tzutc())
    last = now
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
