from urllib.parse import urlparse

# Known color words and modifiers (keep in sync with scripts/group_by_color.py)
COLORS = {
    'black', 'white', 'grey', 'gray', 'blue', 'navy', 'green', 'red', 'pink', 'beige',
    'burgundy', 'ecru', 'brown', 'camel', 'cream', 'tan', 'yellow', 'orange', 'purple', 'khaki',
    'ivory', 'stone', 'leopard'
}
MODIFIERS = {'light', 'dark'}

# Mapping for material/color tokens to normalized label
NORMALIZE = {
    'au': 'gold',
    'ag': 'silver',
    'gold': 'gold',
    'silver': 'silver',
    'rose-gold': 'rose gold',
    'rosegold': 'rose gold',
}


def infer_color_from_url(url: str) -> str:
    """Infer a simple color label from a product URL slug.

    Returns a lower-case string like 'light blue', 'burgundy' or 'unknown'.
    """
    try:
        p = urlparse(url)
        path = p.path or ''
        parts = [seg for seg in path.split('/') if seg]
        if not parts:
            return 'unknown'
        slug = parts[-1]
        tokens = slug.split('-')

        norm_tokens = [NORMALIZE.get(tok, tok) for tok in tokens]

        for i, tok in enumerate(norm_tokens):
            if tok in MODIFIERS and i + 1 < len(norm_tokens) and norm_tokens[i + 1] in COLORS.union(set(NORMALIZE.values())):
                return f"{tok} {norm_tokens[i + 1]}"

        for tok in norm_tokens:
            if tok in NORMALIZE.values() or tok in COLORS:
                return tok

        if 'light' in norm_tokens:
            return 'white'
        if 'dark' in norm_tokens:
            return 'black'

        for tok in tokens:
            if any(c in tok for c in ('blue', 'grey', 'gray', 'black', 'white', 'green', 'red', 'ecru', 'burgundy')):
                return tok

        return 'unknown'
    except Exception:
        return 'unknown'
