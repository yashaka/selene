#

::: selene.core.configuration
    options:
        show_root_toc_entry: False
        members_order: source
        filters:
            - "!_save_screenshot_strategy"
            - "!_save_page_source_strategy"
            - "!_build_local_driver_by_name_or_remote_by_url_and_options"
            - "!_maybe_reset_driver_then_tune_window_and_get_with_base_url"
            - "!_DriverStrategiesExecutor"
            - "!_ManagedDriverDescriptor"
            - "!browser_name"
            - "!_inject_screenshot_and_page_source_pre_hooks"
            - "!_generate_filename"
            - "!wait"

<!-- markdownlint-disable MD001 -->
### _save_screenshot_strategy

Defines a strategy for saving a screenshot.

The default strategy saves a screenshot to a file,
and stores the path to `config.last_screenshot`.

```python
_save_screenshot_strategy: Callable[
    [Config, Optional[str]], Any
] = lambda config, path=None: fp.thread(
    path,
    lambda path: (
        config._generate_filename(suffix='.png') if path is None else path
    ),
    lambda path: (
        os.path.join(path, f'{next(config._counter)}.png')
        if path and not path.lower().endswith('.png')
        else path
    ),
    fp.do(
        fp.pipe(
            os.path.dirname,
            lambda folder: (
                os.makedirs(folder)
                if folder and not os.path.exists(folder)
                else ...
            ),
        )
    ),
    fp.do(
        lambda path: (
            warnings.warn(
                'name used for saved screenshot does not match file '
                'type. It should end with an `.png` extension',
                UserWarning,
            )
            if not path.lower().endswith('.png')
            else ...
        )
    ),
    lambda path: (path if config.driver.get_screenshot_as_file(path) else None),
    fp.do(
        lambda path: setattr(config, 'last_screenshot', path)
    ),
)
```

### _save_page_source_strategy

Defines a strategy for saving a page source on failure.

The default strategy saves a page_source to a file,
and stores the path to `config.last_page_source`.

```python
_save_page_source_strategy: Callable[
    [Config, Optional[str]], Any
] = lambda config, path=None: fp.thread(
    path,
    lambda path: (
        config._generate_filename(suffix='.html') if path is None else path
    ),
    lambda path: (
        os.path.join(path, f'{next(config._counter)}.html')
        if path and not path.lower().endswith('.html')
        else path
    ),
    fp.do(
        fp.pipe(
            os.path.dirname,
            lambda folder: (
                os.makedirs(folder)
                if folder and not os.path.exists(folder)
                else ...
            ),
        )
    ),
    fp.do(
        lambda path: (
            warnings.warn(
                'name used for saved page source does not match file '
                'type. It should end with an `.html` extension',
                UserWarning,
            )
            if not path.lower().endswith('.html')
            else ...
        )
    ),
    lambda path: (path, config.driver.page_source),
    fp.do(lambda path_and_source: fp.write_silently(*path_and_source)),
    lambda path_and_source: path_and_source[0],
    fp.do(
        lambda path: setattr(config, 'last_page_source', path)
    ),
)
```
<!-- markdownlint-enable MD001 -->
