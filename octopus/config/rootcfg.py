# absolute paths, or relative paths from root application directory (ie. above the magnificent-octopus directory),
# to the desired config files (in the order you want them loaded)
CONFIG_FILES = [
    # octopus.lib config files
    "magnificent-octopus/octopus/config/webapp.py",
    "magnificent-octopus/octopus/config/googlemap.py",
    "magnificent-octopus/octopus/config/mail.py",

    # octopus.module config files
    "magnificent-octopus/octopus/modules/crud/settings.py",
    "magnificent-octopus/octopus/modules/doaj/settings.py",
    "magnificent-octopus/octopus/modules/epmc/settings.py",
    "magnificent-octopus/octopus/modules/es/settings.py",
    "magnificent-octopus/octopus/modules/oag/settings.py",
    "magnificent-octopus/octopus/modules/romeo/settings.py",
    "magnificent-octopus/octopus/modules/sherpafact/settings.py",

    # local service configuration
    "config/service.py",
    "local.cfg"
]

# absolute paths, or relative paths from root directory, to the template directories (in the order you want them looked at)
TEMPLATE_PATHS = [
    # local service templates
    "service/templates",

    # octopus standard bootstrap layout templates
    "magnificent-octopus/octopus/templates",

    # octopus modules templates
    "magnificent-octopus/octopus/modules/clientjs/templates",
    "magnificent-octopus/octopus/modules/oag/templates"
]

# absolute paths, or relative paths from the root directory, to the static file directories (in the order you want them looked at)
STATIC_PATHS = [
    # local service static directory
    "service/static",

    # octopus standard static directory - contains all vendor JS, plus the core Octopus JS
    "magnificent-octopus/octopus/static",

    # octopus modules static directories
    "magnificent-octopus/octopus/modules/crud/static",
    "magnificent-octopus/octopus/modules/es/static",
    "magnificent-octopus/octopus/modules/form/static",
    "magnificent-octopus/octopus/modules/oag/static"
]

# module import paths for the startup modules that need to run at application init type (in the order you want them run)
INITIALISE_MODULES = [
    # octopus modules initialisation
    "octopus.modules.es.initialise"
]