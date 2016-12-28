from setuptools import setup
from selene import version

description = 'Concise API for selenium in Python + Ajax support + PageObjects + Widgets (Selenide/Capybara + htmlelements/Widgeon alternative)'
# long_description = 'see http://github.com/yashaka/selene/ for more docs...'

setup(
    name='selene',
    version=version.VERSION,
    url='http://github.com/yashaka/selene/',
    download_url='https://github.com/yashaka/selene/tarball/' + version.VERSION,
    license='Apache Software License',
    author='Iakiv Kramarenko',
    author_email='yashaka@gmail.com',
    description=description,
    # long_description=long_description,
    packages=['selene'],
    include_package_data=True,
    install_requires=['selenium', 'future', 'backports.functools_lru_cache'],
    platforms='any',
    zip_safe=False,
    keywords=['testing', 'selenium', 'selenide', 'browser', 'pageobject', 'widget', 'wrapper'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Internet :: WWW/HTTP :: Browsers',
        'Topic :: Software Development :: Testing'
    ]
)
