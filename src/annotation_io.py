import json
from pathlib import Path
import pandas as pd

base_path = Path(__file__).absolute().parent.parent
mturk_path = base_path / "mturk/results"
annotations_path = base_path / "annotations"


def annotation_file(annotation_id):
    return (annotations_path / "{a}.json".format(a=annotation_id))


def all_annotations():
    ret = {}
    for p in annotations_path.glob('*.json'):
        annotation_id = p.name.rsplit('.', 1)[0]
        with p.open('r') as f:
            ret[annotation_id] = json.load(f)
    return ret


def get_annotation(annotation_id):
    with annotation_file(annotation_id).open('r') as f:
        return json.load(f)


def save_annotation(annotation_id, data):
    with annotation_file(annotation_id).open('w') as f:
        json.dump(data, f)


def annotation_exists(annotation_id):
    return annotation_file(annotation_id).exists()


def mturk_annotation(batch, assignment_id):
    df = pd.read_csv(str(next(mturk_path.rglob(f"*{batch}*.csv"))))
    df = df[[c for c in df.columns if "Answer." in c or 'Id' in c]]
    df = df.rename(columns={c:c.split('.',1)[1] for c in df.columns if '.' in c}).set_index("AssignmentId")
    ret = get_annotation(df.loc[assignment_id, "id"])
    ret["labels"] = json.loads(df.loc[assignment_id, "events"])
    ret["status"] = df.loc[assignment_id, "status"]
    ret["feedback"] = df.loc[assignment_id, "feedback"]
    return ret