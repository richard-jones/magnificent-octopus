from octopus.core import app, initialise
from octopus.lib import plugin, cli
import sys

command = sys.argv[1]
args = sys.argv[2:]

for name, path in app.config.get("CLI_SCRIPTS", {}).iteritems():
    ran = False
    if name == command:
        # get an instance of the script
        klazz = plugin.load_class(path)
        inst = klazz()

        # check that it can legitimately be run
        if not isinstance(inst, cli.Script):
            print command, "is not a legitimate octopus script - must extend from octopus.lib.cli.Script"
            exit()

        # ensure the app is initialised
        initialise()

        # run it
        ran = True
        klazz().run(args)

    if not ran:
        print command, "- command not found"
