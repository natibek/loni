from functools import lru_cache

@lru_cache
def calculate_text_size(text: str) -> tuple[int, int]:
    """Calculates the number of rows and columns text would occupy."""

    if not text:
        return (0, 0)

    txt_arr = text.strip().split("\n")
    cols = max(len(line) for line in txt_arr)
    rows = len(txt_arr)

    return (rows, cols)

