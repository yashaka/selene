from setuptools import setup
from selene import version
from os.path import dirname, join, abspath

description = 'User-oriented browser tests in Python (Selenide port)'
long_description = open(join(abspath(dirname(__file__)), "README.md")).read()

setup(
    name='selene',
    version=version.VERSION,
    url='http://github.com/yashaka/selene/',
    download_url='https://github.com/yashaka/selene/tarball/' + version.VERSION,
    license='MIT',
    author='Iakiv Kramarenko',
    author_email='yashaka@gmail.com',
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['selene',
              'selene.api',
              'selene.common',
              'selene.core',
              'selene.support',
              'selene.support.shared',
              'selene.support.conditions',
              ],
    include_package_data=True,
    install_requires=['selenium==3.141.0', 'webdriver_manager', 'future', 'backports.functools_lru_cache'],
    platforms='any',
    zip_safe=False,
    keywords=['testing', 'selenium', 'selenide', 'browser', 'pageobject', 'widget', 'wrapper'],
    classifiers=[
        'Programming Language :: Python',
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
