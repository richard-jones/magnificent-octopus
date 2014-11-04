# Examples

This module just wraps up some examples of usages of other modules for reference and development purposes

To see the examples, mount the blueprint in your service/web.py

```python
    from octopus.modules.examples.examples import blueprint as examples
    app.register_blueprint(examples, url_prefix="/examples")
```

Then you should be able to see the following examples

* Autocomplete - /examples/ac
* Sherpa Fact - /examples/fact

