from setuptools import setup, find_packages

setup(
    name = 'octopus',
    version = '1.0.0',
    packages = find_packages(),
    install_requires = [
        "werkzeug==0.8.3",
        "Flask==0.9",
        "Flask-Login==0.1.3",
        "requests",
        "esprit",
        "simplejson",
        "lxml==3.4.4",
        "Flask-WTF==0.8.3",
        "nose",
        "Flask-Mail==0.9.1",
        "python-dateutil",
        "unidecode"
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
