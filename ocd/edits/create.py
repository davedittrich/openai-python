# -*- coding: utf-8 -*-

"""
Edit a prompt given an instruction and return the result.
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


class EditsCreate(ShowOne):
    """
    Edit a prompt given an instruction and return the result.

    The prompt is the string to be edited. It is provided as input to the
    model, along with an instruction that tells the model how to edit
    the prompt.

    Trailing whitespace is removed from the prompt as it impacts
    tokenization of the prompt string. While the OpenAI API allows for
    the prompt to be a list of strings or tokens in addition to just
    a simple string, passing those is not supported at this time.

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
            default=defaults.EDIT_MODEL_ID,
            help="ID of the model to use",
        )
        parser.add_argument(
            "-n",
            default=defaults.N,
            type=ranged_type(int, 1, 10),
            help="how many edits to generate",
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
            "--instruction",
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
        if parsed_args.n > 1 and not parsed_args.all:
            # Hack to get around lack of support for multiple
            # completion choices.
            parsed_args.all = True
            parsed_args.usage = False
        prompt = parsed_args.prompt.rstrip()
        completion = openai.Edit.create(
            model=parsed_args.model_id,
            input=prompt,
            instruction=parsed_args.instruction,
            temperature=parsed_args.temperature,
            n=parsed_args.n,
        )
        if not completion:
            raise RuntimeError("[-] no completion produced")
        if not (
            parsed_args.all or parsed_args.usage or parsed_args.n > 1
        ):
            print_completion(get_text_from_completion(completion))
            sys.exit(0)
        columns = ['prompt', 'instruction', 'completion']
        data = [
            prompt,
            parsed_args.instruction,
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
