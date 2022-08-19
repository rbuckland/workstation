#!/usr/bin/env python3
"""
git Submodule Manager

Usage:
    git-submodule-mgr.py [ --dir <git-root-path> ] status
    git-submodule-mgr.py [ --dir <git-root-path> ] branch create [ --all ]

Manager for submodules.

Options:
  -h --help        Show this screen.
  --version        Show version.

Commands:
  status           Report the status on submodules in this repo
  branch           Branch Change operations

Branch Actions:
  create           Create a new branch in dirty submodules, to match super_repo
                   where they are not main.
  --all            If supplied, creates a new branch in _all_ currently checked
                   out submodules, regardless.

Arguments:
  --dir <git-root-path>     The Full Path to the root of the super-repository. Auto detected otherwise
"""

# This Python is a nicer form of
#     git submodule --quiet foreach --recursive \
#     'printf "$name($displaypath)\t%s\t" $(basename $(git remote -v | awk "/origin.*fetch/ {print \$2;exit}")) \
#      ; git --no-pager describe --all --long --always --dirty --broken \
#     ' | column -t


from xmlrpc.client import Boolean
from docopt import docopt
from tabulate import tabulate
import os
import traceback
import sys
import pygit2
from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_TIME
from pygit2 import GIT_STATUS_WT_NEW, GIT_STATUS_WT_DELETED, GIT_STATUS_WT_MODIFIED, GIT_STATUS_WT_RENAMED, GIT_STATUS_WT_TYPECHANGE ,GIT_STATUS_WT_UNREADABLE, GIT_STATUS_CONFLICTED, GIT_STATUS_CURRENT, GIT_STATUS_IGNORED, GIT_STATUS_INDEX_DELETED, GIT_STATUS_INDEX_MODIFIED, GIT_STATUS_INDEX_NEW, GIT_STATUS_INDEX_RENAMED, GIT_STATUS_INDEX_TYPECHANGE
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
    file_status: str = None

def locate_super_root_dir():
    try:
        # yes literally just run the shell version. meh easier.
        return os.popen("dirname $(cd $(git rev-parse --git-dir) && pwd )").read().strip()
    except Exception as e:
        print(f":: not in a git repo - {e}")


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
    """Compute a list of "status" tags we want to report about the submodules"""
    status = []

    if repo_info.endswith("-dirty"):
        status.append(color("dirty", "orange"))
        if repo.head.shorthand != superrepo_branch:
            status.append(color("branch-mismatch", "red"))

    return ", ".join(status)

FILESTATUS_MAP = {
  GIT_STATUS_WT_NEW: "+",
  GIT_STATUS_WT_DELETED :"-",
  GIT_STATUS_WT_MODIFIED:"~",
  GIT_STATUS_WT_RENAMED:"%",
  GIT_STATUS_WT_TYPECHANGE:"√",
  GIT_STATUS_WT_UNREADABLE:"*",
  GIT_STATUS_CONFLICTED:"✘",
  GIT_STATUS_CURRENT:"#",
  GIT_STATUS_IGNORED:"i",
  GIT_STATUS_INDEX_DELETED:"∫",
  GIT_STATUS_INDEX_MODIFIED:"@",
  GIT_STATUS_INDEX_NEW:":",
  GIT_STATUS_INDEX_RENAMED:"=",
  GIT_STATUS_INDEX_TYPECHANGE:"†"

}
def file_status(repo):
  """determine the status of files"""
  file_stats = dict.fromkeys(FILESTATUS_MAP.values(),0)
  for k, v in repo.status().items():
    file_stats[FILESTATUS_MAP[v]] += 1
  return " ".join((f"{k}{v}" for k, v in file_stats.items() if v > 0))

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
                          sub_url="/".join(submodule.url.split(os.path.sep)[-2:]),
                          file_status=file_status(repo)
                          )
        for subm_name in repo.listall_submodules():
            yield from process_submodule(superrepo_root_path, superrepo_branch, parent_name + "/" + submodule.name, repo, repo.lookup_submodule(subm_name))
    except Exception as e:
        print(f"Unexpected error - {module_name} - {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        yield RepoSummary(name=module_name, status=color('<errored>', fg='red'))


def allbase_submodules(superrepo_root_path, super_repo: pygit2.Repository):
    """Start with the super repo, report the status, and then iterate all submodules (recursively)"""
    repo_info = repo_describe(super_repo)
    yield RepoSummary(name="<superrepo> " + superrepo_root_path.split("/")[-1],
                      branch=pretty_branch(super_repo),
                      status=status(super_repo.head.shorthand, super_repo, repo_info),
                      info=repo_info,
                      # last two paths of https://bit.varmour.com/scm/tra/pa_mgmtsrvr.git , or https://github.com/varmour-eng/foo
                      sub_url="/".join(super_repo.remotes["origin"].url.split(os.path.sep)[-2:]),
                      file_status=file_status(super_repo)
                      )
    for subm_name in super_repo.listall_submodules():
        yield from process_submodule(superrepo_root_path, super_repo.head.shorthand, "", super_repo, super_repo.lookup_submodule(subm_name))


def determine_status(superrepo_root_path):
    """Print the table of the root repo"""
    super_repo = pygit2.Repository(superrepo_root_path)
    print(tabulate(
        headers=["path", "branch",  "status", "info", "file_status", "sub_url"],
        tabular_data=[[s.name,
                       s.branch,
                       s.status,
                       s.info,
                       s.file_status,
                       s.sub_url] for s in allbase_submodules(superrepo_root_path, super_repo)],
    ))

def create_or_switch_branch(repo: pygit2.Repository, branch_name):
    """
    Tries to switch to a branch, and if it can't it tries to
    create a local branch then switch.
    """
    try:
      branch = repo.lookup_branch(branch_name)
      if branch is None:
          branch = repo.branches.local.create(branch_name, repo[repo.head.target])
      ref = repo.lookup_reference(branch.name)
      repo.checkout(ref)
    except Exception as e:
       print(f"!! Creating / switching to a branch failed {repo.path} - {e}")



def recursive_create_branches(repo: pygit2.Repository, branch_name: str, create_in_all: bool):
   """
   Create branches across the submodules
   """
   print(f":: processing {repo.path}")

   if repo.head.shorthand != branch_name:
      repo_info = repo_describe(repo)

      if create_in_all:
          print(f">> repo.create_branch({branch_name})")
          create_or_switch_branch(repo, branch_name)
      elif repo_info.endswith("-dirty"):
          print(f">> dirty - repo.create_branch({branch_name})")
          create_or_switch_branch(repo, branch_name)
      else:
          print(f":: skipping - {repo.workdir} (not dirty, not all)")

   for subm_name in repo.listall_submodules():
       sub_repo: pygit2.Repository = None
       try:
         submodule = repo.lookup_submodule(subm_name)
         sub_repo = submodule.open()
         recursive_create_branches(repo = sub_repo, branch_name = branch_name, create_in_all = create_in_all)
       except Exception as e:
          print(f"  :: skipping {subm_name} - {e} not initialised")

def create_new_branches(superrepo_root_path: str, create_in_all: bool):
    """Create branches matching superrepo, if submodule exists"""
    super_repo = pygit2.Repository(superrepo_root_path)
    if super_repo.head.shorthand not in ["main", "master"]:

      for subm_name in super_repo.listall_submodules():
        try:
          submodule = super_repo.lookup_submodule(subm_name)
          sub_repo = submodule.open()
          recursive_create_branches(repo = sub_repo, branch_name = super_repo.head.shorthand, create_in_all = create_in_all)
        except Exception as e:
          print(f"!! error {subm_name} - {e}")

    else:
      print(f":: doing no work - super_repo branch is [{super_repo.head.shorthand}]")

if __name__ == '__main__':
    arguments = docopt(__doc__, version="0.1.0")

    if arguments["--dir"] is None:
        repo_dir = locate_super_root_dir()
    else:
        repo_dir = arguments["--dir"]

    if arguments["status"]:
        determine_status(superrepo_root_path=repo_dir)
        sys.exit(0)

    if arguments["branch"] and arguments["create"]:
        create_new_branches(superrepo_root_path=repo_dir,
                            create_in_all=arguments["--all"])
