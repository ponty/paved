# -*- coding: utf-8 -*-
"""paved.django -- common tasks for django projects.
"""
from paver.easy import options, task, consume_args, path, Bunch
from paver.easy import BuildFailure

from . import paved
from . import util

util.update(
    options.paved,
    dict(
        django = Bunch(
            manage_py = None,
            project = None,
            settings = '',
            syncdb = Bunch(
                fixtures = [],
                ),
            test = Bunch(
                settings = None,
                ),
            ),
        )
    )

__all__ = ['manage', 'call_manage', 'test', 'syncdb', 'shell', 'start']


@task
@consume_args
def manage(args):
    """Run the provided commands against Django's manage.py

    `options.paved.django.settings`: the dotted path to the django
        project module containing settings.

    `options.paved.django.manage_py`: the path where the django
        project's `manage.py` resides.
    """
    args = ' '.join(args)
    call_manage(args)


def call_manage(cmd):
    """Utility function to run commands against Django's `django-admin.py`/`manage.py`.

    `options.paved.django.project`: the path to the django project
        files (where `settings.py` typically resides).

    `options.paved.django.manage_py`: the path where the django
        project's `manage.py` resides.
     """
    settings = options.paved.django.settings
    if settings is None:
        raise BuildFailure("No settings path defined. Use: options.paved.django.settings = 'path.to.project.settings'")
    manage_py = options.paved.django.manage_py
    if manage_py is None:
        manage_py = 'django-admin.py'
    else:
        manage_py = path(manage_py)
        manage_py = 'cd {manage_py.parent}; python ./{manage_py.name}'.format(**locals())
    util.shv('{manage_py} {cmd} --settings={settings}'.format(**locals()))


@task
@consume_args
def test(args):
    """Run tests. Shorthand for `paver manage test`.
    """
    if options.paved.django.test.settings is not None:
        options.paved.django.settings = options.paved.django.test.settings
    cmd = args and 'test %s' % ' '.join(options.args) or 'test'
    call_manage(cmd)


@task
@consume_args
def syncdb(args):
    """Update the database with model schema. Shorthand for `paver manage syncdb`.
    """
    cmd = args and 'syncdb %s' % ' '.join(options.args) or 'syncdb --noinput'
    call_manage(cmd)
    for fixture in options.paved.django.syncdb.fixtures:
        call_manage("loaddata %s" % fixture)


@task
def shell(info):
    """Run the ipython shell. Shorthand for `paver manage shell`.

    Uses `django_extensions <http://pypi.python.org/pypi/django-extensions/0.5>`, if
    available, to provide `shell_plus`.
    """
    cmd = 'shell'

    from django.conf import settings
    try:
        import django_extensions
        if 'django_extensions' in settings.INSTALLED_APPS:
            cmd = 'shell_plus'
        else:
            info('django_extensions is installed, but does not appear in settings.INSTALLED_APPS. Using default shell.')
    except ImportError:
        info("Could not import django_extensions. Using default shell.")

    call_manage(cmd)


@task
def start(info):
    """Run the dev server.

    Uses `django_extensions <http://pypi.python.org/pypi/django-extensions/0.5>`, if
    available, to provide `runserver_plus`.
    """
    cmd = 'runserver'

    from django.conf import settings
    try:
        import django_extensions
        if 'django_extensions' in settings.INSTALLED_APPS:
            cmd = 'runserver_plus'
        else:
            info('django_extensions is installed, but does not appear in settings.INSTALLED_APPS. Using default runserver.')
    except ImportError:
        info("Could not import django_extensions. Using default runserver.")

    call_manage(cmd)
