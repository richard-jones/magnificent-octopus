# Magnificent Octopus

Used for building Flask-based applications which may want to talk to an Elasticsearch back-end, and want to 
integrate with all kinds of external services.

## Root Configuration

The root configuration tells Magnificent Octopus where to load the module configurations from, and where to serve Jinja templates and static files from.

It also details scripts to run during application initialisation (i.e. post-configuration but pre-execution).  See the section **Initialisation** below.

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
        "magnificent-octopus/octopus/templates",
        "... lib and module template directories ...",
        
    ]
    
    # absolute paths, or relative paths from the root directory, to the static file directories (in the order you want them looked at)
    STATIC_PATHS = [
        "service/static",
        "magnificent-octopus/octopus/static",
        "... lib and module static directories ...",
    ]
    
    # module import paths for the startup modules that need to run at application init type (in the order you want them run)
    INITIALISE_MODULES = [
        "octopus.modules.es.initialise"
    ]
```

## Initialisation

After the app has been created and configured, but before it is run, it needs to be initialised.  In all scripts and modules which require the application to be in a known fully-operational state, you will need to run the initialise script first.

```python
    from octopus.core import app, initialise
    initialise()
```

This will load all the modules specified in the **INITIALISE_MODULES** config in the root configuration (see above).  It will then execute their "initialise" function; each module which requires initialisation must provide its own initialisation routine.

To create an initialise routine just supply a function as follows

```python
    from octopus.core import app
    def initialise():
        # do your initialisation operations
        # this function should be idempotent
        pass
```

## Scripts

The octopus /bin directory contains command line scripts that may aid in using/managing an octopus instance.

See the [README](https://github.com/richard-jones/magnificent-octopus/tree/master/bin/README.md) for more details.

## Library code

The octopus.lib directory contains helper libraries for building your applications.  See the [README](https://github.com/richard-jones/magnificent-octopus/tree/master/octopus/lib/README.md) for details

## Templates

Octopus comes with a basic bootstrap3-based layout template.  You should copy the elements you want to modify to your application's template directory, and they will automatically override the octopus ones.

See the templates [here](https://github.com/richard-jones/magnificent-octopus/tree/master/octopus/templates)

## JavaScript

Octopus provides a small library of useful javascript functions.  See the [README](https://github.com/richard-jones/magnificent-octopus/tree/master/octopus/static/js/README.md)

It also bundles an extensive collection of 3rd party utilities which might be useful for your application, which can be found [here](https://github.com/richard-jones/magnificent-octopus/tree/master/octopus/static/vendor)

The default \_js_includes.html template that comes with octopus already imports the latest version of each of these for convenience, so you could copy that file to your project and add/remove as necessary.

## Modules

The following modules are available (follow the links to their README files for more details)

### ClientJS

**module** [octopus.modules.clientjs](https://github.com/richard-jones/magnificent-octopus/tree/master/octopus/modules/clientjs/README.md)

Used for serving javascript configuration to the client for use by other modules.

### CRUD

**module** [octopus.modules.crud](https://github.com/richard-jones/magnificent-octopus/tree/master/octopus/modules/crud/README.md)

Provides a RESTful CRUD (Create, Retrieve, Update, Delete) API for objects in your application.

### DOAJ

**module** [octopus.modules.doaj](https://github.com/richard-jones/magnificent-octopus/tree/master/octopus/modules/doaj/README.md)

Used for providing remote access to the DOAJ search service

### EPMC

**module**: [octopus.modules.epmc](https://github.com/richard-jones/magnificent-octopus/tree/master/octopus/modules/epmc/README.md)

Provides a client library for accessing the EuropePMC metadata and fulltexts

### Elasticsearch

**module**: [octopus.modules.es](https://github.com/richard-jones/magnificent-octopus/tree/master/octopus/modules/es/README.md)

Used for providing direct access to the Elasticsearch back-end:

* Read-only query endpoint
* Autocomplete features.  
* Front-end javascript functions for connecting to back-end features.
* TestCase implementation for setUp and tearDown of test indexes

### Examples

**module**: [octopus.modules.examples](https://github.com/richard-jones/magnificent-octopus/tree/master/octopus/modules/examples/README.md)

Provides working examples of bits of some of the other modules available here

### Form

**module**: [octopus.modules.form](https://github.com/richard-jones/magnificent-octopus/tree/master/octopus/modules/form/README.md)

Various UI form utilities:

* A mechanism to bind WTForms forms with context-specific behaviours
* A UI rendering helper library with support for various Bootstrap form types
* Custom fields and validators beyond those offered by WTForms
* Javascript functions to aid in good form building

### Identifiers

**module**: [octopus.modules.identifiers](https://github.com/richard-jones/magnificent-octopus/tree/master/octopus/modules/identifiers/README.md)

Various tools for working with identifiers

### OAG

**module**: [octopus.modules.oag](https://github.com/richard-jones/magnificent-octopus/tree/master/octopus/modules/oag/README.md)

Client environment for communicating with the Open Article Gauge:

* Pure client environment
* Asynchronous job runner for managing large/repeat requests
* Monitoring interface for job runner

### Romeo

**module**: [octopus.modules.romeo](https://github.com/richard-jones/magnificent-octopus/tree/master/octopus/modules/romeo/README.md)

Provides a client library for accessing the Sherpa RoMEO API.

### Sherpa Fact

**module**: [octopus.modules.sherpafact](https://github.com/richard-jones/magnificent-octopus/tree/master/octopus/modules/sherpafact/README.md)

Provides a client library for accessing the Sherpa FACT API.

