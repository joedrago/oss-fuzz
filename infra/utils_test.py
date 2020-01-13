# Copyright 2019 Google LLC
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
"""Testing Utilities for OSS-Fuzz infrastructure."""

import os
import unittest

import helper
import utils

class TestDetectFuzzers(unittest.TestCase):
  """Class to test that a project's fuzzers can be determined."""

  def test_fake_proj(self):
    """Class to test when a project does not exist."""
    self.assertFalse(utils.get_project_fuzz_targets('notaproj'))

  def test_example_fuzzers(self):
    """Class to test that examples's fuzzers can be determined."""
    helper.build_fuzzers_impl(project_name='example', clean=True,engine='libfuzzer', sanitizer='address', architecture='x86_64', env_to_add=None, source_path=None)
    example_fuzzers = ['do_stuff_fuzzer']
    detected_fuzzers = utils.get_project_fuzz_targets('example')
    detected_fuzzers = map(lambda x: x.split('/')[-1], detected_fuzzers)
    self.assertTrue(detected_fuzzers)
    self.assertCountEqual(example_fuzzers, detected_fuzzers)


class TestIsFuzzTarget(unittest.TestCase):
  """Tests that fuzz targets can be detected automatically. """

  @classmethod
  def setUpClass(self):
    """ Build fuzzers is slow, this avoids calling it for every test case."""
    super(TestIsFuzzTarget, self).setUpClass()
    helper.build_fuzzers_impl(project_name='example', clean=True,engine='libfuzzer', sanitizer='address', architecture='x86_64', env_to_add=None, source_path=None)

  def test_is_not_fuzzer(self):
    not_fuzzer_path = os.path.join(helper.BUILD_DIR, 'out', 'example', 'do_stuff_fuzzer_seed_corpus.zip')
    self.assertFalse(utils.is_fuzz_target_local(not_fuzzer_path))

  def test_is_fuzzer(self):
    fuzzer_path = os.path.join(helper.BUILD_DIR, 'out', 'example', 'do_stuff_fuzzer')
    self.assertTrue(utils.is_fuzz_target_local(fuzzer_path))

  def test_fuzzer_not_file(self):
    not_file_path = os.path.join(helper.BUILD_DIR, 'example', 'not_a_file')
    self.assertFalse(utils.is_fuzz_target_local(not_file_path))

if __name__ == '__main__':
  unittest.main()
