# DOAJ Integration

This provides a very basic client for accessing the DOAJ via its public search interface:

```python
    from octopus.modules.doaj import client
    c = client.DOAJSearchClient()
```

From it you can query the DOAJ using any Elasticsearch formatted query that would work against the data, and get back
the resulting objects:

```python
    q = {"query" : {"match_all" : {}}}
    results = c.object_search(query)
```

You can also query for specific attributes, where methods support it

```python
    journals = c.journal_by_issn("1234-5678")
```

