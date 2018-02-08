# Copyright 2017 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import io
import os
import time
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
# django
from django.conf import settings
from django.utils import timezone
# dashboard
from dashboard.engine.action_mapper import ActionMapper
from dashboard.engine.ds import TaskList
from dashboard.engine.parser import YMLPreProcessor, YMLJobParser
from dashboard.managers.base import BaseManager
from dashboard.managers.inventory import PackagesManager

__all__ = ['DownstreamManager']


class DownstreamManager(BaseManager):
    """
    Packages Downstream Manager
    """

    sandbox_path = 'dashboard/sandbox/'
    job_log_file = sandbox_path + 'downstream.log'

    def _bootstrap(self, build_system):
        self.package_manager = PackagesManager()
        release_streams = \
            self.package_manager.get_release_streams(built=build_system)
        release_stream = release_streams.get()
        if release_stream:
            self.hub_url = release_stream.relstream_server
        # remove log file if exists
        if os.path.exists(self.job_log_file):
            os.remove(self.job_log_file)

    def _save_result_in_db(self, stats_dict):
        pkg_new_fields = {
            'downstream_latest_stats': stats_dict,
            'downstream_lastupdated': timezone.now()
        }
        try:
            self.package_manager.update_package(self.package, pkg_new_fields)
        except Exception as e:
            self.app_logger(
                'ERROR', "Package could not be updated, details: " + str(e)
            )

    def execute_job(self):
        """
        1. PreProcess YML and replace variables with input_values
            - Example: %PACKAGE_NAME%
        2. Parse processed YML and build Job object
        3. Select data structure for tasks and instantiate one
            - Example: Linked list should be used for sequential tasks
        3. Discover namespace and method for each task and fill in TaskNode
        4. Perform actions (execute tasks) and return responses
        """

        yml_preprocessed = YMLPreProcessor(self.YML_FILE, **{
            'PACKAGE_NAME': self.PACKAGE_NAME, 'BUILD_TAG': self.BUILD_TAG
        }).output

        if yml_preprocessed:
            self.job_base_dir = os.path.dirname(settings.BASE_DIR)
            yml_job = YMLJobParser(yml_stream=io.StringIO(yml_preprocessed))
            self.package = yml_job.package
            self.tag = yml_job.tags[0] if len(yml_job.tags) > 0 else None
            self._bootstrap(yml_job.buildsys)
            # for sequential jobs, tasks should be pushed to linked list
            # and output of previous task should be input for next task
            if yml_job.execution == 'sequential':
                self.tasks_ds = TaskList()
            if self.tag and self.package and self.hub_url and self.job_base_dir:
                tasks = yml_job.tasks
                for task in tasks:
                    self.tasks_ds.add_task(task)

                action_mapper = ActionMapper(
                    self.tasks_ds, self.tag, self.package,
                    self.hub_url, self.job_base_dir
                )
                action_mapper.set_actions()
                action_mapper.execute_tasks()
                time.sleep(3)
                action_mapper.clean_workspace()

                if action_mapper.result and not getattr(self, 'DRY_RUN', None):
                    self._save_result_in_db(action_mapper.result)
