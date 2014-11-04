# Magnificent Octopus Helper Library

## Email: octopus.lib.email

Contains functions for sending email from your application

## Gravatar: octopus.lib.gravatar

Contains functions for retrieving data from gravatar

## Plugins: octopus.lib.plugin

Contains functions for dynamically loading classes at run time

## Pycharm: octopus.lib.pycharm

Contains code for integrating with the PyCharm debugger

(currently not working)

## Web Application Support: octopus.lib.webapp

Contains functions for building useful Flask webapplications:

* custom_static - used by Magnificent Octopus to serve static files from a set of directories.  Can be incorporated into your web application with:

```python
    @app.route("/static/<path:filename>")
    def static(filename):
        return custom_static(filename)
```

* ssl_required - decorator which ensures that applications use SSL on certain requests when required:

```python
    @app.route("/account/<username>")
    @ssl_required
    def acc(username): pass
```

* jsonp - decorator which enables support for JSON-P on API requests:

```python
    @app.route("/api/call")
    @jsonp
    def api(): pass
```
