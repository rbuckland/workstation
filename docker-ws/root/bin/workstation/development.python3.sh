#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

set -eux

apt install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt install -y python3.9 python3-distutils python3-dev

update-alternatives --install /usr/bin/python python /usr/bin/python3 1
update-alternatives --config python

curl -o /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py && \
python /tmp/get-pip.py && \
rm /tmp/get-pip.py

python -m pip install --upgrade --force pip
python -m pip install --upgrade setuptools virtualenv wheel 
python -m pip install -r ${DIR}/packages.python.txt
