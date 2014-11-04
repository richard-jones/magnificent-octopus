import os, esprit, jinja2
from flask import Flask
from urllib import unquote

def create_app():
    app = Flask(__name__)
    configure_app(app)
    setup_jinja(app)
    #setup_error_email(app)
    return app

def configure_app(app):
    # read in the root config and resolve it to an actual file
    root_config = os.getenv('APP_CONFIG')
    if not root_config:
        print "Using built-in rootcfg.py"
        root_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "rootcfg.py")
    else:
        root_config = os.path.abspath(root_config)

    if os.path.exists(root_config):
        print "Loading root config from", root_config
        app.config.from_pyfile(root_config)
    else:
        raise Exception("Root config did not exist at " + root_config + ".  You may set one with the APP_CONFIG environment variable")

    # for each config file specified in the root, find and load
    config_files = app.config.get("CONFIG_FILES", [])
    for cf in config_files:
        cf = os.path.abspath(cf)
        if os.path.exists(cf):
            print "Loading config from", cf
            app.config.from_pyfile(cf)
        else:
            print "WARNING: no config file at", cf

    # expand the path names for the static files (so we only have to do it the once)
    statics = app.config.get("STATIC_PATHS", [])
    nps = []
    for sp in statics:
        np = os.path.abspath(sp)
        print "Specifying static directory", np
        nps.append(np)
    app.config["STATIC_PATHS"] = nps

def setup_jinja(app):
    template_paths = app.config.get("TEMPLATE_PATHS", [])
    if len(template_paths) > 0:
        choices = []
        for tp in template_paths:
            tp = os.path.abspath(tp)
            print "Registering Template Path", tp
            choices.append(jinja2.FileSystemLoader(tp))
        my_loader = jinja2.ChoiceLoader(choices)
        app.jinja_loader = my_loader

    app.jinja_env.add_extension('jinja2.ext.do')
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    app.jinja_env.globals['getattr'] = getattr
    app.jinja_env.globals['unquote'] = unquote

    # a jinja filter that prints to the Flask log
    def jinja_debug(text):
        print text
        return ''
    app.jinja_env.filters['debug']=jinja_debug




def setup_error_email(app):
    ADMINS = app.config.get('ADMINS', '')
    if not app.debug and ADMINS:
        import logging
        from logging.handlers import SMTPHandler
        mail_handler = SMTPHandler('127.0.0.1',
                                   'server-error@no-reply.com',
                                   ADMINS, 'error')
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)



app = create_app()

# everything beneath here can be run after the app has been officially created
# though note that all the imports are delayed because of the import circularity-avoidance

def initialise():
    from octopus.lib import plugin
    mods = app.config.get("INITIALISE_MODULES", [])
    for modpath in mods:
        mod = plugin.load_module(modpath)
        fn = getattr(mod, "initialise")
        fn()