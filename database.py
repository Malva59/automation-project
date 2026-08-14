import json
from pathlib import Path

DATABASE = Path("known_codes.json")


def load_codes():
    if not DATABASE.exists():
        return set()

    try:
        with DATABASE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return set(data)

    except (json.JSONDecodeError, TypeError):
        return set()


def save_codes(codes):
    with DATABASE.open("w", encoding="utf-8") as file:
        json.dump(
            sorted(codes),
            file,
            ensure_ascii=False,
            indent=2
        )


def get_new_codes(game, codes):
    known_codes = load_codes()

    new_codes = []

    for code in codes:
        identifier = f"{game}:{code}"

        if identifier not in known_codes:
            new_codes.append(code)

    return new_codes


def mark_code_as_known(game, code):
    known_codes = load_codes()

    identifier = f"{game}:{code}"

    if identifier not in known_codes:
        known_codes.add(identifier)
        save_codes(known_codes)
