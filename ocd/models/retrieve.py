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

    Fields are shown one row at a time::

        $ ocd models retrieve curie
        +----------+------------+
        | Field    | Value      |
        +----------+------------+
        | id       | curie      |
        | object   | model      |
        | created  | 1649359874 |
        | owned_by | openai     |
        | root     | curie      |
        | parent   | None       |
        +----------+------------+

    To see the model permissions, use the ``--permission`` option::

        $ ocd models retrieve curie --permission
        +----------------------+------------------------------------+
        | Field                | Value                              |
        +----------------------+------------------------------------+
        | id                   | modelperm-oPaljeveTjEIDbhDjzFiyf4V |
        | object               | model_permission                   |
        | created              | 1675106503                         |
        | allow_create_engine  | False                              |
        | allow_sampling       | True                               |
        | allow_logprobs       | True                               |
        | allow_search_indices | False                              |
        | allow_view           | True                               |
        | allow_fine_tuning    | False                              |
        | organization         | *                                  |
        | group                | None                               |
        | is_blocking          | False                              |
        +----------------------+------------------------------------+

    To get the raw results, use the ``--raw`` option::

        $ ocd model retrieve curie --raw
        [organization=user-waomxsvz183exp61ebmrx645] {
          "created": 1649359874,
          "id": "curie",
          "object": "model",
          "owned_by": "openai",
          "parent": null,
          "permission": [
            {
              "allow_create_engine": false,
              "allow_fine_tuning": false,
              "allow_logprobs": true,
              "allow_sampling": true,
              "allow_search_indices": false,
              "allow_view": true,
              "created": 1675106503,
              "group": null,
              "id": "modelperm-oPaljeveTjEIDbhDjzFiyf4V",
              "is_blocking": false,
              "object": "model_permission",
              "organization": "*"
            }
          ],
          "root": "curie"
        }

    KNOWN LIMITATIONS: At this time, only one permission object is handled
    for tabular output.

    """

    logger = logging.getLogger(__name__)

    def get_parser(self, prog_name):  # noqa
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--permission',
            action='store_true',
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
