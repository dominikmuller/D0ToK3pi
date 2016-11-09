"""
In order to normalise options files between modes, and between collision and
simulation, we use a helper module.
In order to use this module, we need to add its parent directory to the
PYTHONPATH.
This script does just that, and so must be called before any true options file,
e.g. in Ganga
    j = Job(application='DaVinci')
    j.application.optsfile= [
        '/path/to/module/options/add_helpers.py',
        '/path/to/module/options/my_options.py'
    ]
The path `/path/to/module/options` is then added to PYTHONPATH, and
`my_options` can call `import helpers` and the like.
If you want to use the options files, you should change the path below to
reflect your environment.
"""
import os
import sys
sys.path.append(os.getcwd())
