from octopus.core import app
import importlib

class PluginException(Exception):
    pass

def load_class_raw(classpath):
    modpath = ".".join(classpath.split(".")[:-1])
    classname = classpath.split(".")[-1]
    mod = importlib.import_module(modpath)
    klazz = getattr(mod, classname)
    return klazz

def load_class(classpath, cache_class_ref=True):
    klazz = app.config.get("PLUGIN_CLASS_REFS", {}).get(classpath)
    if klazz is not None:
        return klazz

    klazz = load_class_raw(classpath)

    if cache_class_ref:
        if "PLUGIN_CLASS_REFS" not in app.config:
            app.config["PLUGIN_CLASS_REFS"] = {}
        app.config["PLUGIN_CLASS_REFS"][classpath] = klazz

    return klazz

def load_module(modpath):
    return importlib.import_module(modpath)