import os

_cache = {}


def find_asset(filename, root="assets"):
    if filename in _cache:
        return _cache[filename]

    for folder, _, files in os.walk(root):
        if filename in files:
            path = os.path.join(folder, filename)
            _cache[filename] = path
            return path

    raise FileNotFoundError(
        f"'{filename}' was not found anywhere inside the '{root}' folder"
    )


IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")


def find_asset_like(keyword, root="assets"):
    keyword = keyword.lower()

    for folder, _, files in os.walk(root):
        for name in sorted(files):
            if keyword in name.lower() and name.lower().endswith(IMAGE_EXTS):
                return os.path.join(folder, name)

    return None