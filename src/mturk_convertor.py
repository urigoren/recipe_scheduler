import re,json
from pathlib import Path
import annotation_io
import read_data

def csv_safe(s):
    s = str(s)
    return '"' +s.replace('"', '""').replace('\n', '\\n') +'"'

SERVER = "http://54.93.36.200:8080/"
magic_pattern = re.compile(r"{{[^}]+}}")
annotate_template = Path(__file__).parent.parent / "templates" / "annotate.html"
output_path = Path(__file__).parent.parent / "mturk"

with annotate_template.open('r') as f:
    html = f.read()

magics = {"${v"+str(i)+"}": m for i, m in enumerate(sorted(set(magic_pattern.findall(html))))}
html=html.replace('"/', '"' + SERVER)
for k,v in magics.items():
    html=html.replace(v,k)
with (output_path / "annotate.html").open('w') as f:
    f.write(html)

with (output_path / "annotate.csv").open('w') as f:
    f.write(",".join([csv_safe(f"v{i}") for i in range(len(magics))]) + "\n")
    ##  names are important for `eval`
    events = []
    time_lengths = read_data.time_lengths
    time_lengths[""] = "Ends Immediately"
    resources=read_data.resources
    implicits=read_data.implicit_ingredients
    tools=read_data.tools
    line=[]
    for id, annotation in annotation_io.all_annotations().items():
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
    f.write(",".join([csv_safe(c) for c in line]))
    f.write("\n")
