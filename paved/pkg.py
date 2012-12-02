# -*- coding: utf-8 -*-
"""paved.pkg -- packaging tools for paved.
"""
from paver.easy import sh, task, consume_args, options, Bunch, path, needs
import tempfile
import textwrap

from . import paved
from . import util


try:
    import virtualenv
    has_virtualenv = True
except ImportError:
    has_virtualenv = False


__all__ = ['pip_install', 'easy_install']
if has_virtualenv:
    __all__ += ['pypi','pypi_pip','pypi_easy_install']


@task
@consume_args
def pip_install(args):
    """Send the given arguments to `pip install`.
    """
    util.pip_install(*args)


@task
def easy_install(args):
    """Send the given arguments to `easy_install`.
    """
    util.easy_install(*args)

if has_virtualenv:
    def install_test(installer, name):
        root = path(tempfile.mkdtemp(prefix=name + '_'))
#        info( 'root='+ root)
        script = root / 'start_virtualenv'
        
        txt = """
        def after_install(options, home_dir):
            assert not os.system('{installer} {name}')
        """.format(
                   name=name,
                   installer=root / 'testenv' / 'bin' / installer,
                   )
        
        script_text = virtualenv.create_bootstrap_script(textwrap.dedent(txt))
        script.write_text(script_text)
        script.chmod(0755)
        sh('./start_virtualenv testenv --no-site-packages', cwd=root)
    
    @task
    def pypi_pip(options, info):
        '''pip install package in an empty virtualenv to check for install errors.
        
        dependency: virtualenv 
        '''
        name=options.setup.name
        install_test('pip install', name)
    
    @task
    def pypi_easy_install(options, info):
        '''easy_install package in an empty virtualenv to check for install errors.
        
        dependency: virtualenv 
        '''
        name=options.setup.name
        install_test('easy_install', name)
        
    @task
    @needs(
           'pypi_easy_install',
           'pypi_pip', 
           )
    def pypi():
        '''pip install and easy_install package in an empty virtualenv to check for install errors.
        
        Recommended to run after upload.
        
        dependency: virtualenv 
        '''
        pass
