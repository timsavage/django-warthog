from fabric.api import *


VERSION_HEADER = """VERSION = %s
__version__ = '.'.join(map(str, VERSION))
"""

def write_version(version):
    with open('warthog/__init__.py', 'w') as init:
        init.write(VERSION_HEADER % str(version))


def parse_version(value):
    try:
        major, minor, revision = value.split('.')
        if '-' in revision:
            revision, status = revision.split('-')
            return int(major), int(minor), int(revision), status
        else:
            return int(major), int(minor), int(revision)
    except ValueError, ve:
        return None


def get_version():
    from warthog import VERSION
    version = '.'.join(map(str, VERSION[:3]))
    if len(VERSION) == 4:
        version += '-%s' % VERSION[3]
    return version


@task
def version():
    print get_version()


@task(alias='r')
def release():
    version_string = get_version()

    # Run tests
    local('python manage.py')

    print "Current version:", version_string
    version = None
    while version is None:
        version_string = prompt('New version number?')
        version = parse_version(version_string)
        if version is None:
            print "Invalid version number, please try again."

    # Write version number to file
    write_version(version)

    # Commit back into HG
    local('hg ci warthog/__init__.py -m "Bumped version to %s"' % version_string)

    # Tag release
    local('hg tag "Release-%s"' % version_string)

    # Upload to PyPi
    if prompt("Upload to PyPi?", default='Y', validate=r'^[yYnN]$').lower() == 'y':
        local('python setup.py sdist upload')
