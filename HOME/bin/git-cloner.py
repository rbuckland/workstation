#!/usr/bin/env python3 

"""
Usage: 
    git-cloner [ -n ] [ --workspace <folder> ] <url>

Options:
    --workspace <folder>  The default folder we extract sites to [default: ~/projects]
    -n                    Dry run - show what you would do

"""

# ~/.gitconfig
# [alias]
#   cloner = !~/bin/git-cloner.py

import sys
import os
import docopt
from os.path import expanduser
from urllib.parse import urlparse
from pathlib import Path
import subprocess


def org_from_url(url) -> str:
     return urlparse(url).path.split("/")[1]

def hostname_from_url(url) -> str:
     return urlparse(url).netloc

def get_site_root_folder():
    os.path.dirname()

def root_folder(workspace_folder): 
    if workspace_folder.startswith("~"):
        return expanduser(workspace_folder)

if __name__ == "__main__":
    args = docopt.docopt(__doc__, version='git-cloner')
    url = args["<url>"]

    wf = root_folder(args["--workspace"])
    folder = Path(os.path.join(wf,
           hostname_from_url(url),
           org_from_url(url)))

    print(f":: cloning to {folder}")
    if args["-n"]:
      print(f":: mkdir -p {folder}")
      print(f":: git clone {url}")
    else:
      folder.mkdir(parents=True, exist_ok=True)
      subprocess.run(["git", "clone", url], cwd=folder)
