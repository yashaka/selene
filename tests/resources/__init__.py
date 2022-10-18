from pathlib import Path


def path(relative: str):
    return str(Path(__file__).parent.joinpath(relative).absolute())


def url(relative_path: str):
    return f'file://{path(relative_path)}'
