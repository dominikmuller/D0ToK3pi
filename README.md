# D0ToK3pi


## First time install

Preparing to use on LXPlus:

Use a recent root environment. To match the one expected, run:

```
lb-run LCG/84 $SHELL
```

where `$SHELL` is your shell of choice. If you are not in this environment for setup, the `mkvirtualenv` step will fail with a `libpython` error.

Make sure `.local/bin` is near the beginning of your path.

```
pip install --user --upgrade pip
pip install --user virtualenv virtualenvwrapper
```

Add the following to your `~/.bashrc` file:

```
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME/Devel
source $HOME/.local/bin/virtualenvwrapper.sh
```

If using zsh, this should be your `.zshrc` file, or if using oh-my-zsh, this can be added with the virtualenvwrapper plugin.

> Note on zsh:
> This should be a custom build, the one on LXPlus is buggy.

After reruning your bashrc, you'll need to make a k3pi environment:

```
mkvirtualenv k3pi
pip install numpy scipy matplotlib
pip install -r requirements.txt
```

## Running after install

Then you should be able to `source ./setup.sh` (be careful, if you don't specify the `./` it might not work due to a bad name choice on LXPlus).

To make the ROOT classes, try running make in `CPP/shape_classes` then in `CPP`. This creates the `ROOTex` library.


## Config files (`k3pi_config`)

Basic names are stored in `config.py`, including the eos root path. 

The modes as instances of `mode_base`, in `modes/mode_base.py`. Year, polarity, etc. are stored here, and it can produce a list of files using the files in `filelists/*`. Modes are created in the `modes` directory.

In the main `__init__.py` there is a MODE context manager that picks a file based on mode, and `gcm` which gets the current mode.

## Job options (`job_options`)

The options for the jobs use two python package directories, `helpers` and `modes`. These files use the modes defined previously in `config_files`, and mostly set up the adding or add the required descriptors. The files are run through `ganga_collision` (ganga) or `davinci_collision` (small test run). The completed files are prepared for download through `make_lfn_file`.

## Utilities (`k3pi_root` and `k3pi_utilities`)

A command line program to apply a selection and merge files is in `/k3pi_root/Tree_Splitter.py`.

There are lots of utilities also. `selective_load` is a decorator that loads the current mode.  `Particle` is a class that stores the info about a particle, such as title and daughters. `parser` is a utility for creating a parser. `logger.py` handles logging, `variables.py` defines a `var` class and creates a bunch of variables like `pt` with nice LaTeX representations and units. `tex_compile.py` contains tex compile commands. `helpers.py` reimplements things like progress bars (why not use `Plumbum.cli` or `Click`?). Several are obvious tools just with an added logger call, but there also are a few custom routines. `variables_from_formulae` parses a string for variables, `make_cut_string` builds a `TCut`, and `get_mpv` computes a most probable value using Gaussian kdes. Wrappers for loading and dumbing classifiers and BDTs are in `bdt_utils.py`. `PlotConfig` in `plot_config` is a class to help with plotting. There is also a base folder, `/K3pi_plotting`, that can pdf plotting tools.

## Root C code (`CPP`)

This creates the `ROOTex` library, and uses PyBind11. It contains `Leading`, `SecondLeading`, etc. It has `TreeSplitter`.

## Analysis (`analysis`)

Data can be downloaded from the grid with `download_data.py`.

A parser is implemented for `bdt_studies.py` and `correlations.py`. Data functions for BDT are in `bdt_data.py`. `get_root_preselection.py` will get the selections and uses `ROOTex`.
