# Elastisearch Integration Library

## DAO

A DAO is a Data Access Object and provides a mechanism to load data from a data source.  This module provides a DAO called *ESDAO* which
loads data from Elasticsearch.  It, in turn, extends from the *esprit* Domain Object (esprit.dao.DomainObject).

The key things that it provides are automatic configuration of the ES connection, and a default document mapping which
can be used by the ES initialisation scripts.  Therefore, to implement a DAO which can be used by your model objects, all
that is required is your own type-specific implementation:

```python
class MyDAO(octopus.modules.es.dao.ESDAO):
    __type__ = "mytype"
```

In order for this to work correctly you must have correctly set the configuration parameters:

* ELASTIC_SEARCH_HOST
* ELASTIC_SEARCH_INDEX

### Initialisation

This module provides a function to initialise the index at application startup.  It needs to be in the rootcfg.py as follows:

```python
INITIALISE_MODULES = [
    "octopus.modules.es.initialise"
]
```

In order to have the types in the index created correctly the following configuration is required:

```python
INITIALISE_INDEX = True     # this is the default behaviour

ELASTIC_SEARCH_MAPPINGS = [
    service.dao.MyDAO       # a DAO as defined above
]
```

When the initialise function in the module is run (which magnificent octopus will do for you), it will load each class specified
and call its "mappings" function, and then put the mappings it receives into the index.

To change the mapping for a given type, just override the mappings function

```python
class MyDAO(octopus.modules.es.dao.ESDAO):
    __type__ = "mytype"
    
    @classmethod
    def mappings():
        return {
            cls.__type__ : {
                cls.__type__ : {
                    # mapping definition here
                }
            }
        }
```

Note that a single class may return mappings for multiple types - the above example assumes a one-to-one mapping between 
the class and the type of mapping it creates.

## Query Endpoint

This provides read-only access to configured query endpoints.

Can be mounted into your app as a blueprint with:

```python
    from octopus.modules.es.query import blueprint as query
    app.register_blueprint(query, urlprefix="/query")
```

See **settings.py** for details of configuration.

You can make requests as if this endpoint were an Elasticsearch _search index, so:

    http://localhost:5000/query/_search?q=mysearch
    http://localhost:5000/query/_search?source={<es query object>}

You can also pull objects by identifier:

    http://localhost:5000/query/123456789

## Autocomplete Endpoint(s)

### Compound

The compound autocomplete takes a query, and returns you a multi-field object, containing the fields you are interested in.

This can be useful for building more complex result-selection options in the front end (e.g. showing both a suggested Journal's title and ISSN)

Can be mounted into your app as a blueprint with:

```python
    from octopus.modules.es.autocomplete import blueprint as autocomplete
    app.register_blueprint(autocomplete, url_prefix="/autocomplete")
```

See **settings.py** for details of configuration.

You can make requests as follows:

    http://localhost:5000/autocomplete/compound/journal?q=1234
    http://localhost:5000/autocomplete/compound/journal?q=Revista&size=20

The result will be a list (ordered by relevance) containing the desired fields, e.g:

```python
    [
        {
            issn: ["0123-3475",1909-8758"],
            title: ["Revista Colombiana de Biotecnología"]
        },
        {
            issn: ["1515-6877","1851-8893"],
            title: ["Orientación y Sociedad : Revista Internacional e Interdisciplinaria de Orientación Vocacional Ocupacional "]
        }
    ]
```

#### Javascript

The compound query endpoint can be called via the module's javascript library.  Ensure that the route to the autocomplete endpoint 
is in the javascript configuration.  For example

```javascript
    var octopus = {
        "es" : {
            "compound_endpoint" : "/autocomplete/compound"
        }
    }
```

Set up an input field as an compound autocomplete field with:

```javascript
    esac.bindCompoundAutocomplete({
        selector : "#my_field",
        minimumInputLength : 3,
        placeholder :"Enter some text";
        type : "configured_endpoint";
        format : function(result) { return {id : result.term, text: result.term} };
        allow_clear : true
    })
```

Note that the "configured_endpoint" is one of the autocomplete endpoints specified in **settings.py**.

If you want to call the autocomplete without binding to an input form, as above, you can go directly to the query method:

```javascript
    esac.compoundAutocomplete({
        q : "query string";
        size : 10;
        type : "configured_endpoint";
        success : function(data) {};
        complete : function(data) {};
        error : function(data) {};
    })
```