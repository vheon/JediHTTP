#     Copyright 2017 Cedraro Andrea <a.cedraro@gmail.com>
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
#    limitations under the License.

import time
import copy
import logging
from threading import Thread, Lock
from jedihttp.handlers import server_shutdown


class WatchdogPlugin(object):
    """
    Bottle plugin (http://bottlepy.org/docs/dev/plugindev.html) for
    automatically shutting down the server if no request is made within
    |idle_suicide_seconds| seconds. Checks are done every
    |check_interval_seconds| seconds.
    """
    name = 'watchdog'
    api = 2

    def __init__(self, idle_suicide_seconds, check_interval_seconds):
        self._logger = logging.getLogger(__name__)
        self._check_interval_seconds = check_interval_seconds
        self._idle_suicide_seconds = idle_suicide_seconds

        # No need for a lock on wakeup time since only the watchdog thread ever
        # reads or sets it.
        self._last_wakeup_time = time.time()
        self._last_request_time = time.time()
        self._last_request_time_lock = Lock()
        if idle_suicide_seconds <= 0:
            return
        self._watchdog_thread = Thread(target=self._watchdog_main)
        self._watchdog_thread.daemon = True
        self._watchdog_thread.start()

    def _get_last_request_time(self):
        with self._last_request_time_lock:
            return copy.deepcopy(self._last_request_time)

    def _set_last_request_time(self, last_request_time):
        with self._last_request_time_lock:
            self._last_request_time = last_request_time

    def _time_since_last_request(self):
        return time.time() - self._get_last_request_time()

    def _time_since_last_wakeup(self):
        return time.time() - self._last_wakeup_time

    def _update_last_wakeup_time(self):
        self._last_wakeup_time = time.time()

    def _watchdog_main(self):
        while True:
            time.sleep(self._check_interval_seconds)

            # We make sure we don't terminate if we skipped a wakeup time. If
            # we skipped a check, that means the machine probably went to sleep
            # and the client might still actually be up. In such cases, we give
            # it one more wait interval to contact us before we die.
            if (self._time_since_last_request() >
                    self._idle_suicide_seconds and
                    self._time_since_last_wakeup() <
                    2 * self._check_interval_seconds):
                self._logger.info('Shutting down server due to inactivity.')
                server_shutdown()

            self._update_last_wakeup_time()

    def __call__(self, callback):
        def wrapper(*args, **kwargs):
            self._set_last_request_time(time.time())
            return callback(*args, **kwargs)
        return wrapper
