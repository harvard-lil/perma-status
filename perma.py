import requests
from tenacity import retry, wait_exponential


@retry(wait=wait_exponential(multiplier=1, min=4, max=10))
def lookup(url):
    """
    Helper function for iterating through the Perma API
    """
    r = requests.get(url)
    try:
        data = r.json()
    except Exception as e:
        raise Exception(f"Failed to get JSON: {e} -- response content is {r.text}")
    if data["objects"]:
        return (data["objects"], data["meta"]["next"])
    else:
        return([], None)


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
