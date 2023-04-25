# -*- coding: utf-8 -*-

"""
List models.
"""

# Standard imports
import logging
import sys

# External imports
from cliff.lister import Lister

# Local imports
import openai


class ModelsList(Lister):
    """
    List models.

    When no name is passed as an argument, all models are returned. Providing a
    name string filters the results to only return the model whose ID exactly
    matches that string::

        $ ocd models list curie
        +-------+--------+------------+----------+-------+--------+
        | id    | object |    created | owned_by | root  | parent |
        +-------+--------+------------+----------+-------+--------+
        | curie | model  | 1649359874 | openai   | curie | None   |
        +-------+--------+------------+----------+-------+--------+

    Adding the `--fuzzy` option expands the results to include all models
    that contain the name string anywhere in the model ID. This is useful
    for identifying the latest model version, fine-tuned models, or
    experimental versions of a model::

        $ ocd models list curie --fuzzy
        +-----------------------------+--------+------------+------------+-----------------------------+--------+
        | id                          | object |    created | owned_by   | root                        | parent |
        +-----------------------------+--------+------------+------------+-----------------------------+--------+
        | curie-instruct-beta         | model  | 1649364042 | openai     | curie-instruct-beta         | None   |
        | curie-search-query          | model  | 1651172509 | openai-dev | curie-search-query          | None   |
        | text-curie-001              | model  | 1649364043 | openai     | text-curie-001              | None   |
        | text-similarity-curie-001   | model  | 1651172507 | openai-dev | text-similarity-curie-001   | None   |
        | text-search-curie-doc-001   | model  | 1651172509 | openai-dev | text-search-curie-doc-001   | None   |
        | text-search-curie-query-001 | model  | 1651172509 | openai-dev | text-search-curie-query-001 | None   |
        | curie-similarity            | model  | 1651172510 | openai-dev | curie-similarity            | None   |
        | curie-search-document       | model  | 1651172508 | openai-dev | curie-search-document       | None   |
        | curie                       | model  | 1649359874 | openai     | curie                       | None   |
        | curie:2020-05-03            | model  | 1607632725 | system     | curie:2020-05-03            | None   |
        | if-curie-v2                 | model  | 1610745968 | openai     | if-curie-v2                 | None   |
        | text-curie:001              | model  | 1641955047 | system     | text-curie:001              | None   |
        +-----------------------------+--------+------------+------------+-----------------------------+--------+
        $ ocd models list embedding --fuzzy
        +------------------------+--------+------------+-----------------+------------------------+--------+
        | id                     | object |    created | owned_by        | root                   | parent |
        +------------------------+--------+------------+-----------------+------------------------+--------+
        | text-embedding-ada-002 | model  | 1671217299 | openai-internal | text-embedding-ada-002 | None   |
        +------------------------+--------+------------+-----------------+------------------------+--------+

    If not otherwise specified, results are sorted by ``created` in descending order. This
    makes it easier to identify the latest models (e.g., a new fine-tuned model that you
    create would show up at the top of the table.) To change this, use the sorting
    control options.

    All model attributes except `model_permission` are shown. Use the column specification
    option to change the columns or their order in the table. To see permission
    settings, use the ``models retrieve`` command with the exact model name::

        $ ocd models list ada --fuzzy -c id -c created -f csv
        "id","created"
        "ada",1649357491
        "text-embedding-ada-002",1671217299
        "text-ada-001",1649364042
        "text-similarity-ada-001",1651172505
        "ada-code-search-code",1651172505
        "ada-similarity",1651172507
        "code-search-ada-text-001",1651172507
        "text-search-ada-query-001",1651172505
        "ada-code-search-text",1651172510
        "text-search-ada-doc-001",1651172507
        "code-search-ada-code-001",1651172507
        "ada-search-query",1651172505
        "ada-search-document",1651172507
        "ada:2020-05-03",1607631625
        "text-ada:001",1641949608
    """  # pylint: disable=line-too-long

    logger = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--fuzzy",
            action="store_true",
            default=False,
            help="match if 'name' occurs anywhere in the model ID",
        )
        parser.add_argument(
            "name",
            metavar="NAME",
            nargs="?",
            default=None,
            help="Search model names for this string",
        )
        return parser

    def take_action(self, parsed_args):  # noqa
        model_list = openai.Model.list()
        if parsed_args.name is None:
            models = model_list.data  # type: ignore
        else:
            models = [
                model for model in model_list.data  # type: ignore
                if (
                    (not parsed_args.fuzzy and model.id == parsed_args.name)
                    or (parsed_args.fuzzy and parsed_args.name in model.id)
                )
            ]
        if not models:
            raise RuntimeError("[-] no model data found")
        # Ignore the model_permission object when listing as it is complex
        columns = []
        for key, value in models[0].items():
            if not isinstance(value, list):
                columns.append(key)
        data = [
            [model.get(column) for column in columns]
            for model in models
        ]
        if len(data) == 0:
            sys.exit(1)
        return columns, data


# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :

