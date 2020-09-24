import json
from pathlib import Path

base_path = Path(__file__).absolute().parent.parent
data_path = base_path / "data"

with (data_path / "resources.json").open('r') as f:
    resources = json.load(f)

with (data_path / "tools.json").open('r') as f:
    tools = json.load(f)

with (data_path / "implicit_ingredients.json").open('r') as f:
    implicit_ingredients = json.load(f)

with (data_path / "time_lengths.json").open('r') as f:
    time_lengths = json.load(f)
