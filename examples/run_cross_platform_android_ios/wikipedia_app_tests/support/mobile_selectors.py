import re
from binascii import Error

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By

from examples.run_cross_platform_android_ios import project


def is_android_id(selector):
    return re.match(r'^[a-zA-Z0-9-_]+(\.[a-zA-Z0-9-_]+)+:id/[a-zA-Z0-9-_]+$', selector)


def is_word_with_dashes_underscores_or_numbers(selector):
    return re.match(r'^[a-zA-Z_\d\-]+$', selector)


def are_words_with_dashes_underscores_or_numbers_separated_by_space(selector):
    return re.match(r'^[a-zA-Z_\d\- ]+$', selector)


def is_xpath_like(selector: str):
    return (
        selector.startswith('/')
        or selector.startswith('./')
        or selector.startswith('..')
        or selector.startswith('(')
        or selector.startswith('*/')
    )


def to_app_package_wise_by(selector: str):
    return AppiumBy.ID, (
        f'{project.config.app_package}:id/{selector}'
        if project.config.app_package
        else selector
    )


def to_by_strategy(selector: str):
    if is_xpath_like(selector):
        return By.XPATH, selector

    # BY EXPLICIT ANDROID ID
    if selector.startswith('#') and is_word_with_dashes_underscores_or_numbers(
        selector[1:]
    ):
        if project.config.context is project.EnvContext.android:
            return to_app_package_wise_by(selector[1:])
        else:
            raise Error(
                f'Unsupported selector: {selector}, for platform: {project.config.context}'
            )

    # BY MATCHED ANDROID ID
    if is_android_id(selector):
        return AppiumBy.ID, selector

    # BY EXACT TEXT
    if (selector.startswith('text="') and selector.endswith('"')) or (
        selector.startswith('text=`\'') and selector.endswith('\'')
    ):
        return (
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().text("{selector[6:-1]}")',
            )
            if project.config.context is project.EnvContext.android
            else (AppiumBy.IOS_PREDICATE, f'label == "{selector[6:-1]}"')
        )

    # BY PARTIAL TEXT
    if selector.startswith('text='):
        return (
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().textContains("{selector[5:]}")',
            )
            if project.config.context is project.EnvContext.android
            else (
                AppiumBy.IOS_CLASS_CHAIN,
                f'**/*[`label CONTAINS "{selector[5:]}"`][-1]',
            )
        )

    # BY CLASS NAME (SAME for IOS and ANDROID)
    if any(
        selector.lower().startswith(prefix)
        for prefix in [
            'uia',
            'xcuielementtype',
            'cyi',
            'android.widget',
            'android.view',
        ]
    ):
        return AppiumBy.CLASS_NAME, selector

    # BY IMPLICIT ID (single word, no spaces)
    if is_word_with_dashes_underscores_or_numbers(selector):
        if project.config.context is project.EnvContext.android:
            return to_app_package_wise_by(selector)
        else:
            return AppiumBy.ACCESSIBILITY_ID, selector

    # BY IMPLICIT ACCESSIBILITY ID (SAME for IOS and ANDROID)
    if are_words_with_dashes_underscores_or_numbers_separated_by_space(selector):
        return AppiumBy.ACCESSIBILITY_ID, selector

    raise Error(f'Unsupported selector: {selector}')
