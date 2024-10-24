def relative_from_root(path: str):
    from examples.run_cross_platform_android_ios import wikipedia_app_tests
    from pathlib import Path

    return (
        Path(wikipedia_app_tests.__file__)
        .parent.parent.joinpath(path)
        .absolute()
        .__str__()
    )
