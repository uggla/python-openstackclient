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

from unittest import mock

from osc_lib.cli import format_columns
from osc_lib import exceptions
from osc_lib import utils as common_utils

from openstackclient.compute.v2 import server_backup
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.image.v2 import fakes as image_fakes


class TestServerBackup(compute_fakes.TestComputev2):
    def setUp(self):
        super(TestServerBackup, self).setUp()

        # Get a shortcut to the compute client ServerManager Mock
        self.app.client_manager.sdk_connection = mock.Mock()
        self.app.client_manager.sdk_connection.compute = mock.Mock()
        self.sdk_client = self.app.client_manager.sdk_connection.compute

        # Get a shortcut to the image client ImageManager Mock
        self.images_mock = self.app.client_manager.image
        self.images_mock.find_image.reset_mock()

        # Set object attributes to be tested. Could be overwritten in subclass.
        self.attrs = {}

    def setup_servers_mock(self, count):
        servers = compute_fakes.create_sdk_servers(
            attrs=self.attrs,
            count=count,
        )

        # This is the return value for compute_client.find_server()
        self.sdk_client.find_server = compute_fakes.get_servers(
            servers,
            0,
        )
        return servers


class TestServerBackupCreate(TestServerBackup):
    # Just return whatever Image is testing with these days
    def image_columns(self, image):
        # columnlist = tuple(sorted(image.keys()))
        columnlist = (
            'id',
            'name',
            'owner',
            'protected',
            'status',
            'tags',
            'visibility',
        )
        return columnlist

    def image_data(self, image):
        datalist = (
            image['id'],
            image['name'],
            image['owner_id'],
            image['is_protected'],
            'active',
            format_columns.ListColumn(image.get('tags')),
            image['visibility'],
        )
        return datalist

    def setUp(self):
        super(TestServerBackupCreate, self).setUp()

        # Get the command object to test
        self.cmd = server_backup.CreateServerBackup(self.app, None)

    def setup_images_mock(self, count, servers=None):
        if servers:
            images = image_fakes.create_images(
                attrs={
                    'name': servers[0].name,
                    'status': 'active',
                },
                count=count,
            )
        else:
            images = image_fakes.create_images(
                attrs={
                    'status': 'active',
                },
                count=count,
            )

        # self.images_mock.get = mock.Mock(side_effect=images)
        self.images_mock.find_image = mock.Mock(side_effect=images)
        return images

    def test_server_backup_defaults(self):
        servers = self.setup_servers_mock(count=1)
        images = self.setup_images_mock(count=1, servers=servers)

        arglist = [
            servers[0].id,
        ]
        verifylist = [
            ('name', None),
            ('type', None),
            ('rotate', None),
            ('wait', False),
            ('server', servers[0].id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.backup_server.assert_called_with(
            servers[0].id,
            servers[0].name,
            '',
            1,
        )

        self.assertEqual(self.image_columns(images[0]), columns)
        self.assertCountEqual(self.image_data(images[0]), data)

    def test_server_backup_create_options(self):
        servers = self.setup_servers_mock(count=1)
        images = self.setup_images_mock(count=1, servers=servers)

        arglist = [
            '--name',
            'image',
            '--type',
            'daily',
            '--rotate',
            '2',
            servers[0].id,
        ]
        verifylist = [
            ('name', 'image'),
            ('type', 'daily'),
            ('rotate', 2),
            ('server', servers[0].id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.backup_server.assert_called_with(
            servers[0].id,
            'image',
            'daily',
            2,
        )

        self.assertEqual(self.image_columns(images[0]), columns)
        self.assertCountEqual(self.image_data(images[0]), data)

    @mock.patch.object(common_utils, 'wait_for_status', return_value=False)
    def test_server_backup_wait_fail(self, mock_wait_for_status):
        servers = self.setup_servers_mock(count=1)
        images = self.setup_images_mock(count=1, servers=servers)
        self.images_mock.get_image = mock.Mock(
            side_effect=images[0],
        )

        arglist = [
            '--name',
            'image',
            '--type',
            'daily',
            '--wait',
            servers[0].id,
        ]
        verifylist = [
            ('name', 'image'),
            ('type', 'daily'),
            ('wait', True),
            ('server', servers[0].id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )

        self.sdk_client.backup_server.assert_called_with(
            servers[0].id,
            'image',
            'daily',
            1,
        )

        mock_wait_for_status.assert_called_once_with(
            self.images_mock.get_image, images[0].id, callback=mock.ANY
        )

    @mock.patch.object(common_utils, 'wait_for_status', return_value=True)
    def test_server_backup_wait_ok(self, mock_wait_for_status):
        servers = self.setup_servers_mock(count=1)
        images = self.setup_images_mock(count=1, servers=servers)

        self.images_mock.get_image = mock.Mock(
            side_effect=images[0],
        )

        arglist = [
            '--name',
            'image',
            '--type',
            'daily',
            '--wait',
            servers[0].id,
        ]
        verifylist = [
            ('name', 'image'),
            ('type', 'daily'),
            ('wait', True),
            ('server', servers[0].id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.backup_server.assert_called_with(
            servers[0].id,
            'image',
            'daily',
            1,
        )

        mock_wait_for_status.assert_called_once_with(
            self.images_mock.get_image, images[0].id, callback=mock.ANY
        )

        self.assertEqual(self.image_columns(images[0]), columns)
        self.assertCountEqual(self.image_data(images[0]), data)
