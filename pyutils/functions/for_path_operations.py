from pathlib import Path


def validate_go_up(path: Path, levels: int) -> None:
    "Validation for the go_up function"

    # sentinels
    if not isinstance(path, Path):
        raise TypeError(f"The provided {path=} isn't of type Path")

    if not path.exists():
        raise ValueError("The provided path doesn't exist")

    if levels < 0:
        raise ValueError("The provided number of levels must be positive")


def go_up(path: Path, levels: int) -> Path:
    "The function goes up to the path tree with given number of levels"
    validate_go_up(path, levels)

    return path if levels == 0 else go_up(path.parent, levels - 1)
