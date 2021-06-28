#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
set -eux

. ${DIR}/versions

# https://gauge.org/
curl -SsL https://downloads.gauge.org/stable | sh

curl -SsL -o /usr/local/bin/jq  https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64
chmod +x /usr/local/bin/jq


#
# starship zsh
sh -c "$(curl -fsSL https://starship.rs/install.sh)" -- --yes
