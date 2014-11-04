from octopus.core import app
import pydevd

app.config["DEBUG"] = False
host = app.config.get("DEBUG_SERVER_HOST", "localhost")
port = app.config.get("DEBUG_SERVER_PORT", 51234)

pydevd.settrace(host, port=port, stdoutToServer=True, stderrToServer=True)
print "started with debug"