from __future__ import print_function


def make_exec_app(application='DaVinci', version='v42r1'):
    """Function to create a temporary folder, creates a DaVinci folder
    and recursively copies the content of cwd into that folder to be tarred
    and uploaded as well."""
    import tempfile
    import os
    from distutils.dir_util import copy_tree

    from Ganga.GPI import prepareGaudiExec
    tmp = tempfile.mktemp()
    os.makedirs(tmp)
    app = prepareGaudiExec(application, version, tmp)
    location = app.directory
    print('Copying content in {} to {}'.format(os.getcwd(), location))
    copy_tree(os.getcwd(), location)
    return app
