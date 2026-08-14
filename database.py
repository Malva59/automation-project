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


def get_new_codes(codes):
    known_codes = load_codes()

    new_codes = [
        code for code in codes
        if code not in known_codes
    ]

    # On conserve tous les codes connus + les nouveaux
    all_codes = known_codes.union(codes)

    save_codes(all_codes)

    return new_codes
