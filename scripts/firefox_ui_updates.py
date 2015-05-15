#!/usr/bin/env python
# ***** BEGIN LICENSE BLOCK *****
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
# ***** END LICENSE BLOCK *****
"""firefox_ui_updates.py

Author: Armen Zambrano G.
"""
import sys
import os

# load modules from parent dir
sys.path.insert(1, os.path.dirname(sys.path[0]))

from mozharness.base.script import PreScriptAction
from mozharness.mozilla.testing.firefox_ui_tests import FirefoxUITests


class FirefoxUIUpdates(FirefoxUITests):
    # This will be a list containing one item per release based on configs
    # from tools/release/updates/*cfg
    releases = None

    def __init__(self):
        config_options = [
            [['--tools-repo'], {
                'dest': 'tools_repo',
                'help': 'which tools repo to check out',
            }],
            [['--tools-revision'], {
                'dest': 'tools_revision',
                'help': 'which revision/tag to use for tools',
            }],
            [['--update-config-file'], {
                'dest': 'update_config_file',
                'help': 'which revision/tag to use for firefox_ui_tests',
            }],
        ]

        super(FirefoxUIUpdates, self).__init__(
            config_options=config_options,
            all_actions=[
                'clobber',
                'checkout',
                'create-virtualenv',
                'read-configuration-file',
                'run-tests',
            ],
        )

        dirs = self.query_abs_dirs()

        self.updates_config_file = os.path.join(
            dirs['tools_dir'], 'release', 'updates',
            self.config['update_config_file']
        )

        self.tools_repo = self.config.get('tools_repo',
                                          'http://hg.mozilla.org/build/tools')


    def query_abs_dirs(self):
        if self.abs_dirs:
            return self.abs_dirs
        abs_dirs = super(FirefoxUIUpdates, self).query_abs_dirs()

        dirs = {
            'tools_dir': os.path.join(abs_dirs['abs_work_dir'], 'tools'),
        }

        abs_dirs.update(dirs)
        self.abs_dirs = abs_dirs
        return self.abs_dirs

    def checkout(self):
        '''
        This checkouts the tools repo because it contains the configuration
        files about which locales to test.

        We also checkout firefox_ui_tests and update to the right branch
        for it.
        '''
        super(FirefoxUIUpdates, self).checkout()
        dirs = self.query_abs_dirs()

        self.vcs_checkout(
            repo=self.tools_repo,
            dest=dirs['tools_dir'],
            revision='default',
            vcs='hgtool'
        )


    def read_configuration_file(self):
        '''
        Each line of the releng configuration files look like this:
            NOTE: I'm showing each pair of information as a new line but in reality
            there is one white space separting them.

            release="38.0"
            product="Firefox"
            platform="Linux_x86_64-gcc3"
            build_id="20150429135941"
            locales="ach af ... zh-TW"
            channel="beta-localtest"
            patch_types="complete partial"
            from="/firefox/releases/38.0b9/linux-x86_64/%locale%/firefox-38.0b9.tar.bz2"
            aus_server="https://aus4.mozilla.org"
            ftp_server_from="http://stage.mozilla.org/pub/mozilla.org"
            ftp_server_to="http://stage.mozilla.org/pub/mozilla.org"
            to="/firefox/candidates/38.0-candidates/build2/linux-x86_64/%locale%/firefox-38.0.tar.bz2"

        We will store this information in self.releases as a list of dict per release.
        '''
        self.releases = []
        lines = []
        with open(self.updates_config_file, 'r') as f:
            lines = f.readlines()

        for line in lines:
            release_info = {}
            # The left double quote is handled here
            blocks = line.split('" ')
            # The right double quote is handled here
            for b in blocks:
                key, value = b.split('="')

                # We filter out releases that are older than Gecko 38
                if key == 'release' and value < '38.0':
                    release_info = None
                    break

                if key == 'locales':
                    # locales is the only key with multiple values separated by a white space
                    release_info[key] = value.split(' ')
                else:
                    # Store value
                    release_info[key] = value

            if release_info is not None:
                self.debug('Read information about %s %s' % \
                          (release_info['build_id'], release_info['release']))
                self.releases.append(release_info)

    @PreScriptAction('run-tests')
    def _pre_run_tests(self, action):
        if self.releases is None:
            # XXX: re-evaluate this idea
            self.critical('You need to set the list of releases')
            exit(1)

    def run_tests(self):
        dirs = self.query_abs_dirs()
        bin_dir = os.path.dirname(self.query_python_path())
        fx_ui_tests_bin = os.path.join(bin_dir, 'firefox-ui-update')
        harness_log=os.path.join(dirs['abs_work_dir'], 'harness.log')

        for release in self.releases:
            for locale in release['locales']:
                # Determine from where to download the file
                url = '%s/%s' % (
                    release['ftp_server_from'],
                    release['from'].replace('%locale%', locale)
                )

                file_path = self.download_file(
                    url=url,
                    parent_dir=dirs['abs_work_dir']
                )

                # Build the command
                cmd = [
                    fx_ui_tests_bin,
                    '--installer', file_path,
                    '--update-channel', release['channel'],
                    '--log-unittest=harness.log',
                    '--gecko-log=gecko.log',
                ]

                return_code = self.run_command(cmd, cwd=dirs['abs_work_dir'], output_timeout=100)

                self.info('== Dumping output of harness ==')
                with open(harness_log, 'r') as f:
                    contents = f.readlines()
                    self.warning(contents)
                self.info('== End of harness output ==')

                # Return more output if we fail
                if return_code != 0:
                    self.warning('FAIL: firefox-ui-update has failed for')
                    self.warning('== Dumping gecko output ==')
                    with open('gecko.txt', 'r') as f:
                        contents = f.readlines()
                        self.warning(contents)
                    self.warning('== End of gecko output ==')

                self.rm(file_path)
                self.rm(harness_log)


if __name__ == '__main__':
    myScript = FirefoxUIUpdates()
    myScript.run_and_exit()
