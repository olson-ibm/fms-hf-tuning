# Copyright The FMS HF Tuning Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Third Party
from aim.hugging_face import AimCallback  # pylint: disable=import-error
from transformers.utils import logging

# Local
from .tracker import Tracker
from tuning.config.tracker_configs import AimConfig


class AimStackTracker(Tracker):
    def __init__(self, tracker_config: AimConfig):
        super().__init__(name="aim", tracker_config=tracker_config)
        self.logger = logging.get_logger("aimstack_tracker")

    def get_hf_callback(self):
        c = self.config
        exp = c.experiment
        url = c.aim_url
        repo = c.aim_repo

        if url is not None:
            aim_callback = AimCallback(repo=url, experiment=exp)
        if repo:
            aim_callback = AimCallback(repo=repo, experiment=exp)
        else:
            self.logger.warning(
                "Aim tracker requested but repo or server is not specified. "
                + "Please specify either aim repo or aim server ip and port for using Aim."
            )
            aim_callback = None

        self.hf_callback = aim_callback
        return self.hf_callback

    def track(self, metric, name, stage="additional_metrics"):
        if metric is None or name is None:
            self.logger.warning("Tracked metric value or name should not be None")
            return
        context = {"subset": stage}
        callback = self.hf_callback
        run = callback.experiment
        if run is not None:
            run.track(metric, name=name, context=context)

    def set_params(self, params, name="extra_params"):
        if params is None:
            return
        callback = self.hf_callback
        run = callback.experiment
        if run is not None:
            for key, value in params.items():
                run.set((name, key), value, strict=False)
