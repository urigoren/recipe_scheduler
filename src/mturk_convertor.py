import re, json, sys
from pathlib import Path
import annotation_io
import read_data


def csv_row(lst):
    return ",".join(['"' +str(s).replace('"', '""').replace('\n', '\\n') +'"' for s in lst]) + "\n"


def inject_script(m):
    ret = '<script type="text/javascript">\n'
    with (js_path / (m[2] + ".js")).open('r', encoding='utf8') as f:
        ret+=f.read()
    ret += '\n</script>'
    return ret


MAX_ROWS = 499
magic_pattern = re.compile(r"{{[^}]+}}")
local_js_pattern = re.compile(r'(<script src="/js/([^?/"]+).js[^"]*">\s*</script>)')
annotate_template = Path(__file__).parent.parent / "templates" / "annotate.html"
output_path = Path(__file__).parent.parent / "mturk"
js_path = Path(__file__).parent.parent / "js"

with annotate_template.open('r') as f:
    html = f.read()

magics = {"${v"+str(i)+"}": m for i, m in enumerate(sorted(set(magic_pattern.findall(html))))}
for k,v in magics.items():
    html=html.replace(v,k)

html = local_js_pattern.sub(inject_script,html)

html = html.replace("</head>", '<script src="https://assets.crowd.aws/crowd-html-elements.js"></script>\n</head>', 1)
html = html.replace("</form>", '</form>\n<crowd-form answer-format="flatten-objects"><input type="hidden" name="mturk_result" id="mturk_result" value="{}"></crowd-form>', 1)
with (output_path / "annotate.html").open('w', encoding='utf8') as f:
    f.write(html)

with (output_path / "annotate.csv").open('w') as f:
    row_num = 0
    f.write(csv_row([f"v{i}" for i in range(len(magics))]))
    ##  names are important for `eval`
    events = []
    time_lengths = read_data.time_lengths
    time_lengths[""] = "Ends Immediately"
    resources=read_data.resources
    implicits=read_data.implicit_ingredients
    tools=read_data.tools
    for id, annotation in annotation_io.all_annotations().items():
        line = []
        data=annotation
        num_instructions = len(annotation['instructions'])
        actions = []
        actions.extend([{"display": value, "id": key, "color": "#ff0000"} for key, value in read_data.tools.items()])
        actions.extend([{"display": value, "id": key, "color": "#0000ff"} for key, value in read_data.implicit_ingredients.items()])
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
        if row_num>MAX_ROWS:
            break
