import sys, json, random
from datetime import datetime, timedelta
sys.path.append("src")
from flask import Flask, request, send_from_directory, render_template, redirect, url_for, jsonify
import annotation_io
import read_data
import instruction_parsing

annotation_io.set_recipe_source("npn-cooking")

app = Flask(__name__)

def isJson(x):
    try:
        json.loads(x)
        return True
    except:
        return False

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
    return render_template('list.html', table=table)


@app.route('/annotate/<mturk_batch>/<annotation_id>')
@app.route('/annotate/<annotation_id>')
def annotate(annotation_id, mturk_batch=None):
    if mturk_batch:
        annotation = annotation_io.mturk_annotation(mturk_batch, annotation_id)
    else:
        annotation=annotation_io.get_annotation(annotation_id)
    actions = []
    actions.extend([{"display": value, "id": key, "color": "#ff0000"} for key, value in read_data.tools.items()])
    actions.extend([{"display": value, "id": key, "color": "#0000ff"} for key, value in read_data.activities.items()])
    actions.extend([{"display": value, "id": key, "color": "#000000"} for key, value in read_data.time_lengths.items()])
    actions.extend([{"display": value, "id": key, "color": "#00ff00"} for key, value in annotation["normalized_ingredients"].items()])
    tl = read_data.time_lengths
    tl[""] = "Ends Immediately"
    ingredients_autocomplete = [{"label":desc, "value":{key: desc}} for desc, key in annotation_io.ingredients_map.items()]
    return render_template('annotate.html',
                           data=annotation,
                           id=annotation_id,
                           tools=read_data.tools,
                           activities=read_data.activities,
                           time_lengths=tl,
                           resources=read_data.resources,
                           actions=actions,
                           num_instructions=len(annotation['instructions']),
                           ingredients_autocomplete=ingredients_autocomplete,
                           )


@app.route('/simulate', methods=['GET', 'POST'])
@app.route('/simulate/<annotation_id>')
@app.route('/simulate/<mturk_batch>/<annotation_id>')
def simulate(annotation_id=None, mturk_batch=None):
    if 'actions' in request.form:
        submitted_actions = json.loads(request.form.get('actions', '{}'))
        submitted_ingredients = json.loads(request.form.get('ingredients', '{}'))
        submitted_instructions=instruction_parsing.Instruction.from_dicts(submitted_actions)
        states = instruction_parsing.execute(submitted_ingredients, submitted_instructions)
        # TODO: translate events to UI
        actions_map = []
        actions_map.extend([(key,{"text": value, "color": "#ff0000"}) for key, value in read_data.tools.items()])
        actions_map.extend([(key,{"text": value, "color": "#0000ff"}) for key, value in read_data.activities.items()])
        actions_map.extend([(key,{"text": value, "color": "#000000"}) for key, value in read_data.time_lengths.items()])
        actions_map.extend([(value,{"text": key, "color": "#00ff00"}) for key, value in annotation_io.ingredients_map.items()])
        actions_map = dict(actions_map)
        def ui_view(ts, res, item):
            return {
                "action": item,
                "barColor": actions_map[item]["color"],
                "start": datetime(2020, 1, 1+ts).strftime("%Y-%m-%dT%H:%M:%S"),
                "end": datetime(2020,1,2+ts).strftime("%Y-%m-%dT%H:%M:%S"),
                "id": item + ":" + str(random.randint(100000,999999)),
                "resource": res,
                "text": actions_map[item]["text"],
            }
        events = [ui_view(ts, res, item) for ts, d in states for res, items in d.items() for item in items]
        events += [ui_view(0, instruction_parsing.UNUSED_RESOURCE_ID, ing["id"]) for ing in submitted_ingredients]
        events = sorted(events, key=lambda x:x["id"][0])
        return render_template("display.html",
                               resources=read_data.resources,
                               events=events,
                               )
    resources = [{"id": child["id"], "name": parent["name"] + '/' + child["name"]} for parent in read_data.resources for child in parent.get("children", [])]
    resources +=  [{"id": parent["id"], "name": parent["name"]} for parent in read_data.resources if 'children' not in parent]
    time_lengths = [{"id": k, "name": v} for k, v in read_data.time_lengths.items()]
    tools = [{"id": k, "name": v} for k, v in read_data.tools.items()]
    activities = [{"name": value, "id": key} for key, value in read_data.activities.items()]
    ingredients = []
    derived_actions=[]
    if annotation_id is not None:
        if mturk_batch:
            annotation = annotation_io.mturk_annotation(mturk_batch, annotation_id)
        else:
            annotation = annotation_io.get_annotation(annotation_id)
        derived_actions = instruction_parsing.program(annotation)
        derived_actions = [{
            "ts": a.ts,
            "arg": a.arg,
            "resource": a.resource,
            "command": [c for c in read_data.commands if c["name"] == a.command.name][0]['id'],
            "arg_type": [c for c in read_data.commands if c["name"] == a.command.name][0]['arg_type'],
        }
            for a in derived_actions]
        ingredients = [{"name": value, "id": key} for key, value in annotation["normalized_ingredients"].items()]

    return render_template("simulate.html",
                           resources=resources,
                           commands=read_data.commands,
                           activities=activities,
                           tools=tools,
                           time_lengths=time_lengths,
                           actions=derived_actions,
                           ingredients=ingredients,
                           )


@app.route('/ingredients_autocomplete', methods=['GET', 'POST'])
def ingredients_autocomplete():
    term = request.args.get("term", "")
    ret=[{"label": k, "value": {"id": v, "name": k}} for k,v in annotation_io.ingredients_map.items() if term in k]
    return jsonify(ret)


@app.route('/display/<annotation_id>')
def display(annotation_id):
    annotation = annotation_io.get_annotation(annotation_id)
    return render_template("display.html",
                           resources=read_data.resources,
                           events=annotation["labels"][0],
                           )


@app.route('/save_annotation/<annotation_id>', methods=['GET', 'POST'])
def save_annotation(annotation_id):
    annotation = annotation_io.get_annotation(annotation_id)
    annotation['labels'] = json.loads(request.form.get("events", "%"))
    annotation['status'] = request.form.get("status", '0')
    annotation_io.save_annotation(annotation_id, annotation)
    return redirect(url_for('index'))


@app.route('/edit', methods=['GET', 'POST'])
def edit_jsons():
    data_types = ("activities", "time_lengths", "tools", "resources")
    if request.form.get("data_type", "") in data_types and isJson(request.form.get('data', "")):
        data_type = request.form['data_type']
        assert data_type in data_types
        jdata = json.loads(request.form['data'])
        with (read_data.data_path / (data_type + ".json")).open('w') as f:
            if data_type!='resources':
                json.dump(jdata, f, indent=4, sort_keys=True)
            else:
                json.dump(jdata, f, indent=4)
        read_data.reload()
        return f"<h1>Saved {data_type}</h1>"
    data=dict()
    for t in data_types:
        with (read_data.data_path / (t + ".json")).open('r') as f:
            data[t] = f.read()
    return render_template("edit_data.html", data_types=data_types, data=data)


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
