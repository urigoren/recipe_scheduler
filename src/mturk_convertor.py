import re, json, sys
from pathlib import Path
import annotation_io
import read_data
# annotation_io.set_recipe_source("npn-cooking")

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


MAX_ROWS = 100
magic_pattern = re.compile(r"{{[^}]+}}")
local_js_pattern = re.compile(r'(<script src="/js/([^?/"]+).js[^"]*">\s*</script>)')
local_css_pattern = re.compile(r'(<link rel="stylesheet" href="/css/([^?/"]+).css[^"]*"/>)')
form_pattern = re.compile(r"</?form[^>]*>", flags=re.IGNORECASE)
comment_pattern=re.compile(r"<!--.+-->")
annotate_template = Path(__file__).parent.parent / "templates" / "annotate.html"
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
html = re.sub(r'</script>[\s\t\n]*<script>',"", html, flags=re.MULTILINE)
# html = html.replace("</head>", '<script src="https://s3.amazonaws.com/mturk-public/externalHIT_v1.js"></script>\n</head>', 1)
with (output_path / "annotate.html").open('w', encoding='utf8') as f:
    f.write(html)

with (output_path / "annotate.csv").open('w', encoding="utf-8") as f:
    row_num = 0
    f.write(csv_row([f"v{i}" for i in range(len(magics))]))
    ##  names are important for `eval`
    time_lengths = read_data.time_lengths
    resources = read_data.resources
    activities = read_data.activities
    tools = read_data.tools
    containers = read_data.tool_containers
    ingredients_autocomplete = [{"label": desc, "value": {key: desc}} for desc, key in annotation_io.ingredients_map.items()]
    for id, annotation in annotation_io.all_annotations().items():
        line = []
        data=annotation
        num_instructions = len(annotation['instructions'])
        data["labels"]=[[] for _ in range(num_instructions)]
        validations=[[] for _ in range(num_instructions)]
        if 'validations' in annotation:
            validations=annotation['validations']
        actions = []
        actions.extend([{"display": value, "id": key, "color": "#ff0000"} for key, value in read_data.tools.items()])
        actions.extend([{"display": value, "id": key, "color": "#0000ff"} for key, value in read_data.activities.items()])
        actions.extend([{"display": value, "id": key, "color": "#000000"} for key, value in read_data.time_lengths.items()])
        actions.extend([{"display": value, "id": key, "color": "#00ff00"} for key, value in annotation["normalized_ingredients"].items()])
        for alias, magic in magics.items():
            alias = alias.strip("${}")
            parts = magic.strip('{}').split('|')
            var = parts[0]
            if 'tojson' in parts:
                var = f"json.dumps({var})"
            line.append(eval(var))
        f.write(csv_row(line))
        row_num +=1
        if row_num>=MAX_ROWS:
            break
