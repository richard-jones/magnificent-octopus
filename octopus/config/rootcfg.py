# absolute paths, or relative paths from root directory, to the desired config files (in the order you want them loaded)
CONFIG_FILES = [
    "magnificent-octopus/octopus/config/webapp.py",
    "magnificent-octopus/octopus/modules/sherpafact/settings.py",
    "magnificent-octopus/octopus/modules/es/settings.py",
    "magnificent-octopus/octopus/modules/epmc/settings.py",
    "magnificent-octopus/octopus/config/googlemap.py",
    "config/service.py",
    "local.cfg"
]

# absolute paths, or relative paths from root directory, to the template directories (in the order you want them looked at)
TEMPLATE_PATHS = [
    "service/templates",
    "magnificent-octopus/octopus/templates",
    "magnificent-octopus/octopus/modules/clientjs/templates"
]

# absolute paths, or relative paths from the root directory, to the static file directories (in the order you want them looked at)
STATIC_PATHS = [
    "service/static",
    "magnificent-octopus/octopus/static"
]

# module import paths for the startup modules that need to run at application init type (in the order you want them run)
INITIALISE_MODULES = [
    "octopus.modules.es.initialise"
]