import os
import sys

# load modules from parent dir
sys.path.insert(1, os.path.dirname(sys.path[0]))

from mozharness.base.script import platform_name

# Releng machines
config = {}

platform_config = {
    'linux64': {
        'exes': {
            'python': '/tools/buildbot/bin/python',
            'virtualenv': ['/tools/buildbot/bin/python', '/tools/misc-python/virtualenv.py'],
        },
        'env': {
            'DISPLAY': ':2',
        }
    }
}

config = platform_config[platform_name()]
