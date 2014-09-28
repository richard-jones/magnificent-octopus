# Portality Helper Library

## Email: portality.lib.email

Contains functions for sending email from your application

## Gravatar: portality.lib.gravatar

Contains functions for retrieving data from gravatar

## Plugins: portality.lib.plugin

Contains functions for dynamically loading classes at run time

## Pycharm: portality.lib.pycharm

Contains code for integrating with the PyCharm debugger

(currently not working)

## Web Application Support: portality.lib.webapp

Contains functions for building useful Flask webapplications:

* custom_static - used by Portality to serve static files from a set of directories.  Can be incorporated into your web application with:

    @app.route("/static/<path:filename>")
    def static(filename):
        return custom_static(filename)

* ssl_required - decorator which ensures that applications use SSL on certain requests when required:

    @app.route("/account/<username>")
    @ssl_required
    def acc(username): pass

* jsonp - decorator which enables support for JSON-P on API requests:

    @app.route("/api/call")
    @jsonp
    def api(): pass

