import unicodedata
from urllib.parse import unquote


PREFERRED_NAME_BYTES = 240
FILESYSTEM_NAME_BYTES = 255
MAX_PRESERVED_EXTENSION_BYTES = 32


def sanitize_original_name(raw_name: str) -> str:
    decoded = unquote(raw_name).replace("\\", "/")
    basename = decoded.rsplit("/", 1)[-1]
    without_controls = "".join(
        character for character in basename if not unicodedata.category(character).startswith("C")
    )
    cleaned = without_controls.strip().strip(".").strip() or "untitled"
    stem, extension = _split_extension(cleaned)
    if extension:
        stem = _utf8_prefix(stem, PREFERRED_NAME_BYTES - len(extension.encode("utf-8")))
        return f"{stem}{extension}" if stem else _utf8_prefix(cleaned, PREFERRED_NAME_BYTES)
    return _utf8_prefix(cleaned, PREFERRED_NAME_BYTES) or "untitled"


def collision_name(preferred_name: str, index: int) -> str:
    if index == 0:
        return _utf8_prefix(preferred_name, FILESYSTEM_NAME_BYTES)
    marker = f"_{index:03d}"
    stem, extension = _split_extension(preferred_name)
    available = FILESYSTEM_NAME_BYTES - len(marker.encode("utf-8")) - len(extension.encode("utf-8"))
    shortened_stem = _utf8_prefix(stem, available)
    return f"{shortened_stem}{marker}{extension}"


def _split_extension(name: str) -> tuple[str, str]:
    period = name.rfind(".")
    if period <= 0:
        return name, ""
    extension = name[period:]
    if len(extension.encode("utf-8")) > MAX_PRESERVED_EXTENSION_BYTES:
        return name, ""
    return name[:period], extension


def _utf8_prefix(value: str, byte_limit: int) -> str:
    used = 0
    output: list[str] = []
    for character in value:
        width = len(character.encode("utf-8"))
        if used + width > byte_limit:
            break
        output.append(character)
        used += width
    return "".join(output)
