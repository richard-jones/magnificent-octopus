# SHERPA FACT Integration

## Client Library

This is a basic client library for using the Sherpa FACT API

```python
    from octopus.modules.sherpafact import client
```

Construct an instance of the client (which will use the default configuration in **settings.py** unless otherwise told):

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

## Proxy

You can integrate a proxied call to the FACT API in your application by including the blueprint as follows:

```python
    from octopus.modules.sherpafact.proxy import blueprint as fact
    app.register_blueprint(fact, url_prefix="/fact")
```

Calls must provide the following URL query arguments:

* journal_or_issn - a journal name or an ISSN (the proxy will figure out which)
* funders - a comma delimited list of funder ids from the Juliet service

### JavaScript

The Sherpa Fact proxy can be called via the module's JavaScript library.  Ensure that the route to the proxy endpoint 
is in the javascript configuration; for example, in octopus/modules/sherpafact/settings.py

```python
    CLIENTJS_FACT_PROXY_ENDPOINT = "/autocomplete/compound"
```

You can then call the proxy in javascript with:

```javascript
    octopus.sherpafact.proxy({
        journal_or_issn: "journal_or_issn",
        funders: ["funders"],
        success: success_function
    });
```
