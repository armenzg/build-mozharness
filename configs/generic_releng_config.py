# This config file has generic values needed for any job and any platform running
# on Release Engineering machines inside the VPN
from mozharness.base.script import platform_name

PYTHON_WIN32 = 'c:/mozilla-build/python27/python.exe'
# These are values specific to running machines on Release Engineering machines
# to run it locally on your machines append --cfg developer_config.py
PLATFORM_CONFIG = {
    'linux64': {
        'exes': {
            'python': '/tools/buildbot/bin/python',
            'virtualenv': ['/tools/buildbot/bin/python', '/tools/misc-python/virtualenv.py'],
        },
        'env': {
            'DISPLAY': ':2',
        }
    },
    'macosx64': {},
    'win32': {
        "exes": {
            # Otherwise, depending on the PATH we can pick python 2.6 up
            'python': PYTHON_WIN32,
            'hgtool.py': [PYTHON_WIN32, 'c:/builds/hg-shared/build/tools/buildfarm/utils/hgtool.py'],
            'gittool.py': [PYTHON_WIN32, 'c:/builds/hg-shared/build/tools/buildfarm/utils/gittool.py'],
            'virtualenv': [PYTHON_WIN32, 'c:/mozilla-build/buildbotve/virtualenv.py'],
        }
    }
}

DEFAULT_CONFIG = PLATFORM_CONFIG[platform_name()]
DEFAULT_CONFIG.update({
    "find_links": [
        "http://pypi.pvt.build.mozilla.org/pub",
        "http://pypi.pub.build.mozilla.org/pub",
    ],
    'pip_index': False,
    'virtualenv_path': 'venv',
})

