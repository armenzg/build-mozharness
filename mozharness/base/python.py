#!/usr/bin/env python
# ***** BEGIN LICENSE BLOCK *****
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
# ***** END LICENSE BLOCK *****
'''Python usage, esp. virtualenv.
'''

import os

from mozharness.base.script import (
    PostScriptAction,
    PostScriptRun,
    PreScriptAction,
)
from mozharness.base.errors import VirtualenvErrorList
from mozharness.base.log import WARNING, FATAL

# Virtualenv {{{1
virtualenv_config_options = [
    [["--venv-path", "--virtualenv-path"], {
        "action": "store",
        "dest": "virtualenv_path",
        "default": "venv",
        "help": "Specify the path to the virtualenv top level directory"
    }],
    [["--virtualenv"], {
        "action": "store",
        "dest": "virtualenv",
        "help": "Specify the virtualenv executable to use"
    }],
    [["--pypi-url"], {
        "action": "store",
        "dest": "pypi_url",
        "help": "Base URL of Python Package Index (default http://pypi.python.org/simple/)"
    }],
    [["--find-links"], {
        "action": "extend",
        "dest": "find_links",
        "help": "URL to look for packages at"
    }],
    [["--pip-index"], {
        "action": "store_true",
        "default": True,
        "dest": "pip_index",
        "help": "Use pip indexes (default)"
    }],
    [["--no-pip-index"], {
        "action": "store_false",
        "dest": "pip_index",
        "help": "Don't use pip indexes"
    }],
]


class VirtualenvMixin(object):
    '''BaseScript mixin, designed to create and use virtualenvs.

    Config items:
     * virtualenv_path points to the virtualenv location on disk.
     * virtualenv_modules lists the module names.
     * MODULE_url list points to the module URLs (optional)
    Requires virtualenv to be in PATH.
    Depends on ScriptMixin
    '''
    python_paths = {}
    site_packages_path = None

    def __init__(self, *args, **kwargs):
        self._virtualenv_modules = []
        super(VirtualenvMixin, self).__init__(*args, **kwargs)

    def register_virtualenv_module(self, name, url=None, method=None,
            requirements=None):
        """Register a module to be installed with the virtualenv.

        This method can be called up until create_virtualenv() to register
        modules that should be installed in the virtualenv.

        See the documentation for install_module for how the arguments are
        applied.
        """
        self._virtualenv_modules.append((name, url, method, requirements))

    def query_virtualenv_path(self):
        c = self.config
        dirs = self.query_abs_dirs()
        if 'abs_virtualenv_dir' in dirs:
            return dirs['abs_virtualenv_dir']
        if os.path.isabs(c['virtualenv_path']):
            return c['virtualenv_path']
        return os.path.join(dirs['abs_work_dir'], c['virtualenv_path'])

    def query_python_path(self, binary="python"):
        """Return the path of a binary inside the virtualenv, if
        c['virtualenv_path'] is set; otherwise return the binary name.
        Otherwise return None
        """
        self._check_existing_virtualenv()
        if binary not in self.python_paths:
            bin_dir = 'bin'
            if self._is_windows():
                bin_dir = 'Scripts'
            virtualenv_path = self.query_virtualenv_path()
            if virtualenv_path:
                self.python_paths[binary] = os.path.abspath(os.path.join(virtualenv_path, bin_dir, binary))
            else:
                self.python_paths[binary] = self.query_exe(binary)
        return self.python_paths[binary]

    def query_python_site_packages_path(self):
        if self.site_packages_path:
            return self.site_packages_path
        python = self.query_python_path()
        self.site_packages_path = self.get_output_from_command(
            [python, '-c',
             'from distutils.sysconfig import get_python_lib; ' +
             'print(get_python_lib())'])
        return self.site_packages_path

    def package_versions(self, pip_freeze_output=None, error_level=WARNING, log_output=False):
        """
        reads packages from `pip freeze` output and returns a dict of
        {package_name: 'version'}
        """
        packages = {}

        if pip_freeze_output is None:
            # get the output from `pip freeze`
            pip = self.query_python_path("pip")
            if not pip:
                self.log("package_versions: Program pip not in path", level=error_level)
                return {}
            pip_freeze_output = self.get_output_from_command([pip, "freeze"], silent=True)
            if not isinstance(pip_freeze_output, basestring):
                self.fatal("package_versions: Error encountered running `pip freeze`: %s" % pip_freeze_output)

        for line in pip_freeze_output.splitlines():
            # parse the output into package, version
            line = line.strip()
            if not line:
                # whitespace
                continue
            if line.startswith('-'):
                # not a package, probably like '-e http://example.com/path#egg=package-dev'
                continue
            if '==' not in line:
                self.fatal("pip_freeze_packages: Unrecognized output line: %s" % line)
            package, version = line.split('==', 1)
            packages[package] = version

        if log_output:
            self.info("Current package versions:")
            for package in packages:
                self.info("  %s == %s" % (package, packages[package]))

        return packages

    def is_python_package_installed(self, package_name, error_level=WARNING):
        """
        Return whether the package is installed
        """
        packages = self.package_versions(error_level=error_level).keys()
        return package_name.lower() in [package.lower() for package in packages]

    def _check_existing_virtualenv(self, error_level=WARNING):
        if 'VIRTUAL_ENV' in os.environ:
            self.log("VIRTUAL_ENV %s set; this may break mozharness virtualenv calls!" % os.environ['VIRTUAL_ENV'],
                     level=error_level)
            return True

    def install_module(self, module=None, module_url=None, install_method=None,
                       requirements=()):
        """
        Install module via pip.

        module_url can be a url to a python package tarball, a path to
        a directory containing a setup.py (absolute or relative to work_dir)
        or None, in which case it will default to the module name.

        requirements is a list of pip requirements files.  If specified, these
        will be combined with the module_url (if any), like so:

        pip install -r requirements1.txt -r requirements2.txt module_url
        """
        c = self.config
        dirs = self.query_abs_dirs()
        venv_path = self.query_virtualenv_path()
        self.info("Installing %s into virtualenv %s" % (module, venv_path))
        if not module_url:
            module_url = module
        if install_method in (None, 'pip'):
            if not module_url and not requirements:
                self.fatal("Must specify module and/or requirements")
            pip = self.query_python_path("pip")
            command = [pip, "install"]
            pypi_url = c.get("pypi_url")
            if pypi_url:
                command += ["--pypi-url", pypi_url]
            virtualenv_cache_dir = c.get("virtualenv_cache_dir")
            if virtualenv_cache_dir:
                self.mkdir_p(virtualenv_cache_dir)
                command += ["--download-cache", virtualenv_cache_dir]
            for requirement in requirements:
                command += ["-r", requirement]
            if c.get('find_links') and not c["pip_index"]:
                command += ['--no-index']
        elif install_method == 'easy_install':
            if not module:
                self.fatal("module parameter required with install_method='easy_install'")
            if requirements:
                # Install pip requirements files separately, since they're
                # not understood by easy_install.
                self.install_module(requirements=requirements,
                                    install_method='pip')
            # Allow easy_install to be overridden by
            # self.config['exes']['easy_install']
            default = 'easy_install'
            if self._is_windows():
                # Don't invoke `easy_install` directly on windows since
                # the 'install' in the executable name hits UAC
                # - http://answers.microsoft.com/en-us/windows/forum/windows_7-security/uac-message-do-you-want-to-allow-the-following/bea30ad8-9ef8-4897-aab4-841a65f7af71
                # - https://bugzilla.mozilla.org/show_bug.cgi?id=791840
                default = [self.query_python_path(), self.query_python_path('easy_install-script.py')]
            command = self.query_exe('easy_install', default=default, return_type="list")
        else:
            self.fatal("install_module() doesn't understand an install_method of %s!" % install_method)

        # Add --find-links pages to look at
        for link in c.get('find_links', []):
            command.extend(["--find-links", link])

        # module_url can be None if only specifying requirements files
        if module_url:
            command += [module_url]

        # Allow for errors while building modules, but require a
        # return status of 0.
        if self.run_command(command,
                            error_list=VirtualenvErrorList,
                            cwd=dirs['abs_work_dir']) != 0:
            self.fatal("Unable to install %s!" % module_url)

    def create_virtualenv(self, modules=(), requirements=()):
        """
        Create a python virtualenv.

        The virtualenv exe can be defined in c['virtualenv'] or
        c['exes']['virtualenv'], as a string (path) or list (path +
        arguments).

        c['virtualenv_python_dll'] is an optional config item that works
        around an old windows virtualenv bug.

        virtualenv_modules can be a list of module names to install, e.g.

            virtualenv_modules = ['module1', 'module2']

        or it can be a list of dicts that define a module: url-or-path,
        or a combination.

            virtualenv_modules = [
                'module1',
                {'module2': 'http://url/to/package'},
                {'module3': os.path.join('path', 'to', 'setup_py', 'dir')},
            ]

        virtualenv_requirements is an optional list of pip requirements files to
        use when invoking pip, e.g.,

            virtualenv_requirements = [
                '/path/to/requirements1.txt',
                '/path/to/requirements2.txt'
            ]
        """
        c = self.config
        dirs = self.query_abs_dirs()
        venv_path = self.query_virtualenv_path()
        self._check_existing_virtualenv()
        self.info("Creating virtualenv %s" % venv_path)
        virtualenv = c.get('virtualenv', self.query_exe('virtualenv'))
        if isinstance(virtualenv, str):
            if not os.path.exists(virtualenv) and not self.which(virtualenv):
                self.add_summary("The executable '%s' is not found; not creating virtualenv!" % virtualenv, level=FATAL)
                return -1
            # allow for [python, virtualenv] in config
            virtualenv = [virtualenv]

        # https://bugs.launchpad.net/virtualenv/+bug/352844/comments/3
        # https://bugzilla.mozilla.org/show_bug.cgi?id=700415#c50
        if c.get('virtualenv_python_dll'):
            # We may someday want to copy a differently-named dll, but
            # let's not think about that right now =\
            dll_name = os.path.basename(c['virtualenv_python_dll'])
            target = self.query_python_path(dll_name)
            scripts_dir = os.path.dirname(target)
            self.mkdir_p(scripts_dir)
            self.copyfile(c['virtualenv_python_dll'], target, error_level=WARNING)
        else:
            self.mkdir_p(dirs['abs_work_dir'])

        # make this list configurable?
        for module in ('distribute', 'pip'):
            if c.get('%s_url' % module):
                self.download_file(c['%s_url' % module],
                                   parent_dir=dirs['abs_work_dir'])

        virtualenv_options = c.get('virtualenv_options',
                                   ['--no-site-packages', '--distribute'])

        self.run_command(virtualenv + virtualenv_options + [venv_path],
                         cwd=dirs['abs_work_dir'],
                         error_list=VirtualenvErrorList,
                         halt_on_failure=True)
        if not modules:
            modules = c.get('virtualenv_modules', [])
        if not requirements:
            requirements = c.get('virtualenv_requirements', [])
        if not modules and requirements:
            self.install_module(requirements=requirements,
                                install_method='pip')
        for module in modules:
            module_url = module
            if isinstance(module, dict):
                (module, module_url) = module.items()[0]
            else:
                module_url = self.config.get('%s_url' % module, module_url)
            install_method = 'pip'
            if module in ('pywin32',):
                install_method = 'easy_install'
            self.install_module(module=module,
                                module_url=module_url,
                                install_method=install_method,
                                requirements=requirements)

        for module, url, method, requirements in self._virtualenv_modules:
            self.install_module(module=module, module_url=url,
                install_method=method, requirements=requirements or ())

        self.info("Done creating virtualenv %s." % venv_path)

        self.package_versions(log_output=True)

    def activate_virtualenv(self):
        """Import the virtualenv's packages into this Python interpreter."""
        bin_dir = os.path.dirname(self.query_python_path())
        activate = os.path.join(bin_dir, 'activate_this.py')
        execfile(activate, dict(__file__=activate))


class ResourceMonitoringMixin(object):
    """Provides resource monitoring capabilities to scripts.

    When this class is in the inheritance chain, resource usage stats of the
    executing script will be recorded.

    This class requires the VirtualenvMixin in order to install a package used
    for recording resource usage.

    While we would like to record resource usage for the entirety of a script,
    since we require an external package, we can only record resource usage
    after that package is installed (as part of creating the virtualenv).
    That's just the way things have to be.
    """
    def __init__(self, *args, **kwargs):
        super(ResourceMonitoringMixin, self).__init__(*args, **kwargs)

        self.register_virtualenv_module('psutil==0.7.1', method='pip')
        self.register_virtualenv_module('mozsystemmonitor==0.0.0', method='pip')
        self._resource_monitor = None

    @PostScriptAction('create-virtualenv')
    def _start_resource_monitoring(self, action, success=None):
        self.activate_virtualenv()

        from mozsystemmonitor.resourcemonitor import SystemResourceMonitor

        self.info("Starting resource monitoring.")
        self._resource_monitor = SystemResourceMonitor(poll_interval=1.0)
        self._resource_monitor.start()

    @PreScriptAction
    def _resource_record_pre_action(self, action):
        # Resource monitor isn't available until after create-virtualenv.
        if not self._resource_monitor:
            return

        self._resource_monitor.begin_phase(action)

    @PostScriptAction
    def _resource_record_post_action(self, action, success=None):
        # Resource monitor isn't available until after create-virtualenv.
        if not self._resource_monitor:
            return

        self._resource_monitor.finish_phase(action)

    @PostScriptRun
    def _resource_record_post_run(self):
        if not self._resource_monitor:
            return

        self._resource_monitor.stop()
        self._log_resource_usage()

    def _log_resource_usage(self):
        rm = self._resource_monitor

        if rm.start_time is None:
            return

        def resources(phase):
            cpu_percent = rm.aggregate_cpu_percent(phase=phase, per_cpu=False)
            cpu_times = rm.aggregate_cpu_times(phase=phase, per_cpu=False)
            io = rm.aggregate_io(phase=phase)

            return cpu_percent, cpu_times, io

        def log_usage(prefix, duration, cpu_percent, cpu_times, io):
            message = '{prefix} - Wall time: {duration:.0f}s; ' \
                'CPU: {cpu_percent:.0f}%; ' \
                'Read bytes: {io_read_bytes}; Write bytes: {io_write_bytes}; ' \
                'Read time: {io_read_time}; Write time: {io_write_time}'

            self.info(message.format(prefix=prefix, duration=duration,
                cpu_percent=cpu_percent, io_read_bytes=io.read_bytes,
                io_write_bytes=io.write_bytes, io_read_time=io.read_time,
                io_write_time=io.write_time))

        cpu_percent, cpu_times, io = resources(None)
        duration = rm.end_time - rm.start_time

        log_usage('Total resource usage', duration, cpu_percent, cpu_times, io)

        for phase in rm.phases.keys():
            start_time, end_time = rm.phases[phase]
            cpu_percent, cpu_times, io = resources(phase)
            log_usage(phase, end_time - start_time, cpu_percent, cpu_times, io)


# __main__ {{{1

if __name__ == '__main__':
    '''TODO: unit tests.
    '''
    pass
