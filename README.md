# Portentious

Version 2.0 of the highly useful Portality library from Cottage Labs.

Used for building Flask-based applications which may want to talk to an Elasticsearch back-end

## Library code

The portality.lib directory contains helper libraries for building your applications.  See the [README](https://github.com/richard-jones/portentious/tree/master/portality/lib/README.md) for details

## Modules

The following modules are available (follow the links to their README files for more details)

### Elasticsearch

**module**: [portality.modules.es](https://github.com/richard-jones/portentious/tree/master/portality/modules/es/README.md)

Used for providing direct access to the Elasticsearch back-end.  Implements a read-only query endpoint, and autocomplete features.

### Sherpa Fact

**module**: [portality.modules.sherpafact](https://github.com/richard-jones/portentious/tree/master/portality/modules/sherpafact/README.md)

Provides a client library for accessing the Sherpa FACT API.