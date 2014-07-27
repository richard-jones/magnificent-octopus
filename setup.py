from setuptools import setup, find_packages

setup(
    name = 'monitorui',
    version = '0.0.1',
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
    description = 'monitorui - a basic search/browse interface for the jisc monitor data',
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