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
"""Builds and runs specific OSS-Fuzz project's fuzzers for CI tools."""
import os
import sys

# pylint: disable=wrong-import-position
sys.path.append('/src/oss-fuzz/infra/cifuzz/')
import cifuzz


def main():
  """Runs OSS-Fuzz project's fuzzers for CI tools.
  This script is used to kick off the Github Actions CI tool. It is the
  entrypoint  of the Dockerfile in this directory. This action can be added to
  any OSS-Fuzz project's workflow that uses Github.

  Required environment variables:
    PROJECT_NAME: The name of OSS-Fuzz project.
    FUZZ_TIME: The length of time in seconds that fuzzers are to be run.
    GITHUB_REPOSITORY: The name of the Github repo that called this script.
    GITHUB_SHA: The commit SHA that triggered this script.

  Returns:
    0 on success or 1 on Failure.
  """
  oss_fuzz_project_name = os.environ['PROJECT_NAME']
  fuzz_seconds = int(os.environ['FUZZ_SECONDS'])
  github_repo_name = os.environ['GITHUB_REPOSITORY'].split('/')[-1]
  commit_sha = os.environ['GITHUB_SHA']
  print('Github repo name: ' + github_repo_name)

  # Get the shared volume directory and creates required directory.
  if 'GITHUB_WORKSPACE' not in os.environ:
    return 1
  git_workspace = os.path.join(os.environ['GITHUB_WORKSPACE'], 'storage')
  if not os.path.exists(git_workspace):
    os.mkdir(git_workspace)
  out_dir = os.path.join(os.environ['GITHUB_WORKSPACE'], 'out')
  if not os.path.exists(out_dir):
    os.mkdir(out_dir)

  # Build the specified project's fuzzers from the current repo state.
  cifuzz.build_fuzzers(oss_fuzz_project_name, github_repo_name, commit_sha,
                       git_workspace, out_dir)

  # Run the specified project's fuzzers from the build.
  cifuzz.run_fuzzers(oss_fuzz_project_name, fuzz_seconds, out_dir)
  return 0


if __name__ == '__main__':
  sys.exit(main())
