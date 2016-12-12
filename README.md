# D0ToK3pi

Preparing to use on LXPlus:

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

After reruning your bashrc, you'll need to make a k3pi environment:

```
mkvirtualenv k3pi -r requirements.txt
```

Then you should be able to source setup.sh (I have to copy and paste it to the command line for some unknown reason).
