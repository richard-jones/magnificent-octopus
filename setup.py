from setuptools import setup, find_packages

setup(
    name = 'octopus',
    version = '1.0.0',
    packages = find_packages(),
    install_requires = [
        "requests",
        "Flask==0.9",
        "esprit",
        "Flask-Login==0.1.3",
        "simplejson",
        "lxml",
        "Flask-WTF==0.8.3",
        "nose"
    ],
    url = 'http://cottagelabs.com/',
    author = 'Cottage Labs',
    author_email = 'us@cottagelabs.com',
    description = 'Magnificent Octopus - Flask application helper library',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: Copyheart',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
