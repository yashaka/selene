def pytest_addoption(parser):

    parser.addoption(
        '--headless',
        help='headless mode',
        default=False,
    )
