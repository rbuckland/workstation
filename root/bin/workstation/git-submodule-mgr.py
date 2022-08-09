#!/usr/bin/env python3
"""
git Submodule Manager

Usage: git-submodule-mgr.sh status <root-path>

Manager for submodules.

Options:
  -h --help     Show this screen.
  --version     Show version.

Commands:
  status      Report the status on submodules in this repo

Arguments:
  <root-path>       The Full Path to the root of the super-repository.
"""

# This Python is a nicer form of
#     git submodule --quiet foreach --recursive \
#     'printf "$name($displaypath)\t%s\t" $(basename $(git remote -v | awk "/origin.*fetch/ {print \$2;exit}")) \
#      ; git --no-pager describe --all --long --always --dirty --broken \
#     ' | column -t
#

from docopt import docopt
from tabulate import tabulate
import os
import sys
import pygit2
from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_TIME
from colors import *


from pydantic import BaseModel
import itertools


class RepoSummary(BaseModel):
    """Simple dataclass that we return as we walk the repo tree"""
    name: str
    relative_path: str = None
    branch: str = None
    remote_origin: str = None
    status: str = None
    info: str = None
    tags: list = []
    sub_url: str = None


def repo_describe(repo: pygit2.Repository):
    """Generates a very smilar str of - git --no-pager describe --all --long --always --dirty --broken"""
    return repo.describe(
        show_commit_oid_as_fallback=True,
        describe_strategy=pygit2.GIT_DESCRIBE_ALL,
        always_use_long_format=True,
        dirty_suffix="-dirty")


def pretty_branch(repo):
    """For the status table, color the branch"""
    if repo.head.shorthand in ["main", "master", "trunk"]:
        return color(repo.head.shorthand, 'lightblue')

    if repo.head.shorthand.startswith("feature/"):
        return color(repo.head.shorthand, 'lightgreen')

    if repo.head.shorthand.startswith("rel-"):
        return color(repo.head.shorthand, 'yellow')

    return repo.head.shorthand


def status(superrepo_branch, repo, repo_info):
    """Compule a list of "status" tags we want to report about the submodules"""
    status = []

    if repo_info.endswith("-dirty"):
        status.append(color("dirty", "orange"))
        if repo.head.shorthand != superrepo_branch:
            status.append(color("branch-mismatch", "red"))

    return ", ".join(status)


def process_submodule(superrepo_root_path, superrepo_branch, parent_name: str, parent: pygit2.Repository, submodule: pygit2.Submodule):
    """
    Walk submodules, and sub's of submodules
    """
    # print(f"submodule: {parent.workdir} {submodule.head_id}  {submodule.path}")
    module_name = os.path.relpath(
        f"{parent.workdir}/{submodule.path}", start=superrepo_root_path)
    repo: pygit2.Repository

    # if the submodule is unopenable - it's empty (not init'd)
    try:
        repo = submodule.open()
    except Exception as e:
        yield RepoSummary(name=module_name, status=color('<empty>', fg='orange'), sub_url="/".join(submodule.url.split(os.path.sep)[-2:]))
        return

    try:
        repo_info = repo_describe(repo)

        yield RepoSummary(name=f"{module_name}",
                          branch=pretty_branch(repo),
                          status=status(superrepo_branch, repo, repo_info),
                          info=repo_info,
                          # last two paths of https://bit.varmour.com/scm/tra/pa_mgmtsrvr.git , or https://github.com/varmour-eng/foo
                          sub_url="/".join(submodule.url.split(os.path.sep)[-2:])
                          )
        for subm_name in repo.listall_submodules():
            yield from process_submodule(superrepo_root_path, superrepo_branch, parent_name + "/" + submodule.name, repo, repo.lookup_submodule(subm_name))
    except Exception as e:
        print(f"Unexpected error - {module_name} - {e}", file=sys.stderr)
        yield RepoSummary(name=module_name, status=color('<errored>', fg='red'))


def allbase_submodules(superrepo_root_path, super_repo: pygit2.Repository):
    """Start with the super repo, report the status, and then iterate all submodules (recursively)"""
    repo_info = repo_describe(super_repo)
    yield RepoSummary(name=superrepo_root_path,
                      branch=pretty_branch(super_repo),
                      status=status(super_repo.head.shorthand, super_repo, repo_info),
                      info=repo_info,
                      # last two paths of https://bit.varmour.com/scm/tra/pa_mgmtsrvr.git , or https://github.com/varmour-eng/foo
                      sub_url="/".join(super_repo.remotes["origin"].url.split(os.path.sep)[-2:])
                      )
    for subm_name in super_repo.listall_submodules():
        yield from process_submodule(superrepo_root_path, super_repo.head.shorthand, "", super_repo, super_repo.lookup_submodule(subm_name))


def determine_status(superrepo_root_path):
    """Print the table of the root repo"""
    super_repo = pygit2.Repository(arguments["<root-path>"])
    print(tabulate(
        headers=["path", "branch",  "status", "info", "sub_url"],
        tabular_data=[[s.name, s.branch,
                       s.status, s.info, s.sub_url] for s in allbase_submodules(superrepo_root_path, super_repo)],
    ))

if __name__ == '__main__':
    arguments = docopt(__doc__, version="0.1.0")
    if arguments["status"]:
        determine_status(superrepo_root_path=arguments["<root-path>"])
