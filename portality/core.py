import os, esprit, jinja2
from flask import Flask
from urllib import unquote


def create_app():
    app = Flask(__name__)
    configure_app(app)

    #if app.config.get('INITIALISE_INDEX',False): initialise_index(app)

    setup_jinja(app)
    #setup_error_email(app)
    return app

def configure_app(app):
    # read in the root config
    root_config = os.getenv('APP_CONFIG')
    if not root_config:
        raise Exception("Set APP_CONFIG to your root config file")
    root_config = os.path.abspath(root_config)
    if os.path.exists(root_config):
        print "Loading root config from", root_config
        app.config.from_pyfile(root_config)
    else:
        raise Exception("Root config did not exist at " + root_config)

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
        choices = [app.jinja_loader]
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




def initialise_index(app):
    mappings = app.config["MAPPINGS"]
    conn = esprit.raw.Connection(app.config['ELASTIC_SEARCH_HOST'], app.config['ELASTIC_SEARCH_DB'])
    if not esprit.raw.index_exists(conn):
        print "Creating Index; host:" + str(conn.host) + " port:" + str(conn.port) + " db:" + str(conn.index)
        esprit.raw.create_index(conn)
    for key, mapping in mappings.iteritems():
        if not esprit.raw.has_mapping(conn, key):
            r = esprit.raw.put_mapping(conn, key, mapping)
            print key, r.status_code

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

