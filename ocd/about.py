# -*- coding: utf-8 -*-

"""
About OpenAI API access settings.
"""

# Standard imports
import logging

# External imports
from cliff.show import ShowOne

# Local imports
import openai

from openai.error import AuthenticationError


class About(ShowOne):
    """
    About OpenAI API access settings.

    This command helps provide some general information related to API
    access to provide situational awareness::

        +--------------------+-------------------------------+
        | Field              | Value                         |
        +--------------------+-------------------------------+
        | api_key_set        | True                          |
        | api_access_granted | True                          |
        | organization       | user-xxxxxxxxxxxxxxxxxxxxxxxx |
        +--------------------+-------------------------------+

    Note: Organization IDs for personal accounts start with `user-`,
    while organizations defined in paid accounts start with `org-`.
    """

    logger = logging.getLogger(__name__)

    def take_action(self, parsed_args):  # noqa
        columns = ('api_key_set', 'api_access_granted', 'organization')
        try:
            response = openai.Model.list()
        except AuthenticationError:
            response = {}
        data = [
            openai.api_key not in ['', None],
            'data' in response,
            getattr(response, 'organization', None),
        ]
        return columns, data


# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :
