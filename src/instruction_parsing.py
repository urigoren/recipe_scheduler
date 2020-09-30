import json
from dataclasses import dataclass
from copy import deepcopy
from pathlib import Path
from pprint import pp
import collections
from datetime import datetime
from operator import itemgetter as at
from enum import Enum
from typing import List, Dict, Set

base_path = Path(__file__).absolute().parent.parent
data_path = base_path / "data"

IMMEDIATE = "LIMMEDIATE"

with (data_path / "resources.json").open('r') as f:
    resource_dict = json.load(f)
    resource_dict = {res["id"]: res_category["name"] + "/" + res["name"] for res_category in resource_dict for res in
                     res_category["children"]}


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


class Commands(Enum):
    """Must be in-sync with commands.json"""
    PUT = 0
    REMOVE = 1
    USE = 2
    STOP_USING = 3
    CHEF_CHECK = 4
    MOVE_CONTENTS = 5


@dataclass
class Instruction:
    ts: int
    command: Commands
    ingredient: str
    resource: str


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


def program_step(annotation) -> List[Instruction]:
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
                if ing_type == AssignedTypes.TimeLength:
                    if ing != IMMEDIATE:
                        actions.append(Instruction(ts, Commands.CHEF_CHECK, ing, resource))
                elif ing_type == AssignedTypes.Tool:
                    actions.append(Instruction(ts, Commands.USE, ing, resource))
                elif resource != "A1":
                    actions.append(Instruction(ts, Commands.PUT, ing, resource))
            for ing in removed_ings:
                ing_type = AssignedTypes.parse(ing)
                if resource.startswith("A"):
                    continue
                if ing_type == AssignedTypes.Ingredient or ing_type == AssignedTypes.UnlistedIngredient:
                    actions.append(Instruction(ts, Commands.REMOVE, ing, resource))
                elif ing_type == AssignedTypes.Tool:
                    actions.append(Instruction(ts, Commands.STOP_USING, ing, resource))
        state = deepcopy(new_state)
    for res in resource_dict:
        for ts in range(1, 1 + max_ts):
            before = {a.ingredient for a in actions if
                      a.ts < ts and a.command == Commands.PUT and a.resource == res and AssignedTypes.parse(
                          a.ingredient) == AssignedTypes.Ingredient}
            after = {a.ingredient for a in actions if
                     a.ts == ts and a.command == Commands.REMOVE and a.resource == res and AssignedTypes.parse(
                         a.ingredient) == AssignedTypes.Ingredient}
            new_res = {a.resource for a in actions if
                       a.ts == ts and a.command == Commands.PUT and a.resource != res and a.ingredient in {b for b in
                                                                                                           before}}
            if len(new_res) != 1:
                continue
            new_res = list(new_res)[0]
            if before <= after:
                actions.append(Instruction(ts, Commands.MOVE_CONTENTS, res, new_res))
                actions = [a for a in actions if not (a.ts == ts and (a.command, a.resource) in {(Commands.REMOVE, res),
                                                                                                 (Commands.PUT,
                                                                                                  new_res)} and a.ingredient in before)]

    action_order = [
        Commands.MOVE_CONTENTS,
        Commands.REMOVE,
        Commands.USE,
        Commands.STOP_USING,
        Commands.PUT,
        Commands.CHEF_CHECK,
    ]
    actions = sorted(actions, key=lambda t: (t.ts, action_order.index(t.command)))
    return actions


def program(annotation) -> List[Instruction]:
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
    return actions


def execute(ingredients:List[str], instructions: List[Instruction])->List[Dict[str, Set[str]]]:
    return


def main(args):
    with (data_path / "annotaions.json").open('r') as f:
        annotations = json.load(f)
    pp(program(annotations[args.annotation_id]))
    return 0


if __name__ == "__main__":
    import sys
    from argparse import ArgumentParser

    parser = ArgumentParser(description=main.__doc__)
    parser.add_argument('annotation_id', type=str, help='annotation id')

    sys.exit(main(parser.parse_args()))