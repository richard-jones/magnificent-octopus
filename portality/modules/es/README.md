# Elastisearch Integration Library

## Query Endpoint

This provides read-only access to configured query endpoints.

Can be mounted into your app as a blueprint with:

```python
    from portality.modules.es.query import blueprint as query
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
    from portality.modules.es.autocomplete import blueprint as autocomplete
    app.register_blueprint(autocomplete, urlprefix="/autocomplete")
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