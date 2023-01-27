# -*- coding: utf-8 -*-

"""
Show details about a single model.
"""

# Standard imports
import logging
import sys

# External imports
from cliff.show import ShowOne

# Local imports
import openai


class ModelsRetrieve(ShowOne):
    """
    Show details about a single model.

    To see the model permissions, use the ``--permission`` option.
    """

    logger = logging.getLogger(__name__)

    def get_parser(self, prog_name):  # noqa
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--permission',
            action='store_true',
            dest='permission',
            default=False,
            help='show model permission settings'
        )
        parser.add_argument(
            "model",
            nargs=1,
            metavar="MODEL_ID",
            help="model identifier",
        )
        return parser

    def take_action(self, parsed_args):  # noqa
        model = openai.Model.retrieve(id=parsed_args.model[0])
        if not model:
            raise RuntimeError("[-] no model data found")
        if len(model.permission) > 1:
            # TODO(dittrich): Change how permissions are handled when > 1.
            # I'm guessing that a list is to handle different permissions
            # based on organization and/or group identifiers?
            raise RuntimeError("[-] more than one permission found")
        items = (
            model.permission[0].items()
            if parsed_args.permission
            else model.items()
        )
        columns = []
        data = []
        for key, value in items:
            if not isinstance(value, list):
                columns.append(key)
                data.append(value)
        if len(data) == 0:
            sys.exit(1)
        return columns, data


# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :
