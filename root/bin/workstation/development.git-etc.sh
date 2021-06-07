#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
set -eux

. ${DIR}/versions

apt install -y git

curl --fail --location --show-error --silent \
    -o /tmp/gh_hub.tgz https://github.com/github/hub/releases/download/v${HUB_VERSION}/hub-linux-amd64-${HUB_VERSION}.tgz \
    && tar xvfz /tmp/gh_hub.tgz -C /usr/local/bin --strip-components=2 hub-linux-amd64-${HUB_VERSION}/bin/hub \
    && rm -f /tmp/gh_hub.tgz

curl --fail --location --show-error --silent \
    -o /tmp/gh_cli.tgz https://github.com/cli/cli/releases/download/v${GH_CLI_VERSION}/gh_${GH_CLI_VERSION}_linux_amd64.tar.gz \
    && tar xvfz /tmp/gh_cli.tgz -C /usr/local/bin --strip-components=2 gh_${GH_CLI_VERSION}_linux_amd64/bin/gh \
    && rm -f /tmp/gh_cli.tgz
