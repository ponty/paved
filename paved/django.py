# -*- coding: utf-8 -*-
"""paved.django -- common tasks for django projects.
"""
from paver.easy import options, task, consume_args, Bunch
from paver.easy import BuildFailure

from . import paved
from . import util

util.update(
    options.paved,
    dict(
        django = Bunch(
            manage_py = None,
            project = None,
            syncdb = Bunch(
                fixtures = [],
                ),
            ),
        )
    )

__all__ = ['manage', 'call_manage', 'test', 'syncdb', 'shell', 'start']


@task
@consume_args
def manage(args):
    """Run the provided commands against Django's manage.py

    `options.paved.django.project`: the path to the django project
        files (where `settings.py` typically resides).

    `options.paved.django.manage_py`: the path where the django
        project's `manage.py` resides.
    """
    args = ' '.join(args)
    call_manage(args)


def call_manage(cmd):
    """Utility function to run commands against Django's `manage.py`.

    `options.paved.django.project`: the path to the django project
        files (where `settings.py` typically resides).

    `options.paved.django.manage_py`: the path where the django
        project's `manage.py` resides.
     """
    project = options.paved.django.project
    if project is None:
        raise BuildFailure("No project path defined. Use: options.paved.django.project = 'path.to.project'")
    manage_py = options.paved.django.manage_py
    if manage_py is None:
        manage_py = 'django-admin.py'
    else:
        manage_py = 'cd {manage_py.parent}; python ./{manage_py.name}'.format(**locals())
    util.shv('{manage_py} {cmd} --settings={project}'.format(**locals()))


@task
@consume_args
def test(args):
    """Run tests. Shorthand for `paver manage test`.
    """
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
    try:
        import django_extensions
        call_manage('shell_plus')
    except ImportError:
        info("Could not import django_extensions. Using default shell.")
        call_manage('shell')


@task
def start(info):
    """Run the dev server.

    Uses `django_extensions <http://pypi.python.org/pypi/django-extensions/0.5>`, if
    available, to provide `runserver_plus`.
    """
    try:
        import django_extensions
        call_manage('runserver_plus')
    except ImportError:
        info("Could not import django_extensions. Using default runserver.")
        call_manage('runserver')
