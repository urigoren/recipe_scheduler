import json
from dataclasses import dataclass
from copy import deepcopy
from pathlib import Path
from pprint import pp

base_path = Path(__file__).absolute().parent.parent
annot_path = base_path / "annotations"
data_path = base_path / "data"
preprocessed_path = base_path / "preprocessed"

with (preprocessed_path / "ingredients.json").open("r") as f:
    ingredients = json.load(f)
with (preprocessed_path / "labels.json").open("r") as f:
    idx2label = [tuple(t) for t in json.load(f)]
    label2idx = {r: i for i, r in enumerate(idx2label)}
with (preprocessed_path / "resources.json").open("r") as f:
    resources = json.load(f)
ingredient_dict = {k: v for k, v in ingredients}
resource_dict = {k: v for k, v in resources}


@dataclass
class Instruction:
    ts: int
    command: str
    ingredient: str
    resource: str


def program_step(annotation):
    max_ts = max(map(int, annotation.keys()))
    new_state = None
    state = {res: set() for res in resource_dict}
    for resource, ing in annotation["0"]:
        state[resource].add(ing)
    actions = []
    for ts in range(1, 1 + max_ts):
        new_state = {res: set() for res in resource_dict}
        for resource, ing in annotation[str(ts)]:
            new_state[resource].add(ing)
        for resource in new_state.keys():
            added_ings = new_state[resource] - state[resource]
            removed_ings = state[resource] - new_state[resource]
            for ing in added_ings:
                if ing.startswith("L"):
                    if ing != "LIMMEDIATE":
                        actions.append(Instruction(ts, "chef_check", ing, resource))
                elif ing.startswith("T"):
                    actions.append(Instruction(ts, "use", ing, resource))
                elif resource != "A1":
                    actions.append(Instruction(ts, "put", ing, resource))
            for ing in removed_ings:
                if not ing.startswith("L") and not resource.startswith("A"):
                    actions.append(Instruction(ts, "remove", ing, resource))
        state = deepcopy(new_state)
    for res in resource_dict:
        for ts in range(1, 1 + max_ts):
            before = {a.ingredient for a in actions if a.ts < ts and a.command == "put" and a.resource == res and a.ingredient.startswith("I")}
            after = {a.ingredient for a in actions if a.ts == ts and a.command == "remove" and a.resource == res and a.ingredient.startswith("I")}
            new_res = {a.resource for a in actions if a.ts == ts and a.command == "put" and a.resource != res and a.ingredient in {b for b in before}}
            if len(new_res) != 1:
                continue
            new_res = list(new_res)[0]
            if before <= after:
                actions.append(Instruction(ts, "move_contents", res, new_res))
                actions = [a for a in actions if not (a.ts == ts and (a.command, a.resource) in {("remove", res), ("put", new_res)} and a.ingredient in before)]

    action_order = [
        "move_contents",
        "remove",
        "use",
        "put",
        "chef_check",
    ]
    actions = sorted(actions, key=lambda t: (t.ts, action_order.index(t.command)))
    return actions


def program(annotation, verbose=False):
    """Runs program_step for each item in list, and fix timestamps"""
    # Union all steps, and align timestamps
    actions = []
    ts = 0
    for a in annotation:
        p = program_step(a)
        if len(p) == 0:
            continue
        for instruction in p:
            instruction.ts += ts
        actions.extend(p)
        ts = p[-1].ts
    #
    # Vebose
    if verbose:
        actions = [
            (
                a.ts,
                a.command,
                ingredient_dict.get(a.ingredient, resource_dict.get(a.ingredient, "")),
                resource_dict.get(a.resource),
            )
            for a in actions
        ]
    return actions


def main(args):
    with (data_path / "annotaions.json").open('r') as f:
        annotations = json.load(f)
    pp(program(annotations[args.annotation_id], verbose=args.verbose))
    return 0


if __name__ == "__main__":
    import sys
    from argparse import ArgumentParser
    parser = ArgumentParser(description=main.__doc__)
    parser.add_argument('annotation_id', type=str, help='annotation id')
    parser.add_argument('--verbose', dest='verbose', action='store_true')
    parser.set_defaults(verbose=False)

    sys.exit(main(parser.parse_args()))
