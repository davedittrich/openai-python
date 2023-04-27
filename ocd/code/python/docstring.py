# -*- coding: utf-8 -*-

"""
Create a docstring for Python code.
"""

# Standard imports
import logging
import sys

from pathlib import Path

# External imports
from cliff.command import Command

# Local imports
import openai
from ocd.utils import ranged_type


# pyright: reportGeneralTypeIssues=false


class CodePythonDocstring(Command):
    """
    Create a docstring for Python code.

    Defaults to the current version of Python being used to run 'ocd'.
    To use a different Python version, use the `--python-version` option.

    By default, this command works like a filter, reading code from
    standard input and writing to standard output. You can instead
    get the code from a file using the `--source` option and can write
    the result to a file using the `--destination` option.
    """

    logger = logging.getLogger(__name__)

    def get_parser(self, prog_name):  # noqa
        python_version = ".".join([
            str(sys.version_info.major),
            str(sys.version_info.minor)
        ])
        parser = super().get_parser(prog_name)
        # Hack to validate Python version. Not ideal, but sort of works.
        parser.add_argument(
            "--python-version",
            default=float(python_version),
            type=ranged_type(float, 3.7, 3.10),
            help="Python version to use",
        )
        parser.add_argument(
            "-m", "--model",
            dest="model_id",
            default=self.app.defaults.CODEX_MODEL_ID,
            help="ID of the model to use",
        )
        parser.add_argument(
            "--temperature",
            default=self.app.defaults.CODEX_TEMPERATURE,
            type=ranged_type(float, 0.0, 1.0),
            help="sampling temperature to use",
        )
        parser.add_argument(
            "--max-tokens",
            default=self.app.defaults.CODEX_MAX_TOKENS,
            help="maximum tokens",
        )
        parser.add_argument(
            "--top-p",
            type=float,
            default=1.0,
            help="top p",
        )
        parser.add_argument(
            "--frequency-penalty",
            type=float,
            default=0.0,
            help="frequency penalty",
        )
        parser.add_argument(
            "--presence-penalty",
            type=float,
            default=0.0,
            help="presence penalty",
        )
        parser.add_argument(
            "--source",
            default='-',
            help="read code from source file instead of stdin",
        )
        parser.add_argument(
            "--destination",
            default='-',
            help="write docstring to file instead of stdout",
        )
        return parser

    def take_action(self, parsed_args):  # noqa
        if parsed_args.source == '-':
            source_code = sys.stdin.read()
        else:
            source_code = Path(parsed_args.source).read_text(encoding='utf-8')
        prompt = (
            f'# Python {parsed_args.python_version}\n'
            f'\n{source_code}\n'
            '# An elaborate, high quality docstring for the above function:\n'
            '"""'
        )
        response = openai.Completion.create(
            prompt=prompt,
            model=parsed_args.model_id,
            temperature=parsed_args.temperature,
            max_tokens=parsed_args.max_tokens,
            top_p=parsed_args.top_p,
            frequency_penalty=parsed_args.frequency_penalty,
            presence_penalty=parsed_args.presence_penalty,
            stop=['#', '"""']
        )
        if not response:
            raise RuntimeError("[-] no response received")
        finish_reason = response['choices'][0]['finish_reason']
        docstring = response['choices'][0]['text']
        result = f'"""\n{docstring}\n"""\n'
        if finish_reason != 'stop':
            self.logger.info(
                "[-] completion did not stop normally: %s",
                finish_reason,
            )
        if parsed_args.destination == '-':
            print(result)
        else:
            outfile_path = Path(parsed_args.destination)
            outfile_path.write_text(result, encoding='utf-8')


# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :
