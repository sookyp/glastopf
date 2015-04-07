# Copyright (C) 2015 Johnny Vestergaard <jkv@unixcluster.dk>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# modified by Sooky Peter <xsooky00@stud.fit.vutbr.cz>
# Brno University of Technology, Faculty of Information Technology

import logging
import os

from glastopf.modules.reporting.auxiliary.base_logger import BaseLogger


class LogSyslog(BaseLogger):
    def __init__(self, data_dir, work_dir, config="glastopf.cfg"):
        config = os.path.join(work_dir, config)
        BaseLogger.__init__(self, config)
        self.options = {
            "enabled": self.config.getboolean("syslog", "enabled"),
            "socket": self.config.get("syslog", "socket"),
        }

        if self.options['enabled']:
        #Make sure we only have one logger
            try:
                LogSyslog.logger
            except AttributeError:
                LogSyslog.logger = logging.getLogger('glaspot_attack')
                LogSyslog.logger.propagate = False
                if ":" in self.options['socket']:
                    host, port = self.options['socket'].split(":")
                    address = (host, int(port))
                else:
                    address = (self.options['socket'], 514)
                logging.info('Using syslog logger on remote {0}.'.format(address))
                LogSyslog.log_handler = logging.handlers.SysLogHandler(address=address)
                LogSyslog.logger.addHandler(self.log_handler)
                LogSyslog.logger.setLevel(logging.INFO)

    def insert(self, attack_event):
        message = "Glaspot: %(pattern)s attack method from %(source_ip)s:%(source_port)s against %(host)s:%(port)s. [%(method)s %(url)s]" % {
            'pattern': attack_event.matched_pattern,
            'source_ip': attack_event.source_ip,
            'source_port': attack_event.source_port,
            'host': attack_event.sensor_addr[0],
            'port': attack_event.sensor_addr[1],
            'method': attack_event.http_request.request_verb,
            'url': attack_event.http_request.request_url,
        }
        LogSyslog.logger.info(message)
