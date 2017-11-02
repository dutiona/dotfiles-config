#!/bin/zsh

#set -x

dotdir="$(cd $(dirname $0); pwd)"
cd "$dotdir"

hostname=$(hostname)

function create_link() {
    dotfile="$1"
    dotlink="$HOME/.$1"

    # Link to hostname specific version of the dotfile
    [[ -f "${dotfile}.${hostname}" ]] && dotfile="${dotfile}.${hostname}"

    # Link already exist
    [[ -h "$dotlink" ]] && [[ $(readlink "$dotlink") == "$dotdir/$dotfile" ]] && return;

    # Ask to replace an existing file
    [[ -e "$dotlink" ]] && {
        echo "Replace '$dotlink' [yN]? "
        read -q && rm -rf "$dotlink"
    }

    # Create the link
    ln -sf "$dotdir/$dotfile" "$dotlink"
}

# sometime ~/.config does not exist
mkdir -p ~/.config

# Create symlinks
create_link Xresources
create_link gitconfig
create_link gvimrc
create_link less
create_link lesskey
create_link pentadactylrc
create_link vimperatorrc
create_link tmux.conf
create_link vim
create_link vimrc
create_link xsession
create_link zsh
create_link zshenv
create_link zshrc
create_link zprofile
create_link zlogin
create_link zprezto
create_link zpreztorc
create_link config/nvim

# Fetch git submodule
git submodule update --init --recursive

# Install vim plugin manager
curl -fLo ~/.dotfiles/vim/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim

# Fetch vim plugins
# With vim >= 7.3, we could add the option '-E -s' to be headless
if vim -E -s -X -u ~/.vim/empty.vim -c ':qa' &> /dev/null ; then
    vim -E -s -X -u ~/.vim/bundles.vim -c ':PlugInstall' -c ':PlugClean!' -c ':qa'
else
    vim -X -u ~/.vim/bundles.vim -c ':PlugInstall' -c ':PlugClean!' -c ':qa'
fi

rm -rf ~/.vim/bundle
true
