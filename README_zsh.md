# Installing zsh on LXPlus

Download the source or use git (check out a tag, though), and then run:

```
Util/preconfig
./configure --prefix=$HOME/.local
make
make install.bin
make install.fns
make install.modules
```

(install.docs and runhelp does not work for me)

Then you can add the following to your bashrc to default to zsh:

```
# -f tests if file exists, therefore only start zsh if executable is there.
if [ -f "$HOME/.local/bin/zsh" ]; then
    export SHELL=$HOME/.local/bin/zsh
    $HOME/.local/bin/zsh
    # Exit from bash immediately when I quit zsh.
    if [ $? -eq 0 ]; then
        exit
    fi
fi
```

