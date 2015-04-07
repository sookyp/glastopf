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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# modified by Sooky Peter <xsooky00@stud.fit.vutbr.cz>
# Brno University of Technology, Faculty of Information Technology

from webob import Request, Response


class GlastopfWSGI(object):
    def __init__(self, honeypot):
        self.honeypot = honeypot

    def remove_hop_by_hop_headers(self, headers):
        """
        Removes hop-by-hop headers from a dictionary of headers.
        """
        hop_by_hop_names = ("connection", "keep-alive", "proxy-authenticate",
                            "proxy-authorization", "te", "trailers",
                            "transfer-encoding", "upgrade")

        for header in hop_by_hop_names:
            if header in headers:
                del headers[header]

    def application(self, environ, start_response):
        req_webob = Request(environ)
        res_webob = Response()

        #addr tuple as glastopf expects it
        remote_addr = (req_webob.remote_addr, int(environ["REMOTE_PORT"]))
        if "SERVER_NAME" in environ and "SERVER_PORT" in environ:
            # we could use socket.gethostbyname to get the ip...
            sensor_addr = (environ["SERVER_NAME"], environ["SERVER_PORT"])
        else:
            sensor_addr = ("", "")

        header, body = self.honeypot.handle_request(req_webob.as_text(),
                                                         remote_addr, sensor_addr)

        header_list = header.splitlines()
        try:
            # format: http_version status_code description
            res_webob.status_code = int(header_list[0].split()[1])
        except ValueError:
            # ['User-agent: *', 'Disallow:']
            # default 200 OK
            pass
        for h in header_list:
            if ":" in h:
                h, v = h.split(":", 1)
                res_webob.headers[str(h.strip())] = str(v.strip())
        # this will adjust content-length header
        res_webob.charset = "utf8"
        res_webob.text = body.decode("utf-8", "ignore")

        #WSGI applications are not allowed to create or modify hop-by-hop headers
        self.remove_hop_by_hop_headers(res_webob.headers)
        return res_webob(environ, start_response)
