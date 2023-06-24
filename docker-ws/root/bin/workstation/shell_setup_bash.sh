#!/bin/bash 

#
# Custom setup for bash
#

if [ ! -f /home/${USERNAME}/.bashrc ] && [ -f /etc/dotfiles/.bashrc ]; then
    ln -s /etc/dotfiles/.bashrc /home/${USERNAME}/.bashrc 
fi
