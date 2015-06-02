#!/usr/bin/env python
# ***** BEGIN LICENSE BLOCK *****
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
# ***** END LICENSE BLOCK *****
"""vcstools.py

Author: Armen Zambrano G.
"""
import os
import stat

from mozharness.base.script import PreScriptAction
from mozharness.base.vcs.vcsbase import VCSScript

VCS_TOOLS = ('hgtool.py', 'gittool.py')


class VCSToolsScript(VCSScript):
    ''' This script allows us to fetch hgtool.py and gittool.py if
    we're running the script on developer mode.
    '''
    @PreScriptAction('checkout')
    def _pre_checkout(self, action):
        dirs = self.query_abs_dirs()

        if self.config.get('developer_mode'):
            # We put them on base_work_dir to prevent the clobber action
            # to delete them before we use them
            for vcs_tool in VCS_TOOLS:
                file_path = self.query_exe(vcs_tool)
                if not os.path.exists(file_path):
                    self.download_file(
                        url=self.config[vcs_tool],
                        file_name=file_path,
                    )
                    self.chmod(file_path, 0755)
        else:
            for vcs_tool in VCS_TOOLS:
                file_path = self.which(vcs_tool)
                if file_path is None:
                    file_path = self.query_exe(vcs_tool)

                    if os.path.isfile(file_path) and \
                       (os.stat(file_path).st_mode and stat.S_IRGRP):
                        self.critical("%s is not executable." % file_path)

                    self.fatal("This machine is missing %s, if this is your "
                               "local machine you can use --cfg "
                               "developer_config.py" % vcs_tool)
