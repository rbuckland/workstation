#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

set -eux

. ${DIR}/versions

#
# nvm - node version manager
# export XDG_CONFIG_HOME=/usr/local/nvm
export NVM_DIR=/usr/local/nvm
export PROFILE=/dev/null
mkdir -p ${NVM_DIR}
curl -o- https://raw.githubusercontent.com/creationix/nvm/v${NVM_VERSION}/install.sh | bash 

. $NVM_DIR/nvm.sh
nvm install "$NODE_VERSION"
nvm alias default "$NODE_VERSION"
nvm use default 

DEFAULT_NODE_VERSION=$(nvm version default)

#
# setup default profile
#
ln -s $NVM_DIR/nvm.sh /etc/profile.d/nvm.sh
echo "export NODE_PATH=$NVM_DIR/versions/node/$DEFAULT_NODE_VERSION/lib/node_modules" > /etc/profile.d/nvm_env.sh
echo "export PATH=$NVM_DIR/versions/node/$DEFAULT_NODE_VERSION/bin:\$PATH" >> /etc/profile.d/nvm_env.sh

npm install -g $( cat /bin/workstation/packages.node.txt | egrep -v "(^#|^\s*$)" )