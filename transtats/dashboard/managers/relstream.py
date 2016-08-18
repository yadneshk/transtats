# Copyright 2016 Red Hat, Inc.
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

from ..models.relstream import ReleaseStream
from .base import BaseManager


class ReleaseStreamManager(BaseManager):
    """
    Release Stream Manager
    """
    def get_active_relstreams(self):
        """
        Fetch slug and name for all active release streams
        :return: tuple
        """
        streams = None
        try:
            streams = self.db_session.query(ReleaseStream.relstream_slug, ReleaseStream.relstream_name) \
                .filter_by(relstream_status='active').all()
        except:
            # log event, passing for now
            pass
        return tuple(streams) if streams else ()
