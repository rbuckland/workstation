#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
set -eux

. ${DIR}/versions

# https://gauge.org/
curl -SsL https://downloads.gauge.org/stable | sh


#
# starship zsh
sh -c "$(curl -fsSL https://starship.rs/install.sh)" -- --yes
