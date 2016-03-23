from octopus.lib import cli
from octopus.modules.scheduler import core

class StartScheduler(cli.Script):
    def run(self, argv):
        core.run()
