#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#


from openstackclient.compute.v2 import server_share
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes


class TestServerShareList(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.share = compute_fakes.create_share()

        self.compute_sdk_client.find_server.return_value = self.server
        self.compute_sdk_client.share_attachments.return_value = self.share

        # Get the command object to test
        self.cmd = server_share.ListServerShare(self.app, None)

    def test_server_share_attachments(self):
        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(("Share ID", "Status", "Tag"), columns)
        self.assertEqual(
            (
                (
                    self.share[0].share_id,
                    self.share[0].status,
                    self.share[0].tag,
                ),
                (
                    self.share[1].share_id,
                    self.share[1].status,
                    self.share[1].tag,
                ),
            ),
            tuple(data),
        )
        self.compute_sdk_client.share_attachments.assert_called_once_with(
            self.server,
        )


class TestServerShareShow(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.share = compute_fakes.create_share()

        self.compute_sdk_client.find_server.return_value = self.server
        self.compute_sdk_client.get_share_attachment.return_value = self.share[
            0
        ]

        # Get the command object to test
        self.cmd = server_share.ShowServerShare(self.app, None)

    def test_server_get_share_attachment(self):
        arglist = [
            self.server.id,
            self.share[0].id,
        ]
        verifylist = [
            ('server', self.server.id),
            ('share_id', self.share[0].id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(
            ('Export Location', 'Share ID', 'Status', 'Tag', 'UUID'), columns
        )
        self.assertEqual(
            (
                self.share[0].export_location,
                self.share[0].share_id,
                self.share[0].status,
                self.share[0].tag,
                self.share[0].uuid,
            ),
            tuple(data),
        )
        self.compute_sdk_client.get_share_attachment.assert_called_once_with(
            self.server, self.share[0].id
        )


class TestServerShareCreate(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.share = compute_fakes.create_share()

        self.compute_sdk_client.find_server.return_value = self.server
        self.compute_sdk_client.create_share_attachment.return_value = (
            self.share[0]
        )

        # Get the command object to test
        self.cmd = server_share.AddServerShare(self.app, None)

    def test_server_create_share_attachment(self):
        arglist = [
            self.server.id,
            self.share[0].id,
            "--tag",
            self.share[0].tag,
        ]
        verifylist = [
            ('server', self.server.id),
            ('share_id', self.share[0].id),
            ('tag', self.share[0].tag),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(
            ("Export Location", "Share ID", "Status", "Tag", "UUID"), columns
        )
        self.assertEqual(
            (
                self.share[0].export_location,
                self.share[0].share_id,
                self.share[0].status,
                self.share[0].tag,
                self.share[0].uuid,
            ),
            tuple(data),
        )
        self.compute_sdk_client.create_share_attachment.assert_called_once_with(
            self.server, self.share[0].id, tag=self.share[0].tag
        )


class TestServerShareDelete(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.share = compute_fakes.create_share()

        self.compute_sdk_client.find_server.return_value = self.server

        # Get the command object to test
        self.cmd = server_share.RemoveServerShare(self.app, None)

    def test_server_share_delete_attachment(self):
        arglist = [
            self.server.id,
            self.share[0].id,
        ]
        verifylist = [
            ('server', self.server.id),
            ('share_id', self.share[0].id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_sdk_client.delete_share_attachment.assert_called_once_with(
            self.server,
            self.share[0].id,
        )
