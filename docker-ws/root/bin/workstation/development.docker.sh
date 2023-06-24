#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
set -eux

. ${DIR}/versions

# a nice way to locate OS variable parameters - not needed now
# eval $( cat /etc/os-release | sed 's/^/OS_RELEASE_/g' ) 

apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

curl --fail --location --show-error --silent https://download.docker.com/linux/ubuntu/gpg \
| gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg    

echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update



# + apt-cache madison docker-ce
#  docker-ce | 5:20.10.6~3-0~ubuntu-bionic | https://download.docker.com/linux/ubuntu bionic/stable amd64 Packages
#  docker-ce | 5:20.10.5~3-0~ubuntu-bionic | https://download.docker.com/linux/ubuntu bionic/stable amd64 Packages
#  ...
#  docker-ce | 5:19.03.15~3-0~ubuntu-bionic | https://download.docker.com/linux/ubuntu bionic/stable amd64 Packages

DCE_VER=$(apt-cache madison docker-ce | grep ${DOCKER_CE_VERSION} | head -1 | awk '{ print $3 }')
apt-get install -y \
    docker-ce=${DCE_VER} \
    docker-ce-cli=${DCE_VER} \
    containerd.io

# docker-compose
#

curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose