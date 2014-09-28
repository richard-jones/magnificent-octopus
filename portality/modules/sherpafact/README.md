# SHERPA FACT Client Library

This is a basic client library for using the Sherpa FACT API

```python
    from portality.modules.sherpafact import client
```

Construct an instance of the client (which will use the default configuration in settings.py unless otherwise told):

```python
    fc = client.FactClient()
```

Then run your query against the API with the relevant arguments:

```python
    fact = fc.query("609", issn="1234-5678")
```

This will return you an instance of the client.Fact object, for the relevant return type.  You can get the raw
data out if it with

```python
    fact.raw
```