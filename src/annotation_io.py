import json
from pathlib import Path

base_path = Path(__file__).absolute().parent.parent
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
