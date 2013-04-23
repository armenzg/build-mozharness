#!/usr/bin/env python
import os
config = {
    "default_actions": [
        'clobber',
        'checkout-sources',
        'get-blobs',
        'update-source-manifest',
        'build',
        'build-symbols',
        'build-update-testdata',
        'make-updates',
        'make-socorro-json',
        'prep-upload',
        'upload',
        'upload-source-manifest',
    ],
    "ssh_key": os.path.expanduser("~/.ssh/b2gbld_dsa"),
    "ssh_user": "b2gbld",
    "upload_remote_host": "pvtbuilds.pvt.build.mozilla.org",
    "upload_remote_basepath": "/pvt/mozilla.org/b2gotoro/tinderbox-builds",
    "upload_remote_nightly_basepath": "/pvt/mozilla.org/b2gotoro/nightly",
    "tooltool_servers": ["http://runtime-binaries.pvt.build.mozilla.org/tooltool/"],
    "gittool_share_base": "/builds/git-shared/git",
    "gittool_base_mirror_urls": [],
    "hgtool_share_base": "/builds/hg-shared",
    "hgtool_base_mirror_urls": ["http://hg-internal.dmz.scl3.mozilla.com"],
    "hgtool_base_bundle_urls": ["http://ftp.mozilla.org/pub/mozilla.org/firefox/bundles"],
    "exes": {
        "tooltool.py": "/tools/tooltool.py",
    },
    "manifest": {
        "upload_remote_host": "stage.mozilla.org",
        "upload_remote_basepath": "/pub/mozilla.org/b2g/manifests/%(version)s",
        "ssh_key": os.path.expanduser("~/.ssh/b2gbld_dsa"),
        "ssh_user": "b2gbld",
        "branches": {
            'mozilla-b2g18_v1_0_0': '1.0.0',
            'mozilla-b2g18_v1_0_1': '1.0.1',
            'mozilla-b2g18': '1.1.0',
            'mozilla-central': '2.0.0',
        },
        "translate_hg_to_git": True,
        "translate_base_url": "http://cruncher.build.mozilla.org/mapper",
        "target_suffix": "-eng",
    },
    "env": {
        "CCACHE_DIR": "/builds/ccache",
        "CCACHE_COMPRESS": "1",
        "CCACHE_UMASK": "002",
        "GAIA_OPTIMIZE": "1",
        "SYMBOL_SERVER_HOST": "symbolpush.mozilla.org",
        "SYMBOL_SERVER_USER": "b2gbld",
        "SYMBOL_SERVER_SSH_KEY": "/home/mock_mozilla/.ssh/b2gbld_dsa",
        "SYMBOL_SERVER_PATH": "/mnt/netapp/breakpad/symbols_b2g/",
        "POST_SYMBOL_UPLOAD_CMD": "/usr/local/bin/post-symbol-upload.py",
        "B2G_UPDATER": "1",
        "B2G_SYSTEM_APPS": "1",
    },
    "purge_minsize": 15,
    "clobberer_url": "http://clobberer.pvt.build.mozilla.org/index.php",
    "is_automation": True,
    "variant": "eng",
    "target_suffix": "-eng",
    "smoketest_config": {
        "devices": {
            "otoro": {
                "system_fs_type": "ext4",
                "system_location": "/dev/block/mmcblk0p19",
                "data_fs_type": "ext4",
                "data_location": "/dev/block/mmcblk0p22",
                "sdcard": "/mnt/sdcard",
                "sdcard_recovery": "/sdcard",
                "serials": ["full_otoro"],
            },
        },
        "public_key": os.path.abspath("build/target/product/security/testkey.x509.pem"),
        "private_key": os.path.abspath("build/target/product/security/testkey.pk8"),
    },
    "repo_mirror_dir": "/builds/git-shared/repo",
    "repo_remote_mappings": {
        'https://android.googlesource.com/': 'https://git.mozilla.org/external/aosp',
        'git://codeaurora.org/': 'https://git.mozilla.org/external/caf',
        'https://git.mozilla.org/b2g': 'https://git.mozilla.org/b2g',
        'git://github.com/mozilla-b2g/': 'https://git.mozilla.org/b2g',
        'git://github.com/mozilla/': 'https://git.mozilla.org/b2g',
        'https://git.mozilla.org/releases': 'https://git.mozilla.org/releases',
        'http://android.git.linaro.org/git-ro/': 'https://git.mozilla.org/external/linaro',
    },
}