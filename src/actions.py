import json
from dataclasses import dataclass
from copy import deepcopy
from pathlib import Path
from pprint import pp
import collections
from datetime import datetime
from operator import itemgetter as at
from enum import Enum
from typing import List

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

IMMEDIATE = "LIMMEDIATE"
ingredient_dict = {k: v for k, v in ingredients}
resource_dict = {k: v for k, v in resources}


@dataclass
class Instruction:
    ts: int
    command: str
    ingredient: str
    resource: str


class AssignedTypes(Enum):
    Ingredient = 0
    UnlistedIngredient = 1
    TimeLength = 2
    Tool = 3

    @classmethod
    def parse(cls, ing_id):
        return {
            "I": AssignedTypes.Ingredient,
            "M": AssignedTypes.UnlistedIngredient,
            "L": AssignedTypes.TimeLength,
            "T": AssignedTypes.Tool,

        }[ing_id[0]]


def handle_instruction_label(lst):
    events = list(map(at("start", "end", "action", "resource"), lst))
    ret = collections.defaultdict(list)
    for start, end, action, resource in events:
        start = (datetime.strptime(start, "%Y-%m-%dT00:00:00") - datetime(2020, 1, 1)).days
        end = (datetime.strptime(end, "%Y-%m-%dT00:00:00") - datetime(2020, 1, 1)).days
        for i in range(start, end):
            ret[i].append((resource, action))
    # Add "LIMMEDIATE" if no time duration specified
    for lst in ret.values():
        has_time_duration_map = collections.defaultdict(bool)
        for res, action in lst:
            has_time_duration_map[res] |= AssignedTypes.parse(action) == AssignedTypes.TimeLength
        for res, has_time_duration in has_time_duration_map.items():
            if not has_time_duration:
                lst.append((res, IMMEDIATE))
            lst.sort()

    return dict(ret)


def program_step(annotation)->List[Instruction]:
    max_ts = max(map(int, annotation.keys()))
    new_state = None
    state = {res: set() for res in resource_dict}
    for resource, ing in annotation.get("0", annotation.get(0)):
        state[resource].add(ing)
    actions = []
    for ts in range(1, 1 + max_ts):
        new_state = {res: set() for res in resource_dict}
        for resource, ing in annotation.get(str(ts), annotation.get(ts)):
            new_state[resource].add(ing)
        for resource in new_state.keys():
            added_ings = new_state[resource] - state[resource]
            removed_ings = state[resource] - new_state[resource]
            for ing in added_ings:
                ing_type = AssignedTypes.parse(ing)
                if ing_type==AssignedTypes.TimeLength:
                    if ing != IMMEDIATE:
                        actions.append(Instruction(ts, "chef_check", ing, resource))
                elif ing_type==AssignedTypes.Tool:
                    actions.append(Instruction(ts, "use", ing, resource))
                elif resource != "A1":
                    actions.append(Instruction(ts, "put", ing, resource))
            for ing in removed_ings:
                ing_type = AssignedTypes.parse(ing)
                if resource.startswith("A"):
                    continue
                if ing_type==AssignedTypes.Ingredient or ing_type==AssignedTypes.UnlistedIngredient:
                    actions.append(Instruction(ts, "remove", ing, resource))
                elif ing_type==AssignedTypes.Tool:
                    actions.append(Instruction(ts, "stop_using", ing, resource))
        state = deepcopy(new_state)
    for res in resource_dict:
        for ts in range(1, 1 + max_ts):
            before = {a.ingredient for a in actions if a.ts < ts and a.command == "put" and a.resource == res and AssignedTypes.parse(a.ingredient) == AssignedTypes.Ingredient}
            after = {a.ingredient for a in actions if a.ts == ts and a.command == "remove" and a.resource == res and AssignedTypes.parse(a.ingredient) == AssignedTypes.Ingredient}
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
        "stop_using",
        "put",
        "chef_check",
    ]
    actions = sorted(actions, key=lambda t: (t.ts, action_order.index(t.command)))
    return actions


def program(annotation, verbose=False)->List[Instruction]:
    """Runs program_step for each item in list, and fix timestamps"""
    # Union all steps, and align timestamps
    if 'labels' in annotation:
        annotation = [handle_instruction_label(l) for l in annotation['labels']]
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
