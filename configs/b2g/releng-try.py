#!/usr/bin/env python
import os
config = {
    "default_actions": [
        'purge-builds',
        'checkout-gecko',
        'download-gonk',
        'unpack-gonk',
        'build',
        'prep-upload',
        'upload',
    ],
    "ssh_key": os.path.expanduser("~/.ssh/b2gtry_dsa"),
    "ssh_user": "b2gtry",
    "upload_remote_host": "pvtbuilds2.dmz.scl3.mozilla.com",
    #"upload_remote_host": "dev-stage01.srv.releng.scl3.mozilla.com",
    "upload_remote_basepath": "/pub/mozilla.org/b2g/try-builds",
    "enable_try_uploads": True,
    "tooltool_servers": ["http://runtime-binaries.pvt.build.mozilla.org/tooltool/"],
    "vcs_share_base": "/builds/hg-shared",
    "vcs_base_mirror_urls": ["http://hg-internal.dmz.scl3.mozilla.com"],
    "vcs_base_bundle_urls": ["http://ftp.mozilla.org/pub/mozilla.org/firefox/bundles"],
    "exes": {
        "tooltool.py": "/tools/tooltool.py",
    },
    "env": {
        "CCACHE_DIR": "/builds/ccache",
        "CCACHE_COMPRESS": "1",
        "CCACHE_UMASK": "002",
    },
    "purge_minsize": 10,
    #"clobberer_url": "http://clobberer-stage.pvt.build.mozilla.org/index.php",
    "clobberer_url": "http://clobberer.pvt.build.mozilla.org/index.php",
}
