import unicodedata


DEFAULT_EVENT_NAME = "Photo Drop"
MAX_EVENT_NAME_CHARACTERS = 100


def normalize_event_name(value: str | None) -> str:
    candidate = value or ""
    if any(unicodedata.category(character).startswith("C") for character in candidate):
        raise ValueError("Event name cannot contain control characters")
    normalized = " ".join(candidate.split()) or DEFAULT_EVENT_NAME
    if len(normalized) > MAX_EVENT_NAME_CHARACTERS:
        raise ValueError(f"Event name cannot exceed {MAX_EVENT_NAME_CHARACTERS} characters")
    return normalized
