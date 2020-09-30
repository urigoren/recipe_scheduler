import sys, json

sys.path.append("src")
from flask import Flask, request, send_from_directory, render_template, redirect, url_for, jsonify
import annotation_io
import read_data
import instruction_parsing

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
    annotation=annotation_io.get_annotation(annotation_id)
    actions = []
    actions.extend([{"display": value, "id": key, "color": "#ff0000"} for key, value in read_data.tools.items()])
    actions.extend([{"display": value, "id": key, "color": "#0000ff"} for key, value in read_data.implicit_ingredients.items()])
    actions.extend([{"display": value, "id": key, "color": "#000000"} for key, value in read_data.time_lengths.items()])
    actions.extend([{"display": value, "id": key, "color": "#00ff00"} for key, value in annotation["normalized_ingredients"].items()])
    return render_template('annotate.html',
                           events=json.dumps(annotation["labels"]),
                           data=annotation,
                           id=annotation_id,
                           tools=read_data.tools,
                           implicits=read_data.implicit_ingredients,
                           time_lengths=read_data.time_lengths,
                           resources=json.dumps(read_data.resources),
                           actions=json.dumps(actions),
                           event0=json.dumps(annotation["labels"][0]),
                           num_instructions=len(annotation['instructions']),
                           )


@app.route('/simulate', methods=['GET', 'POST'])
@app.route('/simulate/<annotation_id>')
def simulate(annotation_id=None):
    if 'actions' in request.form:
        submitted_actions = json.loads(request.form.get('actions', '{}'))
        submitted_ingredients = json.loads(request.form.get('ingredients', '{}'))
        states = instruction_parsing.execute(submitted_ingredients, submitted_actions)
        # TODO: translate events to UI
        events = states
        return render_template("display.html",
                               resources=json.dumps(read_data.resources),
                               events=json.dumps(events),
                               )
    resources = [{"id": child["id"], "name": parent["name"] + '/' + child["name"]} for parent in read_data.resources for child in parent["children"]]
    time_lengths = [{"id": k, "name": v} for k, v in read_data.time_lengths.items()]
    tools = [{"id": k, "name": v} for k, v in read_data.tools.items()]
    ingredients = []
    derived_actions=[]
    if annotation_id is not None:
        annotation = annotation_io.get_annotation(annotation_id)
        derived_actions = instruction_parsing.program(annotation)
        derived_actions = [{
            "ts": a.ts,
            "arg": a.ingredient,
            "resource": a.resource,
            "command": [c for c in read_data.commands if c["name"] == a.command.name][0]['id'],
            "arg_type": [c for c in read_data.commands if c["name"] == a.command.name][0]['arg_type'],
        }
            for a in derived_actions]
        ingredients = [{"name": value, "id": key} for key, value in annotation["normalized_ingredients"].items()]

    return render_template("simulate.html",
                           resources=json.dumps(resources),
                           commands=json.dumps(read_data.commands),
                           tools=json.dumps(tools),
                           time_lengths=json.dumps(time_lengths),
                           actions=json.dumps(derived_actions),
                           ingredients=json.dumps(ingredients),
                           )


@app.route('/ingredients_autocomplete', methods=['GET', 'POST'])
def ingredients_autocomplete():
    term = request.args.get("term", "")
    ret=[{"label": k, "value": {"id": v, "name": k}} for k,v in read_data.ingredients_map.items() if term in k]
    return jsonify(ret)


@app.route('/display/<annotation_id>')
def display(annotation_id):
    annotation = annotation_io.get_annotation(annotation_id)
    return render_template("display.html",
                           resources=json.dumps(read_data.resources),
                           events=json.dumps(annotation["labels"][0]),
                           )


@app.route('/save_annotation/<annotation_id>', methods=['GET', 'POST'])
def save_annotation(annotation_id):
    annotation = annotation_io.get_annotation(annotation_id)
    annotation['labels'] = json.loads(request.form.get("events", "%"))
    annotation['status'] = request.form.get("status", '0')
    annotation_io.save_annotation(annotation_id, annotation)
    return redirect(url_for('index'))


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
