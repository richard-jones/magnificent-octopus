# absolute paths, or relative paths from root application directory (ie. above the magnificent-octopus directory),
# to the desired config files (in the order you want them loaded)
CONFIG_FILES = [
    # octopus.lib config files
    "magnificent-octopus/octopus/config/cli.py",
    "magnificent-octopus/octopus/config/dates.py",
    "magnificent-octopus/octopus/config/googlemap.py",
    "magnificent-octopus/octopus/config/http.py",
    "magnificent-octopus/octopus/config/mail.py",
    "magnificent-octopus/octopus/config/webapp.py",

    # octopus.module config files
    "magnificent-octopus/octopus/modules/account/settings.py",
    "magnificent-octopus/octopus/modules/cache/settings.py",
    "magnificent-octopus/octopus/modules/clientjs/settings.py",
    "magnificent-octopus/octopus/modules/coreacuk/settings.py",
    "magnificent-octopus/octopus/modules/crud/settings.py",
    "magnificent-octopus/octopus/modules/doaj/settings.py",
    "magnificent-octopus/octopus/modules/epmc/settings.py",
    "magnificent-octopus/octopus/modules/es/settings.py",
    "magnificent-octopus/octopus/modules/jper/settings.py",
    "magnificent-octopus/octopus/modules/oag/settings.py",
    "magnificent-octopus/octopus/modules/romeo/settings.py",
    "magnificent-octopus/octopus/modules/sherpafact/settings.py",
    "magnificent-octopus/octopus/modules/store/settings.py",
    "magnificent-octopus/octopus/modules/swordv2/settings.py",

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
    "magnificent-octopus/octopus/modules/account/templates",
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
    "magnificent-octopus/octopus/modules/account/static",
    "magnificent-octopus/octopus/modules/clientjs/static",
    "magnificent-octopus/octopus/modules/crud/static",
    "magnificent-octopus/octopus/modules/es/static",
    "magnificent-octopus/octopus/modules/form/static",
    "magnificent-octopus/octopus/modules/oag/static",
    "magnificent-octopus/octopus/modules/sherpafact/static"
]

# module import paths for the app initialisation modules that need to run at flask app creation
# (e.g. to do things like add login management support)
SETUP_MODULES = [
    "octopus.modules.account.setup_app",     # NOTE that you will also need to set ACCOUNT_ENABLE=True for this to run
    "service.setup_app"
]

# module import paths for the startup modules that need to run at application startup (in the order you want them run)
# (e.g. to do things like create/pre-populate the database)
INITIALISE_MODULES = [
    "octopus.modules.es.initialise",
    "service.initialise"
]