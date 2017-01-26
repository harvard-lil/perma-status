import numpy as np
import argparse
from perma_times import get_objects


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", help="How many captures to check", default=20, type=int)
    parser.add_argument("--offset", help="How many captures back", default=0, type=int)
    args = parser.parse_args()
    objects = get_objects(args.limit, args.offset)
    output_numbers(objects, args.limit, args.offset)


def output_numbers(objects, limit, offset):
    mrc = objects[0][1]
    print("{offset}th capture ago was {seconds:.0f} seconds ago".format(offset=offset, seconds=mrc))
    mrcc = filter(lambda x: x[3] is not None, objects)[0][1]
    print("{offset}th completed capture was {seconds:.0f} seconds ago".format(offset=offset, seconds=mrcc))
    nthago = objects[-1][1]
    print("{limit}th capture ago was {seconds:.0f} seconds ago".format(limit=limit + offset, seconds=nthago))
    print("")
    queue_times = np.array([x[2] for x in objects if x[2] is not None])
    print("mean queue time over the {offset}th-{limit}th captures is {mean:.2f} seconds".format(offset=offset, limit=limit + offset, mean=np.mean(queue_times)))
    capture_times = np.array([x[3] for x in objects if x[3] is not None])
    print("mean capture time over the {offset}th-{limit}th captures is {mean:.2f} seconds".format(offset=offset, limit=limit + offset, mean=np.mean(capture_times)))
    print("")
    # why can capture_time be null when overall status is "success"?
    print("number of 'unfinished' captures in the {offset}th-{limit}th (null capture_time) is {number}".format(offset=offset, limit=limit + offset, number=len([x for x in objects if x[3] is None])))
    print("")
    # first "interval" is spurious, so skip it
    intervals = np.array([x[4] for x in objects[1:]])
    print("maximum interval between {offset}th-{limit}th captures is {max:.0f} seconds".format(offset=offset, limit=limit + offset, max=max(intervals)))
    print("minimum interval between {offset}th-{limit}th captures is {min:.0f} seconds".format(offset=offset, limit=limit + offset, min=min(intervals)))
    print("")
    print("capture health statistic candidates")
    print("(mrc == most recent capture, mrcc == most recent completed capture)")
    print("-----------------------------------")
    stat1 = mrc / np.mean(intervals)
    print("#1:  time to mrc / mean interval between {offset}th-{limit}th: {stat:.2f}".format(offset=offset, limit=limit + offset, stat=stat1))
    stat1a = mrcc / np.mean(intervals)
    print("#1a: time to mrcc / mean interval between {offset}th-{limit}th: {stat:.2f}".format(offset=offset, limit=limit + offset, stat=stat1a))
    stat2 = mrc / nthago
    print("#2:  time to mrc / time to {limit}th ago: {stat:.5f}".format(limit=limit + offset, stat=stat2))
    stat2a = mrcc / nthago
    print("#2a: time to mrcc / time to {limit}th ago: {stat:.5f}".format(limit=limit + offset, stat=stat2a))
    stat3 = np.std(intervals)
    print("#3:  standard deviation of intervals between {offset}th-{limit}th: {stat:.2f}".format(offset=offset, limit=limit + offset, stat=stat3))
    stat4 = mrc / stat3
    print("#4:  time to mrc / standard deviation of intervals between {offset}th-{limit}th: {stat:.2f}".format(offset=offset, limit=limit + offset, stat=stat4))
    stat5 = mrcc / stat3
    print("#5:  time to mrcc / standard deviation of intervals between {offset}th-{limit}th: {stat:.2f}".format(offset=offset, limit=limit + offset, stat=stat5))

    # compare some of these stats with limit == 20 to the same with limit == 100 or 1000?
    # or the change from limit 20, offset 100 to limit 20, offset 0?

if __name__ == "__main__":
    main()
