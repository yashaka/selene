from pathlib import Path

# TODOMVC_URL = 'https://todomvc.com/examples/emberjs/'
TODOMVC_URL = 'https://todomvc.com/examples/jquery/dist'


def path(relative: str):
    return str(Path(__file__).parent.joinpath(relative).absolute())


def url(relative_path: str):
    return f'file://{path(relative_path)}'
