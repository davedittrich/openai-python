# -*- coding: utf-8 -*-

"""
Create a completion using a model.
"""

# Standard imports
import logging
import sys

# External imports
from cliff.show import ShowOne

# Local imports
import openai
from ocd.utils import (
    Defaults,
    get_text_from_completion,
    ranged_type,
    print_completion,
)

defaults = Defaults()


class CompletionsCreate(ShowOne):
    """
    Create a completion from a prompt using a model.

    The prompt is the string used to generate the completion.
    Trailing whitespace is removed from the prompt as it impacts
    tokenization of the prompt string. While the OpenAI API allows for
    the prompt to be a list of strings or tokens in addition to just
    a simple string, passing those is not supported at this time::

        $ ocd completion create --prompt "What is the exact text of the first sentence in the U.S. Constitution?"
        +------------+-----------------------------------------------------------------------+
        | Field      | Value                                                                 |
        +------------+-----------------------------------------------------------------------+
        | prompt     | What is the exact text of the first sentence in the U.S. Constitution? |
        | completion |                                                                       |
        |            |                                                                       |
        |            | We the People of the United States, in Order to form a more           |
        +------------+-----------------------------------------------------------------------+

    The leading whitespace in the completion is retained unless the ``--trim`` option is specified.

    To get the full response from the API in JSON format, use the ``--raw`` option::

        $ ocd completion create --prompt "What is the exact text of the first sentence in the U.S. Constitution?" --raw
        [organization=user-waomxsvz183exp61ebmrx645] {
          "choices": [
            {
              "finish_reason": "length",
              "index": 0,
              "logprobs": null,
              "text": "\n\n\"We the People of the United States, in Order to form a"
            }
          ],
          "created": 1675116632,
          "id": "cmpl-6eWe8bdBPXA6Sx8lmLMus7xf7cZUF",
          "model": "curie-instruct-beta",
          "object": "text_completion",
          "usage": {
            "completion_tokens": 16,
            "prompt_tokens": 18,
            "total_tokens": 34
          }
        }

    You can request more than one completion using the ``-n`` option,
    though you should be cautious using this option as it can quickly
    use up a large number of tokens. The default output format is
    tabular and the leading whitespace in completions is maintained::

        +--------------+-------------------------------------+
        | Field        | Value                               |
        +--------------+-------------------------------------+
        | prompt       | Give a single name for a boy. Name: |
        | completion_1 |                                     |
        |              |                                     |
        |              |  Liam                               |
        | completion_2 |                                     |
        |              |                                     |
        |              | Derek                               |
        | completion_3 |                                     |
        |              |                                     |
        |              | Ethan                               |
        | completion_4 |  Adam                               |
        +--------------+-------------------------------------+

    The ``--trim`` option removes whitespace from the completions::

        +--------------+-------------------------------------+
        | Field        | Value                               |
        +--------------+-------------------------------------+
        | prompt       | Give a single name for a boy. Name: |
        | completion_1 | Kai                                 |
        | completion_2 | Connor                              |
        | completion_3 | Miles                               |
        | completion_4 | Luke                                |
        +--------------+-------------------------------------+

    The ``--text`` option outputs the completions without including the
    prompt or using the tabular formatting feature. It can be combined
    with the ``--trim`` option to get cleaner output::

        ===== Completion 0 =====
        Adam
        ===== Completion 1 =====
        Dylan
        ===== Completion 2 =====
        David
        ===== Completion 3 =====
        Landon

    You can optionally specify a suffix, which is a string that
    comes after a completion of inserted text.

    For information on sampling temperature, see:
    "How to sample from language models", by Ben Mann, Medium, May 24, 2019,
    https://towardsdatascience.com/how-to-sample-from-language-models-682bceb97277

    """

    logger = logging.getLogger(__name__)

    def get_parser(self, prog_name):  # noqa
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "-m", "--model",
            dest="model_id",
            default=defaults.MODEL_ID,
            help="ID of the model to use",
        )
        parser.add_argument(
            "--echo",
            action="store_true",
            default=False,
            help="echo back the prompt in addition to the completion",
        )
        parser.add_argument(
            "--max-tokens",
            default=defaults.MAX_TOKENS,
            help="maximum tokens",
        )
        parser.add_argument(
            "--temperature",
            default=defaults.TEMPERATURE,
            type=ranged_type(float, 0.0, 1.0),
            help="sampling temperature to use",
        )
        parser.add_argument(
            "--prompt",
            default=None,
            required=True,
            help="prompt for completion",
        )
        parser.add_argument(
            "--suffix",
            default=None,
            help="suffix that comes after a completion of inserted text",
        )
        output_group = parser.add_mutually_exclusive_group()
        output_group.add_argument(
            "-a", "--all",
            action="store_true",
            default=False,
            help="return all results in the completion",
        )
        output_group.add_argument(
            "-u", "--usage",
            action="store_true",
            default=False,
            help="output usage information",
        )
        return parser

    def take_action(self, parsed_args):  # noqa
        prompt = parsed_args.prompt.strip()
        completion = openai.Completion.create(
            model=parsed_args.model_id,
            prompt=prompt,
            suffix=parsed_args.suffix,
            temperature=parsed_args.temperature,
            echo=parsed_args.echo,
        )
        if not completion:
            raise RuntimeError("[-] no completion produced")
        if parsed_args.echo:
            print_completion(get_text_from_completion(completion))  # noqa
            sys.exit(0)
        columns = ['prompt', 'completion']
        data = [
            prompt,
            (
                completion if parsed_args.all
                else get_text_from_completion(completion)
            )
        ]
        if parsed_args.usage:
            for key, value in completion.usage.items():  # type: ignore
                columns.append(key)
                data.append(value)
        return columns, data


# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :

