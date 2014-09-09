from setuptools import setup, find_packages

setup(
    name = 'portality',
    version = '2.0.0',
    packages = find_packages(),
    install_requires = [
        "requests",
        "Flask==0.9",
        "esprit",
        "Flask-Login==0.1.3",
    ],
    url = 'http://cottagelabs.com/',
    author = 'Cottage Labs',
    author_email = 'us@cottagelabs.com',
    description = 'Portality 2 - Flask application helper library',
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