# Magnificent Octopus Helper Library

## CLCSV: octopus.lib.clcsv

Classes for representing CSV files, including column-wise reading and unicode support

## DataObj: octopus.lib.dataobj

Class which provides services to objects which store their internal state in self.data

Create an object which supports all the data operations:

    class MyObject(octopus.lib.dataobj.DataObj):
        pass

You can then create new data objects empty or with a seed dictionary:

    myo = MyObject()
    myo = MyObject({"one" : 1, "two" : "two"})

if you specify a SCHEMA class attribute then the dictionary you pass in will be validated against it.

You may also validate any document at any time by calling .validate().

To specify a schema use the following structure:

```json
{
    "fields" : ["<string-like field>"],
    "bools" : ["<boolean fields>"],
    
    "lists" : ["<fields which are lists>"],
    "list_entries" : {
        "<list field name>" : {<object definition>}
    },
    
    "objects" : ["<fields which are objects>"],
    "object_entries" : {
        "<object entry name>" : {<object definition>}
    }
}
```

For list fields, if no entry is provided in list_entries, the values will be validated as strings.

For object fields, if no entry is provided in object_entries, the sub-structure will not be validated

Schema structure nests, so where you see <object definition> you can use the schema definition structure in its place.


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
