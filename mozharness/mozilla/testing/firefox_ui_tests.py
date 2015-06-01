#!/usr/bin/env python
# ***** BEGIN LICENSE BLOCK *****
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
# ***** END LICENSE BLOCK *****
"""firefox_ui_updates.py

Author: Armen Zambrano G.
"""
import copy
import sys
import os

from mozharness.base.script import platform_name
from mozharness.base.python import (
    PreScriptAction,
    VirtualenvMixin,
    virtualenv_config_options,
)
from mozharness.mozilla.vcstools import VCSToolsScript

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


class FirefoxUITests(VCSToolsScript, VirtualenvMixin):
    config_options = [
        [['--firefox-ui-repo'], {
            'dest': 'firefox_ui_repo',
            'default': 'https://github.com/mozilla/firefox-ui-tests.git',
            'help': 'which firefox_ui_tests repo to use',
        }],
        [['--firefox-ui-branch'], {
            'dest': 'firefox_ui_branch',
            'default': 'master',
            'help': 'which branch to use for firefox_ui_tests',
        }],
    ] + copy.deepcopy(virtualenv_config_options)

    def __init__(self, config_options=[], all_actions=[], **kwargs):
        self.config_options += config_options

        if all_actions is None:
            # Default actions
            all_actions = [
                'clobber',
                'checkout',
                'create-virtualenv',
                'run-tests',
            ]

        super(FirefoxUITests, self).__init__(
            config_options=self.config_options,
            all_actions=all_actions,
            config=DEFAULT_CONFIG,
            **kwargs
        )

        self.firefox_ui_repo = self.config['firefox_ui_repo']
        self.firefox_ui_branch = self.config['firefox_ui_branch']

    def query_abs_dirs(self):
        if self.abs_dirs:
            return self.abs_dirs
        abs_dirs = super(FirefoxUITests, self).query_abs_dirs()

        dirs = {
            'fx_ui_dir': os.path.join(abs_dirs['abs_work_dir'], 'firefox_ui_tests'),
        }

        abs_dirs.update(dirs)
        self.abs_dirs = abs_dirs
        return self.abs_dirs


    def checkout(self):
        '''
        We checkout firefox_ui_tests and update to the right branch
        for it.
        '''
        dirs = self.query_abs_dirs()

        self.vcs_checkout(
            repo=self.firefox_ui_repo,
            dest=dirs['fx_ui_dir'],
            branch=self.firefox_ui_branch,
            vcs='gittool'
        )


    @PreScriptAction('create-virtualenv')
    def _pre_create_virtualenv(self, action):
        dirs = self.query_abs_dirs()

        self.register_virtualenv_module(
            'firefox-ui-tests',
            url=dirs['fx_ui_dir'],
        )


    def run_tests(self):
        pass
