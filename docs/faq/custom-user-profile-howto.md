# How to use custom profile

Browsers (Chrome and Firefox) save your personal information such as bookmarks,
passwords and user preferences in a set of files called "custom profile",
which is stored in a separate location from the browser program files.
You can have multiple custom profiles, each containing
a separate set of user information.

You can use command-line switch *(argument, option)* to tell browser
which profile to use.

## Recipe for Chrome

```python
def test_chrome_fresh_profile_simple():
    from selene import browser
    from selenium.webdriver import Chrome, ChromeOptions

    browser_options = ChromeOptions()
    browser_options.add_argument("user-data-dir=D:\_cache\Chrome\Fresh User Data")
    browser_options.add_argument("profile-directory=Default")

    browser.config.driver = Chrome(options=browser_options)

    browser.open("chrome://version/")
    browser.quit()
```

## Recipe for Firefox

```python
def test_firefox_existing_profile():
    from selene import browser
    from selenium.webdriver import Firefox, FirefoxOptions

    browser_options = FirefoxOptions()
    browser_options.add_argument("-profile")
    browser_options.add_argument("/home/user/snap/firefox/common/.mozilla/firefox/t2y46pn0.default")

    browser.config.driver = Firefox(options=browser_options)

    browser.open("about:profiles")
    browser.quit()
```

## What's about Safari?

Safari browser doesn't appear to support multiple profiles.

## Details on Chrome

The custom profile in Chrome is also called *"user data directory"*.
Profiles are ideal when you want to:

- Share browser settings with multiple people (team members).
- Keep your different test accounts separate.

### Change User Data location

According to [ChromeDriver documentation][doc-chromedriver-capabilities] page:

> By default, ChromeDriver will create a new temporary profile for each session.
you can use the `user-data-dir` Chrome command-line switch
to tell Chrome which profile to use:
>
> ```python
> from selenium.webdriver import ChromeOptions
>
> options = ChromeOptions()
> options.add_argument("user-data-dir=/path/to/your/custom/profile")
> ```
>
> You can create your own custom profile by just running Chrome
(on the command-line or through ChromeDriver)
with the `user-data-dir` switch set to some new directory.
If the path doesn't exist, Chrome will create a new profile
in the specified location. You can then modify the profile settings
as desired, and ChromeDriver can use the profile in the future.
Open chrome://version in the browser to see what profile Chrome is using.

Thus, to run webdriver with a brand new profile
you should specify another User Data directory on your computer:

```python
def test_chrome_fresh_profile_with_path():
    from pathlib import Path
    from selene import browser
    from selenium.webdriver import Chrome, ChromeOptions

    user_data = Path().home() / "my home profile"
    profile_dir = "Default"

    browser_options = ChromeOptions()
    browser_options.add_argument(f"user-data-dir={user_data}")
    browser_options.add_argument(f"profile-directory={profile_dir}")

    browser.config.driver = Chrome(options=browser_options)

    browser.open("chrome://version/")
    browser.quit()
```

This repeats default behavior for new ChromeDriver session,
but here we know exactly where the User Data directory will be created.
It might be useful in rare cases.

We recommend you to use
[Path][pathlib-path] class of [pathlib][python-pathlib] module
*(especially in Python 3.6+)* for work with local paths.
It lets you forget about slashes on different platforms,
write more concise code, and do basic filesystem operations
(writing / reading files, creating folders,
resolve symlinks, work with relative paths, glob files and folders, etc.).

<!-- markdownlint-disable MD046 -->
??? note "Path class drawbacks"

    While the **Path** is a great choice for local files and modern Python.
    It has some disadvantages:

    - does not support cloud storage paths (such as `gc://` or `s3://`)
    
    - has no equivalents for `shutil` functions, `os.chdir`, `os.walk` and
    `relpath` from os.path
    - performance issues (when you operate with thousands of Path objects)
<!-- markdownlint-enable MD046 -->

### Use existing profile

You can copy your existing User Data directory *(with all profiles in it)*,
and use them on another computer, with another browser version,
recovery after system crash, etc.

Therefore, you can create and modify your profile in advance
and then use it in tests. If you don't know how to add a new profile in Chrome,
please refer to ["Use Chrome with multiple profiles"][profiles-chrome-support]
support page. The default location of the User Data directory for different OS:

- Windows: `%LOCALAPPDATA%\Google\Chrome\User Data`
- Linux: `~/.config/google-chrome`
- Mac OS X: `~/Library/Application Support/Google/Chrome`

Generally it varies by OS platform, branding, and release channel.
For more details, please go to Chromium's
["User Data Directory"][user-data-dir-chromium] document.

The first *(default)* profile in Chrome is a subdirectory
(often `Default`) within the user data directory.
If you have **only one** default profile,
you can omit `profile-directory` argument (switch).

```python
# You can omit this line for a single profile
browser_options.add_argument("profile-directory=Default")
```

When you create a new profile the subfolder "Profile N"
is created in User Data directory.
Where N is consecutive number, i.e. 2, 3, 4, and so on.
When folder has been created you cannot change its name via Chrome GUI.

**Important:** When you have multiple profiles you ==have to== specify
which profile to use for webdriver session
via the `user-data-dir` switch.

Let's assume you have pre-configured profiles,
which placed on relative path to your test file,
something like this:

```plain
📁 tests/
├── 📁 test-data
    └── 📁 profiles
        ├── 📁 Default
        └── 📁 Profile 2
└── 📁 some-feature
    └── 📄 web_ui_tests.py
```

Then, you can easily move your `tests` folder and run tests anywhere.

```python
# in 'web_ui_tests.py' file
def test_chrome_second_profile():
    from pathlib import Path
    from selene import browser
    from selenium.webdriver import Chrome, ChromeOptions

    user_data = Path(__file__).parent.parent / "test-data" / "profiles"
    profile_dir = "Profile 2"

    browser_options = ChromeOptions()
    browser_options.add_argument(f"user-data-dir={user_data}")
    browser_options.add_argument(f"profile-directory={profile_dir}")

    browser.config.driver = Chrome(options=browser_options)

    browser.open("chrome://version/")
    browser.quit()
```

<!-- markdownlint-disable MD046 -->
!!! tip "How to know the name of profile folder?"

    1. Open browser with desired profile
    *(for a non-default location, use the same user data path
    for the command-line switch `--user-data-dir "/path/to/user data"`)*
    2. Navigate to `chrome://version`
    3. Look for the **Profile Path** field.
    This gives the path to the profile directory.
<!-- markdownlint-enable MD046 -->

**Security Note:** Share test profiles carefully, someone can get access
to your sensitive information. Don't forget to delete profile folder manually,
after you remove that profile in Chrome's profile manager.

### Arguments syntax

You should always bear in mind the context of using command-line
options (switches) for Chrome: Selenium tests or shell (terminal) commands.
**ChromeOptions** class let you simplify the syntax of passed
command-line arguments and it cares about quoting white spaces.

Here are some tips for using arguments in tests:

- It does not matter - with double dash (hyphens) `--` or without.

    These two method calls are valid and equivalent:

    `.add_argument("user-data-dir=D:\_cache\Chrome\Fresh User Data")`  
    `.add_argument("--user-data-dir=D:\_cache\Chrome\Fresh User Data")`

    The same for `profile-directory` argument and others.

- Slash `/` and backslash `\` in paths are interchangeable on Windows hosts.
    Forward slashes `/` are also valid on Windows
    *(at least with modern version of Python and Windows 10, 11)*

    These three method calls are valid and equivalent on Windows:

    `.add_argument("user-data-dir=D:/_cache/Chrome/Fresh User Data")`  
    `.add_argument("user-data-dir=D:\_cache\Chrome\Fresh User Data")`
    `.add_argument("user-data-dir=D:\\_cache\\Chrome\\Fresh User Data")`

    DO NOT USE backslash `\` on Linux hosts,
    because it's valid character for filepath there.

- Do NOT quote white spaces

    <!-- markdownlint-disable MD046 -->
    !!! success "GOOD"

        ```python
        .add_argument("user-data-dir=D:\_cache\Chrome\Fresh User Data")
        .add_argument("profile-directory=Profile 2")
        ```

    !!! failure "BAD"

        ```python
        .add_argument('user-data-dir="D:\_cache\Chrome\Fresh User Data"')
        .add_argument('profile-directory="Profile 2"')
        ```
    <!-- markdownlint-enable MD046 -->

- Do NOT add `Default` subfolder at the end of user data directory

    <!-- markdownlint-disable MD046 -->
    !!! success "GOOD"

        ```python
        .add_argument("user-data-dir=D:\_cache\Chrome\Fresh User Data")
        .add_argument("profile-directory=Default")
        ```

    !!! failure "BAD"

        ```python
        .add_argument("user-data-dir=D:\_cache\Chrome\Fresh User Data\Default")
        ```
    <!-- markdownlint-enable MD046 -->

## Details on Firefox

Managing profiles in Firefox is more tricky than in Chrome.
Read more about that on ["Profile Manager"][firefox-profile-manager] page.
Nevertheless, custom profiles are also available for us.

### Use existing profile by path

To work with Firefox profile we must know its path
(where it's located). In Firefox browser:

1. Navigate to `about:profiles` internal page.
2. Search your profile on the page.
3. Look for the **Root Directory** field.
This gives the path to the profile directory.
4. Copy or note down path value.

Command-line argument `-profile "profile_path"` is intended for start Firefox
with the profile with the given path.
Let's look how to use this switch in test,
assuming that we know the path to existing default profile on Ubuntu OS
and run our test in terminal via pytest runner
*(not from VS Code or PyCharm)*:

```python
def test_firefox_existing_profile():
    from pathlib import Path
    from selene import browser
    from selenium.webdriver import Firefox, FirefoxOptions

    profile_dir = Path().home() / "snap/firefox/common/.mozilla/firefox/t2y46pn0.default"

    browser_options = FirefoxOptions()
    browser_options.add_argument("-profile")
    browser_options.add_argument(f"{profile_dir}")

    browser.config.driver = Firefox(options=browser_options)

    browser.open("about:profiles")
    browser.quit()
```

Pay attention that we called .add_argument() twice for Firefox browser
and imported respective classes: **Firefox** and **FirefoxOptions**.

<!-- markdownlint-disable MD046 -->
!!! note "About argument syntax in Firefox"

    Unlike Chrome, we have to pass `-profile` exactly *(with single dash (hyphen))*.
    As for the paths, we can also write them with forward slash `/` or
    double backslash `\\` on Windows. But DO NOT USE backslashes on Linux hosts as well.
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? tip "Run snap-based Firefox from VS Code and PyCharm"

    Firefox installed via snap on Ubuntu 22.04 fails to start,
    when you try to run a Selenium test from another snap app
    (such as VS Code or PyCharm).

    One way to workaround this problem is specifying exact path
    to `firefox` and `geckodriver` executable files:

    ```python
    def test_snap_firefox_existing_profile_on_ubuntu():
        from pathlib import Path
        from selene import browser
        from selenium.webdriver import Firefox, FirefoxOptions
        from selenium.webdriver.firefox.service import Service

        install_dir = Path("/snap/firefox/current/usr/lib/firefox")
        driver_loc = install_dir / "geckodriver"
        binary_loc = install_dir / "firefox"

        profile_dir = Path().home() / "snap/firefox/common/.mozilla/firefox/t2y46pn0.default"

        browser_options = FirefoxOptions()
        browser_options.add_argument("-profile")
        browser_options.add_argument(f"{profile_dir}")

        fire_service = Service(driver_loc)
        browser_options.binary_location = f"{binary_loc}"
        browser.config.driver = Firefox(
            service=fire_service,
            options=browser_options,
        )

        browser.open("about:profiles")
        browser.quit()
    ```

    This is "Path version" of the solution from this
    [comment][snap-firefox-comment].
    This workaround has a strange side effect: coping profile and cache data
    into `~/.mozilla/firefox/` and `~/.cache/mozilla/firefox` directories.
    In any cae, it's better than a failure during browser start.

    [snap-firefox-comment]: https://github.com/SeleniumHQ/selenium/issues/11414#issuecomment-136673035
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? warning "Argument -P "profile_name" does not work with webdriver"

    Unfortunately, you can use this argument only in terminal modifying your profile
    to use it in the future. At the moment, you can't use profile by name in tests.
<!-- markdownlint-enable MD046 -->

### Use empty profile

If you need profile with default settings and don't want to create it via Profile Manager,
you can specify empty folder that has write permissions.
This folder must be created **before** you run the test. For example, this might be:

```python
new_dir = Path().home() / "Desktop/New Dir"
new_dir.mkdir(parents=True, exist_ok=True)
browser_options.add_argument(f"{new_dir}")
```

As mentioned above, this profile won't be listed with other existing profiles,
but you can open Firefox with it and modify the profile settings from terminal
specifying the same command-line switches (arguments).

## Troubleshooting

In this section we'll list most common exceptions (errors)
that you might have, running Selenium tests with browser profiles,
possible causes of errors and how to fix them.

### DevToolsActivePort file doesn't exist

{==

selenium.common.exceptions.WebDriverException:  
Message: unknown error: Chrome failed to start: exited normally.  
(unknown error: DevToolsActivePort file doesn't exist)

==}

If a browser does not start at all,
then you have specified the `--profile-directory` that does not exist.
*Check profile directory name and argument syntax.*  
If a browser starts and closes with this exception,
then the same profile is opened in another window.
*Close all windows that use this profile and try again.*

### Could not remove old devtools port file

{==

selenium.common.exceptions.WebDriverException:  
Message: unknown error: Could not remove old devtools port file.  
Perhaps the given user-data-dir at "path/to/user data"
is still attached to a running Chrome or Chromium process.

==}

Unnecessary quoting of white spaces in user data directory path
(invalid path in general). *Check syntax in arguments*.  
The same profile is opened in another window.
*Close all windows that use this profile and try again.*

### Cannot create default profile directory

{==

selenium.common.exceptions.WebDriverException:  
Message: unknown error: cannot create default profile directory

==}

Chrome can't create folder (no write permissions).
*Specify the user data directory in a less restrictive location or
grant permissions for `chromedriver` executable and `google-chrome` itself*.

### Unable to discover open pages

{==

selenium.common.exceptions.WebDriverException:  
Message: unknown error: unable to discover open pages

==}

Usually, the window for choosing profile is displayed
(when multiple profiles exist).
*Don't forget to specify `profile-directory` in that case
(especially for Default profile folder)*

### Unable to write Firefox profile

{==

selenium.common.exceptions.SessionNotCreatedException:  
Message: Failed to set preferences: Unable to write Firefox profile:
The system cannot find the path specified. (os error 3)

==}

Profile folder for Firefox does not exist or has no write permissions.
*Try to create this folder in advance.
Specify the profile directory in a less restrictive location or
grant permissions for `geckodriver` executable and `firefox` itself*.  
&nbsp;

<!-- markdownlint-disable MD046 -->
??? abstract "Environment and package versions used for writing examples"

    ```plain
    python = "3.10"
    selene = "2.0.0b17"
    pytest = "7.2.1"
    selenium = "4.8.2"

    chromedriver = "110.0.5481"
    geckodriver = "0.32.2"

    Windows 10 x64 Version 22H2
    Ubuntu 22.04.2 LTS (with snap-packaged Firefox)
    VS Code 1.76
    ```
<!-- markdownlint-enable MD046 -->

<!-- References -->
[doc-chromedriver-capabilities]: https://chromedriver.chromium.org/capabilities
[profiles-chrome-support]: https://support.google.com/chrome/answer/2364824?hl
[user-data-dir-chromium]: https://github.com/chromium/chromium/blob/main/docs/user_data_dir.md
[pathlib-path]: https://docs.python.org/3/library/pathlib.html#pathlib.Path
[python-pathlib]: https://docs.python.org/3/library/pathlib.html
[firefox-profile-manager]: https://support.mozilla.org/en-US/kb/profile-manager-create-remove-switch-firefox-profiles
