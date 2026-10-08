import json


def load_scenes(path="config/scenes.json"):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["scenes"]


def get_formal_scenes(scenes):
    return [s for s in scenes if s["type"] == "formal"]


def get_practice_scene(scenes):
    for s in scenes:
        if s["type"] == "practice":
            return s
    return None