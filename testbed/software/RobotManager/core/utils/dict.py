def flatten_dict(data: dict, indent: int = 0) -> list[tuple[str, str]]:
    """
    Recursively flatten a dictionary into a list of (key, value) tuples.
    The key is indented by two spaces per level. If a value is a dict, the key
    is shown with an empty value, and its contents are flattened below.
    Lists are displayed as a comma-separated list inside square brackets.
    """
    rows = []
    for key, value in data.items():
        prefix = "  " * indent + str(key)
        if isinstance(value, dict):
            rows.append((prefix, ""))
            rows.extend(flatten_dict(value, indent=indent + 1))
        elif isinstance(value, list):
            rows.append((prefix, "[" + ", ".join(str(x) for x in value) + "]"))
        else:
            rows.append((prefix, str(value)))
    return rows