import json
from pathlib import Path

base_path = Path(__file__).absolute().parent.parent
data_path = base_path / "data"

resources = [
    {"name": "Serve", "id": "SERVE", "merger":  False, "frozen": "top"},
    {"name": "Beaker1", "id": "ONE", "merger":  True},
    {"name": "Beaker2", "id": "TWO", "merger":  True},
    {"name": "Beaker3", "id": "THREE", "merger":  True},
    {"name": "Beaker4", "id": "FOUR", "merger":  True},
    {"name": "Beaker5", "id": "FIVE", "merger":  True},
    {"name": "Beaker6", "id": "SIX", "merger":  True},
    {"name": "Beaker7", "id": "SEVEN", "merger":  True},
    {"name": "Trash Bin", "id": "TRASH"},
    {
        "name": "Validation", "id": "VALID", "expanded": False, "children": [
            {"name": "Unused", "id": "VALID_UNUSED", "merger":  False},
            {"name": "Mixture 1", "id": "VALID_MIX1", "merger":  False},
            {"name": "Mixture 2", "id": "VALID_MIX2", "merger":  False},
            {"name": "Mixture 3", "id": "VALID_MIX3", "merger":  False},
            {"name": "Mixture 4", "id": "VALID_MIX4", "merger":  False},
            {"name": "Mixture 5", "id": "VALID_MIX5", "merger":  False}

        ]
    }
]

tools = {'TOO': 'Orange',
 'TPP': 'Purple',
 'TYY': 'Yellow',
 'TBB': 'Blue',
 'TGG': 'Green',
 'TRR': 'Red'}
tool_containers = []
time_lengths = {'LOOO': 'Orange',
 'LPPP': 'Purple',
 'LYYY': 'Yellow',
 'LBBB': 'Blue',
 'LGGG': 'Green',
 'LRRR': 'Red'}
commands = []

ingredients = {'IO': 'Orange',
 'IP': 'Purple',
 'IY': 'Yellow',
 'IB': 'Blue',
 'IG': 'Green',
 'IR': 'Red'}

activities = {}

def reload():
    with (data_path / "commands.json").open('r') as f:
        commands = json.load(f)
reload()
