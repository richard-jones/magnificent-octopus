# Portentious

Version 2.0 of the highly useful Portality library from Cottage Labs.

Used for building Flask-based applications which may want to talk to an Elasticsearch back-end

## Root Configuration

The root configuration tells Portentious where to load the module configurations from, and where to server Jinja templates and static files from.

The built-in configuration will load the config for all known modules and libraries.  You can override this by providing your own one in the environment variable APP_CONFIG at startup.

It provides ONLY the following configuration options:

```python
    # absolute paths, or relative paths from root directory, to the desired config files (in the order you want them loaded)
    CONFIG_FILES = [
        "... lib and module configs ...",
        "config/service.py",
        "local.cfg"
    ]
    
    # absolute paths, or relative paths from root directory, to the template directories (in the order you want them looked at)
    TEMPLATE_PATHS = [
        "service/templates",
        "portentious/portality/templates"
    ]
    
    # absolute paths, or relative paths from the root directory, to the static file directories (in the order you want them looked at)
    STATIC_PATHS = [
        "service/static",
        "portentious/portality/static"
    ]
```

## Library code

The portality.lib directory contains helper libraries for building your applications.  See the [README](https://github.com/richard-jones/portentious/tree/master/portality/lib/README.md) for details

## Modules

The following modules are available (follow the links to their README files for more details)

### Elasticsearch

**module**: [portality.modules.es](https://github.com/richard-jones/portentious/tree/master/portality/modules/es/README.md)

Used for providing direct access to the Elasticsearch back-end.  Implements a read-only query endpoint, and autocomplete features.  
Also provides front-end javascript functions for querying the back-end features.

### Sherpa Fact

**module**: [portality.modules.sherpafact](https://github.com/richard-jones/portentious/tree/master/portality/modules/sherpafact/README.md)

Provides a client library for accessing the Sherpa FACT API.