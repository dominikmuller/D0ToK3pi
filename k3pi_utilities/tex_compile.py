from __future__ import print_function

import os
from k3pi_config import config
import subprocess
import shutil
import tempfile
import logging as log

from . import helpers

# List of LaTeX packages always used when creating .tex documents
REQUIRED_PACKAGES = ['tikz', 'amsmath']


def patch_buffer_bug(filename):
    """Patch short buffer bug.

    In TVirtualPS, the object responsible for saving graphics, the maximum line
    length, defined by kMaxBuffer, is 250 characters. This is troublesome,
    because it can cause long lines to be split during a LaTeX sequence,
    leading to a syntax error.  This method joins lines that have been
    truncated, overwriting filename with the contents stripped of newlines.
    """
    patched = '{0}.patched'.format(filename)
    with open(patched, 'wt') as fout:
        with open(filename, 'rt') as fin:
            prevline = None
            for line in fin:
                # If the previous line was truncated, merge it with this one
                if prevline:
                    line = prevline + line
                    prevline = None
                # If this line ends with a character (before the newline), it
                # should be merged with the following line
                if line[-2].isalpha():
                    prevline = line[0:-1]
                    continue
                fout.write(line)
    helpers.move_file(patched, filename)


def make_tex(packages, texfile, sansserif=False):
    """Convert the LaTeX fragment at texfile to a full LaTeX document.

    The packages used will always include those defined by REQUIRED_PACKAGES.
    Keyword arguments:
    packages -- List of packages to included in the preamble with usepackage
    texfile -- Path to the .tex file to process
    sansserif -- Use a sans serif font if True (default: False)
    """
    all_packages = '\n'.join([
        '\\usepackage{{{0}}}'.format(p) for p in (packages + REQUIRED_PACKAGES)
    ])
    if sansserif:
        font_str = '\\usepackage[cm]{sfmath}\n'
        font_str += '\\renewcommand{\\familydefault}{\\sfdefault}'
    else:
        font_str = '\\usepackage{mathptmx}'

    # Double braces are replaced by single braces by format
    document = (
        '\\documentclass[11pt]{{article}}\n'
        '\\usepackage[active, tightpage]{{preview}}\n'
        '\\newcommand{{\\splitline}}[2]{{\n'
        '    \\genfrac{{}}{{}}{{0pt}}{{}}{{#1}}{{#2}}\n'
        '}}\n'
        '\\setlength\\PreviewBorder{{0pt}}\n'
        '{packages}\n'
        '\\usetikzlibrary{{patterns, shapes, plotmarks}}\n'
        '{fonts}\n'
        '\\begin{{document}}\n'
        '    \\begin{{preview}}\n'
        '        \\input{{"{input_file}"}}\n'
        '    \\end{{preview}}\n'
        '\\end{{document}}\n'
    ).format(
        packages=all_packages,
        fonts=font_str,
        input_file=os.path.abspath(texfile)
    )

    return document


def convert_tex_to_pdf(texfile, packages=None, shut_up=True, **kwargs):
    """Convert the .tex file to a .pdf file.

    **kwargs are passed to make_tex.
    Keyword arguments:
    texfile -- Name of the .tex file (including the extension)
    packages -- List of LaTeX packages to pass to make_tex (default: [])
    """
    log.debug('Converting {0}'.format(texfile))
    patch_buffer_bug(texfile)
    if not packages:
        packages = []

    # Create temporary directory
    temp_dir = tempfile.mkdtemp('', 'rootTeX-')

    header_filename = os.path.join(temp_dir, 'rootTeX-header.tex')
    log.debug('Header file : {0}'.format(header_filename))

    header_file = open(header_filename, 'w')
    header_file.write(make_tex(packages, texfile, **kwargs))
    header_file.close()

    compile_tex(header_filename, temp_dir, texfile.replace('.tex', '.pdf'),
                shut_up)

    # remove temporary directory
    shutil.rmtree(temp_dir)


def compile_tex(headerFileName, working_dir, output_name, shut_up=True):

    proc = subprocess.Popen(['lualatex', headerFileName],
                            cwd=working_dir, stdout=config.devnull)
    proc.communicate()

    retVal = proc.returncode

    if retVal is not 0:
        log.warn('Error compiling document {0}'.format(output_name))
    else:
        src = '{0}.pdf'.format(os.path.splitext(headerFileName)[0])
        helpers.move_file(src, output_name)

    return retVal is not 0
