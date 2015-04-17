from setuptools import setup

from selene import version

description = 'Concise API for selenium + Ajax support + PageObjects + Widgets in Python (Selenide/Capybara + Widgeon alternative)'
long_description = 'see http://github.com/yashaka/selene/ for more docs...'

setup(
    name='selene',
    version=version.VERSION,
    url='http://github.com/yashaka/selene/',
    license='Apache Software License',
    author='Iakiv Kramarenko',
    install_requires=[],
    author_email='yashaka@gmail.com',
    description=description,
    long_description=long_description,
    packages=['widgeon'],
    include_package_data=True,
    platforms='any',
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Development Status :: 2 - Pre-Alpha',
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