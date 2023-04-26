# Copyright 2020, Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Compute v2 Server action implementations"""

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _


def _get_server_share_columns(client, item):
    # Non admin cannot see uuid and export location, so hide them
    if item.uuid is None:
        column_map = {
            'share_id': 'Share ID',
            'status': 'Status',
            'tag': 'Tag',
        }
        hidden_columns = ['id', 'location', 'name', 'uuid', 'export_location']
    else:
        column_map = {
            'uuid': 'UUID',
            'share_id': 'Share ID',
            'status': 'Status',
            'tag': 'Tag',
            'export_location': 'Export Location',
        }
        hidden_columns = ['id', 'location', 'name']

    return utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


class ListServerShare(command.Lister):
    """List all the shares attached to a server.

    Note: This api is available since nova microversion 2.97.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server to list share mapping for (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.sdk_connection.compute

        server = compute_client.find_server(
            parsed_args.server,
            ignore_missing=False,
        )
        shares = compute_client.share_attachments(server)

        columns = (
            'share_id',
            'status',
            'tag',
        )
        column_headers = (
            'Share ID',
            'Status',
            'Tag',
        )

        return (
            column_headers,
            (utils.get_item_properties(s, columns) for s in shares),
        )


class ShowServerShare(command.ShowOne):
    """Show detail of a share attachment to a server.

    Note: This api is available since nova microversion 2.97.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server to list share mapping for (name or ID)'),
        )
        parser.add_argument(
            'share_id',
            metavar='<share-id>',
            help=_('Share to show details for (ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.sdk_connection.compute

        server = compute_client.find_server(
            parsed_args.server,
            ignore_missing=False,
        )
        share = compute_client.get_share_attachment(
            server, parsed_args.share_id
        )

        display_columns, columns = _get_server_share_columns(
            compute_client,
            share,
        )
        data = utils.get_item_properties(share, columns)
        return display_columns, data


class AddServerShare(command.ShowOne):
    """Create a share attachment to a server.

    Note: This api is available since nova microversion 2.97.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server to create share mapping for (name or ID)'),
        )
        parser.add_argument(
            'share_id',
            metavar='<share-id>',
            help=_('Share to associate (ID)'),
        )
        parser.add_argument(
            '--tag',
            metavar='<tag>',
            help=_(
                'Optional tag used to mount the share, '
                'if not provided the share uuid is used as tag by default'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.sdk_connection.compute

        server = compute_client.find_server(
            parsed_args.server,
            ignore_missing=False,
        )
        if parsed_args.tag:
            tag = parsed_args.tag
        else:
            tag = parsed_args.share_id
        share = compute_client.create_share_attachment(
            server, parsed_args.share_id, tag=tag
        )

        display_columns, columns = _get_server_share_columns(
            compute_client,
            share,
        )
        data = utils.get_item_properties(share, columns)
        return display_columns, data


class RemoveServerShare(command.Command):
    """Delete a share attachment to a server.

    Note: This api is available since nova microversion 2.97.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server to delete share mapping for (name or ID)'),
        )
        parser.add_argument(
            'share_id',
            metavar='<share-id>',
            help=_('Share to delete (ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.sdk_connection.compute

        server = compute_client.find_server(
            parsed_args.server,
            ignore_missing=False,
        )
        compute_client.delete_share_attachment(server, parsed_args.share_id)
