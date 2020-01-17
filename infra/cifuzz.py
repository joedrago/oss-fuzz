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
import logging
import os
import shutil
import sys
import tempfile

import build_specified_commit
import fuzz_target
import helper
import repo_manager
import datetime
import utils


def main():
  """Connects Fuzzers with CI tools.

  Returns:
    True on success False on failure.
  """
  logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', stream=sys.stdout, level=logging.DEBUG)
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
    return build_fuzzers(args) == 0
  if args.command == 'run_fuzzers':
    return run_fuzzers(args) == 0
  print('Invalid argument option, use build_fuzzers or run_fuzzer.', file=sys.stderr)
  return False


def build_fuzzers(args):
  """Builds all of the fuzzers for a specific OSS-Fuzz project.

  Returns:
    True on success False on failure.
  """

  # TODO: Fix return value bubble to actually handle errors.
  with tempfile.TemporaryDirectory() as tmp_dir:

    inferred_url, repo_name = build_specified_commit.detect_main_repo(
        args.project_name, repo_name=args.repo_name)
    logging.debug('Building fuzzers for project: {}.'.format(args.project_name))
    build_repo_manager = repo_manager.RepoManager(inferred_url,
                                                  os.environ['GITHUB_WORKSPACE'],
                                                  repo_name=repo_name)
    return build_specified_commit.build_fuzzers_from_commit(
        args.project_name, args.commit_sha, build_repo_manager) == 0


def run_fuzzers(args):
  """Runs a all fuzzer for a specific OSS-Fuzz project.

  Returns:
    True on success False on failure.
  """
  print('Starting to run fuzzers.')
  fuzzer_paths = utils.get_project_fuzz_targets(args.project_name)
  print('Fuzzer paths', str(fuzzer_paths))
  fuzz_targets = []
  for fuzzer in fuzzer_paths:
    fuzz_targets.append(fuzz_target.FuzzTarget(args.project_name, fuzzer, 20))
  print(fuzzer_paths)
  error_detected = False

  for target in fuzz_targets:
    print('Fuzzer {} started running.'.format(target.target_name))
    test_case, stack_trace = target.start()
    if not test_case or not stack_trace:
      logging.debug('Fuzzer {} finished running.'.format(target.target_name))
      print('Fuzzer {} finished running.'.format(target.target_name))
    else:
      error_detected = True
      print("Fuzzer {} Detected Error: {}".format(target.target_name, stack_trace), file=sys.stderr)
      shutil.move(test_case, '/tmp/testcase')
      break
  return not error_detected


if __name__ == '__main__':
  main()
