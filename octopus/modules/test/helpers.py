import socket
import time
import sys
import subprocess
from octopus.modules import dictdiffer


def get_first_free_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))  # let OS pick the first available port
    free_port = sock.getsockname()[1]  # which port did the OS pick?
    sock.close()
    return free_port


class TestServer(object):
    def __init__(self, port, index, python_app_module_path='service/web.py'):
        self.port = port
        self.index = index
        self.python_app_module_path = python_app_module_path
        self._process = None

    def get_server_url(self):
        """
        Return the url of the test server
        """
        return 'http://localhost:{0}'.format(self.port)

    def spawn(self):
        # sys.executable is the full, absolute path to the current Python interpreter
        # This is used so that the new process with the test app in it runs properly in a virtualenv.
        self._process = subprocess.Popen([sys.executable, self.python_app_module_path, '--port', str(self.port), '--index', self.index, '--no-logging'])

        # we must wait for the server to start listening
        time.sleep(1)

    def terminate(self):
        if self._process:
            self._process.terminate()


def diff_dicts(d1, d2, d1_label='d1', d2_label='d2', print_unchanged=False):
    """
    Diff two dictionaries - prints changed, added and removed keys and the changed values. DOES NOT DO NESTED DICTS!

    :param d1: First dict - we compare this with d2
    :param d2: Second dict - we compare against this one
    :param d1_label: Will be used instead of "d1" in debugging output to make it more helpful.
    :param d2_label: Will be used instead of "d2" in debugging output to make it more helpful.
    :param print_unchanged: - should we print set of unchanged keys (can be long and useless). Default: False.
    :return: nothing, prints results to STDOUT
    """
    differ = dictdiffer.DictDiffer(d1, d2)
    print 'Added :: keys present in {d1} which are not in {d2}'.format(d1=d1_label, d2=d2_label)
    print differ.added()
    print
    print 'Removed :: keys present in {d2} which are not in {d1}'.format(d1=d1_label, d2=d2_label)
    print differ.removed()
    print
    print 'Changed :: keys which are the same in {d1} and {d2} but whose values are different'.format(d1=d1_label, d2=d2_label)
    print differ.changed()
    print

    if differ.changed():
        print 'Changed values :: the values of keys which have changed. Format is as follows:'
        print '  Key name:'
        print '    value in {d1}'.format(d1=d1_label)
        print '    value in {d2}'.format(d2=d2_label)
        print
        for key in differ.changed():
            print ' ', key + ':'
            print '   ', d1[key]
            print '   ', d2[key]
            print
        print

    if print_unchanged:
        print 'Unchanged :: keys which are the same in {d1} and {d2} and whose values are also the same'.format(d1=d1_label, d2=d2_label)
        print differ.unchanged()
