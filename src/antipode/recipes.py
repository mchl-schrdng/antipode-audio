"""Shared recipe fields, deterministic seeds and named arrangements."""

from copy import deepcopy


RECIPE_FIELDS = {"duration", "layers", "peak_db", "seed", "effects"}
_EVENT_FIELDS = {
    "layer", "start", "duration", "note", "frequency", "note_end", "frequency_end",
    "level_db", "pan", "pan_end", "fade_in", "fade_out", "gesture",
}


def check_fields(value: dict, allowed: set[str], label: str) -> None:
    if not isinstance(value, dict) or any(key not in allowed for key in value):
        raise ValueError(f"{label} must be an object containing only: {', '.join(sorted(allowed))}.")


def checked_seed(seed: int) -> int:
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("seed must be an integer between 0 and 4294967295.")
    return seed


def layer_seed(layer: dict, recipe_seed: int, source_index: int) -> int:
    return checked_seed(layer.get("seed", (recipe_seed + source_index) % 2**32))


def resolve_member(family: dict, member: str) -> dict:
    """Return a standalone recipe. The renderer validates its DSP values as usual.

    A member inherits the base duration and layers. Its optional events each
    play one zero-based source layer, with overrides for that performance.
    """
    check_fields(family, {"base", "members"}, "family")
    base = family.get("base")
    check_fields(base, RECIPE_FIELDS, "family base")
    layers = base.get("layers")
    if ("duration" not in base or not isinstance(layers, list) or not 1 <= len(layers) <= 16
            or not all(isinstance(layer, dict) for layer in layers)):
        raise ValueError("family base requires a duration and 1–16 layer objects.")
    members = family.get("members")
    if not isinstance(members, dict) or not members or not all(isinstance(k, str) and k.strip() for k in members):
        raise ValueError("family members must be an object with nonempty member names.")
    if not isinstance(member, str) or member not in members:
        raise ValueError(f"Unknown family member. Choose from: {', '.join(members)}.")
    arrangement = members[member]
    check_fields(arrangement, {"duration", "events"}, f"member {member!r}")
    recipe = {key: deepcopy(value) for key, value in base.items() if key != "layers"}
    if "duration" in arrangement:
        recipe["duration"] = arrangement["duration"]
    if "events" not in arrangement:
        recipe["layers"] = deepcopy(layers)
        return recipe

    events = arrangement["events"]
    if not isinstance(events, list) or not 1 <= len(events) <= 16:
        raise ValueError("member events must contain 1–16 event objects.")
    seed = checked_seed(base.get("seed", 0))

    recipe["layers"] = []
    for index, event in enumerate(events):
        check_fields(event, _EVENT_FIELDS, f"event {index}")
        source = event.get("layer")
        if type(source) is not int or not 0 <= source < len(layers):
            raise ValueError(f"event {index} must reference a base layer index from 0 to {len(layers) - 1}.")
        layer = deepcopy(layers[source])
        # A static performance edit takes over that control for this event.
        curves = layer.get("automation")
        if isinstance(curves, dict) and curves:
            if "level_db" in event:
                curves.pop("level_db", None)
            if "pan" in curves and ("pan" in event or "pan_end" in event):
                points = curves.pop("pan")
                if "pan" not in event:
                    match points:
                        case [[0, initial_pan], *_]:
                            layer["pan"] = initial_pan
                        case _:
                            raise ValueError("Inherited pan automation must start with [0, pan].")
            if not curves:
                del layer["automation"]
        for hz, note in (("frequency", "note"), ("frequency_end", "note_end")):
            if hz in event and note in event:
                raise ValueError(f"event {index} must specify either {hz} or {note}, not both.")
            if hz in event:
                layer.pop(note, None)
            if note in event:
                layer.pop(hz, None)
        layer.update({key: value for key, value in event.items() if key != "layer"})
        # The renderer normally derives the seed from the layer index. Anchor
        # it to the source so that reordering voices preserves their timbre.
        layer["seed"] = layer_seed(layer, seed, source)
        recipe["layers"].append(layer)
    return recipe
