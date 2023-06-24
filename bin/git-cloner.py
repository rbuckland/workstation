#!/usr/bin/env python3 

"""
Usage: 
    git-cloner [ --workspace <folder> ] <url>

Options:
    --workspace <folder>  The default folder we extract sites to [default: ~/projects]

"""

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

    wf = root_folder(args["--workspace"])
    folder = Path(os.path.join(wf,
           hostname_from_url(args["<url>"]),
           org_from_url(args["<url>"])))

    print(f":: cloning to {folder}")
    folder.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", args["<url>"]], cwd=folder)
