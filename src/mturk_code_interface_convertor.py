import re, json, sys
from pathlib import Path
import annotation_io
import read_data
import pandas as pd
annotation_io.set_recipe_source("npn-cooking")
mturk_path = Path(__file__).absolute().parent.parent / "mturk"/"results"

def load_results(batch):
    df = pd.read_csv(str(next(mturk_path.rglob(f"*{batch}*.csv"))))
    #hack:
    df = df.rename(columns={"Input.v9":"Answer.Title"})
    df = df[[c for c in df.columns if "Answer." in c or 'Id' in c]]
    df = df.rename(columns={c:c.split('.',1)[1] for c in df.columns if '.' in c})
    return df.set_index("AssignmentId")

def csv_row(lst):
    return ",".join(['"' +str(s).replace('"', '""').replace('\n', '\\n') +'"' for s in lst]) + "\n"


def inject_script(m):
    ret = '<script>\n'
    with (js_path / (m[2] + ".js")).open('r', encoding='utf8') as f:
        ret+=f.read()
    ret += '\n</script>'
    return ret


def inject_style(m):
    ret = '<style>\n'
    with (css_path / (m[2] + ".css")).open('r', encoding='utf8') as f:
        ret+=f.read()
    ret += '\n</style>'
    return ret


batch = 4335716
annotation_ids_from_batch = set(load_results(batch)["id"].unique())

magic_pattern = re.compile(r"{{[^}]+}}")
local_js_pattern = re.compile(r'(<script src="/js/([^?/"]+).js[^"]*">\s*</script>)')
local_css_pattern = re.compile(r'(<link rel="stylesheet" href="/css/([^?/"]+).css[^"]*"/>)')
form_pattern = re.compile(r"</?form[^>]*>", flags=re.IGNORECASE)
comment_pattern=re.compile(r"<!--.+-->")
annotate_template = Path(__file__).parent.parent / "templates" / "code.html"
output_path = Path(__file__).parent.parent / "mturk"
js_path = Path(__file__).parent.parent / "js"
css_path = Path(__file__).parent.parent / "css"

exp_path = Path(__file__).parent.parent/"data"/"npn-cooking"/"20210216_exp"
annotation_io.set_annotation_path(exp_path)

with annotate_template.open('r') as f:
    html = f.read()

html = comment_pattern.sub("", html)

magics = {"${v"+str(i)+"}": m for i, m in enumerate(sorted(set(magic_pattern.findall(html))))}
for k,v in magics.items():
    html=html.replace(v,k)

html = local_js_pattern.sub(inject_script,html)
html = local_css_pattern.sub(inject_style,html)
html = form_pattern.sub("", html)
# html = html.replace("</head>", '<script src="https://s3.amazonaws.com/mturk-public/externalHIT_v1.js"></script>\n</head>', 1)
with (output_path / "code_annotate.html").open('w', encoding='utf8') as f:
    f.write(html)

with (output_path / "code_annotate.csv").open('w', encoding="utf-8") as f:
    f.write(csv_row([f"v{i}" for i in range(len(magics))]))
    ##  names are important for `eval`
    ingredients_autocomplete = [{"label": desc, "value": {key: desc}} for desc, key in
                                annotation_io.ingredients_map.items()]
    commands = read_data.commands
    resources = [{"id": child["id"], "name": parent["name"] + '/' + child["name"]} for parent in read_data.resources for child in parent.get("children", [])]
    resources +=  [{"id": parent["id"], "name": parent["name"]} for parent in read_data.resources if 'children' not in parent]
    time_lengths = [{"id": k, "name": v} for k, v in read_data.time_lengths.items()]
    tools = [{"id": k, "name": v} for k, v in read_data.tools.items()]
    activities = [{"name": value, "id": key} for key, value in read_data.activities.items()]
    ingredients = []
    actions = []
    for id, annotation in annotation_io.all_annotations().items():
        if id not in annotation_ids_from_batch:
            continue
        line = []
        ingredients = [{"name": value, "id": key} for key, value in annotation["normalized_ingredients"].items()]
        instructions = annotation['instructions']
        num_instructions = len(annotation['instructions'])
        title = annotation['title']
        for alias, magic in magics.items():
            alias = alias.strip("${}")
            parts = magic.strip('{}').split('|')
            var = parts[0]
            if 'tojson' in parts:
                var = f"json.dumps({var})"
            line.append(eval(var))
        f.write(csv_row(line))
