#!/usr/bin/env python
"""signdebs.py

Usage:
    signdebs.py [args]
"""

import os
import shutil
import subprocess
import sys
import urllib2
from urllib2 import URLError, HTTPError

# load modules from parent dir
sys.path[0] = os.path.dirname(sys.path[0])

import Log
reload(Log)
from Log import SimpleFileLogger, BasicFunctions

import Config
reload(Config)
from Config import SimpleConfig



# MaemoDebSigner {{{1
class MaemoDebSigner(SimpleConfig, BasicFunctions):
    def __init__(self, configFile=None):
        """I wanted to inherit BasicFunctions in SimpleFileLogger but
        that ends up not carrying down to this object since SimpleConfig
        doesn't inherit the logger, just has a self.logObj.
        """
        SimpleConfig.__init__(self, configFile=configFile)
        BasicFunctions.__init__(self)

    def parseArgs(self):
        """I want to change this to send the list of options to
        Config.parseArgs() but don't know a way to intuitively do that.
        Each add_option seems to take *args and **kwargs, so it would be

            complexOptionList = [
             [["-f", "--file"], {"dest": "filename", "help": "blah"}],
             [*args, **kwargs],
             [*args, **kwargs],
             ...
            ]
            SimpleConfig.parseArgs(self, options=complexOptionList)

        Not very pretty, but having the options logic in every inheriting
        script isn't that great either.
        """
        parser = SimpleConfig.parseArgs(self)
        parser.add_option("--locale", action="append", dest="locales",
                          type="string",
                          help="Specify the locale(s) to repack")
        parser.add_option("--platform", action="append", dest="platforms",
                          type="string",
                          help="Specify the platform(s) to repack")
        parser.add_option("--debname", action="store", dest="debname",
                          type="string",
                          help="Specify the name of the deb")
        (options, args) = parser.parse_args()
        for option in parser.variables:
             self.setVar(option, getattr(options, option))

    def queryDebName(self, debNameUrl=None):
        debName = self.queryVar('debname')
        if debName:
            return debName
        if debNameUrl:
            self.info('Getting debName from %s' % debNameUrl)
            try:
                ul = urllib2.build_opener()
                fh = ul.open(debNameUrl)
                debName = fh.read()[:-1] # chomp
                self.debug('Deb name is %s' % debName)
                return debName
            except HTTPError, e:
                self.fatal("HTTP Error: %s %s" % (e.code, url))
            except URLError, e:
                self.fatal("URL Error: %s %s" % (e.code, url))

    def clobberRepoDir(self):
        repoDir = self.queryVar("repoDir")
        if not repoDir:
            self.fatal("clobberRepoDir: repoDir not set!")
        if os.path.exists(repoDir):
            self.rmtree(repoDir)

    def queryLocales(self, platform, platformConfig=None):
        locales = self.queryVar("locales")
        if not locales:
            locales = []
            if not platformConfig:
                platformConfig = self.queryVar("platformConfig")
            pf = platformConfig[platform]
            localesFile = self.queryVar("localesFile")
            if "multiDirUrl" in pf:
                locales.append("multi")
            if "enUsDirUrl" in pf:
                locales.append("en-US")
            if "l10nDirUrl" in pf and localesFile:
                """This assumes all locales in the l10n json file
                are applicable. If not, we'll have to parse the json
                for matching platforms.
                """
                localesJson = self.parseConfigFile(localesFile)
                locales.extend(localesJson.keys())
        return locales

    def createRepos(self):
        repoDir = self.queryVar("repoDir")
        platformConfig = self.queryVar("platformConfig")
        platforms = self.queryVar("platforms")
        if not platforms:
            platforms = platformConfig.keys()

        self.clobberRepoDir()
        self.mkdir_p(repoDir)

        for platform in platforms:
            """This assumes the same deb name for each locale in a platform.
            """
            self.info("###%s###" % platform)
            pf = platformConfig[platform]
            debName = self.queryDebName(debNameUrl=pf['debNameUrl'])
            locales = self.queryLocales(platform, platformConfig=platformConfig)
            for locale in locales:
                self.debug("Locale %s" % locale)



# __main__ {{{1
if __name__ == '__main__':
    debSigner = MaemoDebSigner(configFile='%s/configs/deb_repos/trunk_nightly.json' % sys.path[0])
    # TODO check out appropriate hg repos
    debSigner.createRepos()

#    for platform in platforms:
#        signObj = MaemoDebSigner(configJson=platformConfig)
#        print signObj.debNameUrl
#        debName = signObj.getDebName()
#        print debName
#
#        # Assuming the deb name is consistent across all locales for a platform
#
#        for locale in platformLocales:
#            repoName = config['repoName'].replace('LOCALE', locale)
#            installFile = platformConfig['installFile'].replace('LOCALE', locale)
#            url = ''
#            if locale == 'multi':
#                url = platformConfig['multiDirUrl']
#            elif locale == 'en-US':
#                url = platformConfig['enUsDirUrl']
#            else:
#                url = '%s/%s' % (platformConfig['l10nDirUrl'], locale)
#            url += '/%s' % debName
#            if not downloadFile(url, debName):
#                print "Skipping %s ..." % locale
#                continue
#
#            binaryDir = '%s/%s/dists/%s/%s/binary-armel' % \
#                        (config['repoDir'], repoName, platform,
#                         config['section'])
#            absBinaryDir = '%s/%s' % (config['baseWorkDir'], binaryDir)
#            mkdir_p(absBinaryDir)
#            shutil.move(debName, absBinaryDir)
#            signRepo(config, repoName, platform)
#
#            # TODO create install file
#            # TODO upload
