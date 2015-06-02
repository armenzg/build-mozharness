from mozharness.base.script import platform_name

PLATFORM_CONFIG = {
    'linux64': {
        'update_verify_config': 'mozRelease-firefox-linux64.cfg'
    },
    'macosx64': {
        'update_verify_config': 'mozRelease-firefox-macosx.cfg'
    },
    'win32': {
        'update_verify_config': 'mozRelease-firefox-win32.cfg'
    },
}

config = PLATFORM_CONFIG[platform_name()]
config.update({
    'firefox_ui_branch': 'mozilla-beta'
}
