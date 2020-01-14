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
"""A module to handle running fuzz targets for a specified amount of time."""
import datetime
import enum
import logging
import multiprocessing
import os
import time

import helper

class FuzzTarget():
  """A class to manage a single fuzz target.

  Attributes:
    project_name: The name of the OSS-Fuzz project this target is associated with.
    target_name: The name of the fuzz target.
    output_message: The message the target sends as its status.
    message_lock: A lock for the message object.
    duration: The length of time in seconds that the target should run.
    process: The process running the target.
  """

  def __init__(self, project_name, target_path, duration):
    """Represents a single fuzz target.

    Args:
      project_name: The OSS-Fuzz project of this target.
      target_path: The location of the fuzz target binary.
      duration: The length of time  in seconds the target should run.
    """
    self.target_name = target_path.split('/')[-1]
    self.duration = duration
    self.project_name = project_name
    self.message_lock = multiprocessing.Lock()
    self._set_message(None)

  def start(self):
    """Starts the fuzz target run for the length of time specifed by duration.

    Returns:
      None if target ran out of time or Error message if target found an error.
    """
    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(seconds=self.duration)
    self.process = multiprocessing.Process(target=self._run_fuzzer)
    self.process.start()
    while datetime.datetime.now() < end_time:
      if not self.process.is_alive():
        break
      time.sleep(.1)
    if self.process.is_alive():
      self.process.terminate()
      self.process.join()
    return self.get_message()

  def _run_fuzzer(self):
    """Runs the fuzz target.

    Note: Intended to be run in a separate process.
    """
    logging.debug('Fuzzer {0} started on process {1}.'.format(self.target_name, os.getpid()))
    return_code = helper.run_fuzzer_impl(self.project_name, self.target_name, 'libfuzzer', 'address', None, [])
    self._set_message('Error occurred before fuzzer run finished.')
    logging.debug('Fuzzer {} stopped before time up.'.format(self.target_name))

  def _set_message(self, message_to_set):
    """Synchronously sets the message attribute.

    Args:
       message_to_set: The string to set the message to.
    """
    logging.debug('Setting {} message to {}.'.format(self.target_name, message_to_set))
    self.message_lock.acquire()
    self.message = message_to_set
    self.message_lock.release()

  def get_message(self):
    """Synchronously gets the message of the fuzz target."""
    self.message_lock.acquire()
    message = self.message
    self.message_lock.release()
    return message
