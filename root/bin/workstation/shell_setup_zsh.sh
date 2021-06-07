#!/bin/bash 

#
# Custom setup for zsh
#

if [ ! -f /home/${USERNAME}/.zshrc ]; then
    ls -s /etc/dotfiles/.zshrc /home/${USERNAME}/.zshrc 
fi

# if [ ! -f /home/${USERNAME}/.oh-my-zsh ]; then
#    ls -s /etc/dotfiles/.oh-my-zsh /home/${USERNAME}/.oh-my-zsh
# fi

export ZSH_CUSTOM=/home/${USERNAME}/.oh-my-zsh/custom
