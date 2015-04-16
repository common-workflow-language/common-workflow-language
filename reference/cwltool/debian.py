import subprocess
import logging
import sys
import requests
import os
import apt
import apt_pkg
import apt.debfile

_logger = logging.getLogger("cwltool")

def install_package(package_name):
    cache = apt.cache.Cache()
    pkg = cache[package_name]
    if not pkg.installed:
        pkg.mark_install()
        cache.commit()


def check_depends(string):
    apt_pkg.init_config()
    apt_pkg.init_system()
    for dep in apt_pkg.parse_depends(string):
        if not apt_pkg.check_dep(dep):
            return False
    return True


def install_depends(string, dry_run=False):
    for dep in apt_pkg.parse_depends(string):
        if not apt_pkg.check_dep(dep) and dry_run is False:
            install_package(dep[0])


def check_depends_from_environment(requirements, hints, dry_run=False):
    if requirements:
        for r in reversed(requirements):
            if r["class"] == "DebianRequirement":
                if 'DebianDepends' in r:
                    install_depends(r['DebianDepends'])
    if hints:
        for r in reversed(hints):
            if r["class"] == "DebianRequirement":
                if 'DebianDepends' in r:
                    install_depends(r['DebianDepends'])
    return None
