import json
from pathlib import Path

base_path = Path(__file__).absolute().parent.parent
data_path = base_path / "data"

resources = []
tools = {}
activities = {}
time_lengths = {}
commands = []


def reload():
    global resources, tools, activities, time_lengths, ingredients_map, commands
    with (data_path / "resources.json").open('r') as f:
        resources = json.load(f)

    with (data_path / "tools.json").open('r') as f:
        tools = json.load(f)

    with (data_path / "activities.json").open('r') as f:
        activities = json.load(f)

    with (data_path / "time_lengths.json").open('r') as f:
        time_lengths = json.load(f)

    with (data_path / "commands.json").open('r') as f:
        commands = json.load(f)


reload()
