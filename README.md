# D0ToK3pi

Preparing to use on LXPlus:

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

After reruning your bashrc, you'll need to make a k3pi environment:

```
mkvirtualenv k3pi
pip install numpy scipy matplotlib
pip install -r requirements.txt
```

Then you should be able to `source ./setup.sh` (be careful, if you don't specify the `./` it might not work due to a bad name choice on LXPlus).

To start using it, try running make in `CPP/shape_classes` then in `CPP`.
