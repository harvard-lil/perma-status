from flask import Flask, render_template, jsonify
import os
from perma import get_objects


app = Flask(__name__)


@app.route("/")
def perma_status(up="up!", message=""):
    """
    Show the status page with charts

    The required template is generated by index.py
    """
    try:
        with open(os.getenv('MAINTENANCE_FILE', 'maintenance.txt'), 'r') as f:
            up = f.readline()
            message = f.read()
    except FileNotFoundError:
        pass
    try:
        return render_template("index.html", up=up, message=message)
    except Exception:
        return jsonify({"error": "missing template"}), 500


@app.route("/monitor")
def perma_monitor():
    """ hit the Perma API and get the last twenty captures for analysis """
    limit = 20
    thresholds = {"unfinished": 7, "statistic": 0.9}
    objects = get_objects(limit, 0)

    # how many of the last {limit} captures that are not user uploads
    # are not complete?
    unfinished = len([x for x in objects if x[3] is None and (not x[4])])

    # what is the ratio of seconds from now to the last completed capture
    # to the seconds from now to {limit} captures ago?
    # 'mrcc' means 'most recent completed capture'
    mrcc = list(filter(lambda x: x[3] is not None, objects))[0][1]
    nth_ago = objects[-1][1]
    statistic = mrcc / nth_ago

    report = {"status": [], "messages": []}
    if unfinished > thresholds["unfinished"]:
        report["status"].append("PROBLEM_PENDING")
        msg = f"{unfinished} uncompleted captures in the last {limit}"
        report["messages"].append(msg)

    if statistic > thresholds["statistic"]:
        report["status"].append("PROBLEM_LOWUSAGE")
        msg = f"statistic for time to last successful capture) is {statistic}"
        report["messages"].append(msg)

    if not report["status"]:
        report["status"] = ["OK"]

    output = {
        "unfinished": unfinished,
        "statistic": statistic,
        "report": report
    }
    return jsonify(**output)
