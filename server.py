import sys, json

sys.path.append("src")
from flask import Flask, request, send_from_directory, render_template, redirect, make_response, jsonify
import pandas as pd
from pathlib import Path
from operator import itemgetter as at
import annotation_io

data_dir = Path("data")

app = Flask(__name__)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('assets', 'favicon.ico')


@app.route('/js/<path:path>')
def serve_js(path):
    return send_from_directory('js', path)


@app.route('/css/<path:path>')
def serve_css(path):
    return send_from_directory('css', path)


@app.route('/')
def index():
    annotations = annotation_io.all_annotations()
    table = [{
        "id": annotation_id,
        "title": data["title"],
        "num_ing": len(data["ingredients"]),
        "num_instruct": len(data["instructions"]),
        "status": data["status"],
    }
        for annotation_id, data in annotations.items()
    ]
    return render_template('list.html', table=json.dumps(table))


@app.route('/annotate/<annotation_id>')
def annotate(annotation_id):
    return render_template('annotate.html')


@app.after_request
def add_no_cache(response):
    if request.endpoint != "static":
        response.headers["Cache-Control"] = "no-cache"
        response.headers["Pragma"] = "no-cache"
    return response


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


if __name__ == "__main__":
    app.run(port=8080, host='0.0.0.0', debug=True)
