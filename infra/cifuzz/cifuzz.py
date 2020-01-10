# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module used by CI tools in order to interact with fuzzers.
This module helps CI tools do the following:
  1. Build fuzzers.
  2. Run fuzzers.
Eventually it will be used to help CI tools determine which fuzzers to run.
"""

import argparse
import os
import sys
import tempfile

# Adds access to repo_manager and utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import repo_manager
import helper
import utils


def main():
  """Connects Fuzzers with CI tools."""
  parser = argparse.ArgumentParser(
      description='Help CI tools manage specific fuzzers.')

  subparsers = parser.add_subparsers(dest='command')
  build_fuzzer_parser = subparsers.add_parser(
      'build_fuzzers', help='Build an OSS-Fuzz projects fuzzers.')
  build_fuzzer_parser.add_argument('project_name')
  build_fuzzer_parser.add_argument('repo_name')
  build_fuzzer_parser.add_argument('commit_sha')

  run_fuzzer_parser = subparsers.add_parser(
      'run_fuzzers', help='Run an OSS-Fuzz projects fuzzers.')
  run_fuzzer_parser.add_argument('project_name')
  args = parser.parse_args()

  # Change to oss-fuzz main directory so helper.py runs correctly.
  if os.getcwd() != helper.OSSFUZZ_DIR:
    os.chdir(helper.OSSFUZZ_DIR)
  if args.command == 'build_fuzzers':
    if build_fuzzers(args):
      print('Error building projects fuzzers.')
      return 1
    return 0
  elif args.command == 'run_fuzzer':
    if run_fuzzers(args):
      print('Error running projects fuzzers.')
      return 1
    return 0
  print('Invalid argument option, use  build_fuzzers or run_fuzzer.')
  return 1


def build_fuzzers(args):
  """Builds all of the fuzzers for a specific OSS-Fuzz project.

  Returns:
    True on successful build or False on failure
  """
  with tempfile.TemporaryDirectory() as tmp_dir:
    inferred_url, repo_name = utils.detect_main_repo(
        args.project_name, repo_name=args.repo_name)
    if not inferred_url and not repo_name:
      return False
    build_repo_manager = repo_manager.RepoManager(
        inferred_url, tmp_dir, repo_name=repo_name)
    return utils.build_fuzzers_from_commit(args.project_name, args.commit_sha,
                                           build_repo_manager)


def run_fuzzers(args):
  """Runs a all fuzzer for a specific OSS-Fuzz project."""
  # TODO: Implement this function
  return 0


if __name__ == '__main__':
  main()
