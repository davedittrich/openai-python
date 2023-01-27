# -*- coding: utf-8 -*-

"""
Initialization file for `ocd` command classes.
"""

# Standard imports
import argparse
import subprocess  # nosec
import sys
import webbrowser

from pathlib import Path

# External imports
import tiktoken

# Local imports
import openai


DEFAULT_EDIT_MODEL_ID = 'text-davinci-edit-001'
DEFAULT_EMBEDDING_MODEL_ID = 'text-embedding-ada-002'
DEFAULT_IMAGES_N = 1
DEFAULT_MAX_TOKENS = 16
DEFAULT_MODEL_ID = 'curie-instruct-beta'
DEFAULT_TEMPERATURE = '0.9'
IMAGES_SIZES = [
    "256x256",
    "512x512",
    "1024x1024"
]
IMAGES_RESPONSE_FORMATS = [
    'b64_json',
    'url',
]
MAX_IMAGES_PROMPT = 1000
MAX_IMAGES_N = 10


def get_text_from_completion(completion):
    return completion.choices[0].text

def get_model_ids(model_list=None):
    """
    Return a list of model ids from a list of models returned by the
    OpenAI API.
    """
    if model_list is None:
        model_list = openai.Model.list()
    return (model.id for model in model_list)


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """
    Returns the number of tokens in a text string.

    Trailing whitespace is removed from the string as it impacts
    tokenization.
    """
    encoding = tiktoken.get_encoding(encoding_name)
    # Strip trailing whitespace from the string
    num_tokens = len(encoding.encode(string.strip()))
    return num_tokens


def save_tokens_to_file(file_name: str, tokens: list) -> None:
    """Save the tokens."""
    raise NotImplementedError


def get_file_type(file_path: Path) -> str:
    p = subprocess.Popen(
        ['/usr/bin/file', '-b', file_path.name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False  # nosec
    )
    pout, perr = p.communicate()
    return (
        pout.decode('utf-8').strip() if len(perr) == 0
        else str(file_path.suffix[1:]).upper()
    )


# Based on: https://stackoverflow.com/a/64259328
def ranged_type(value_type, min_value, max_value):
    """
    Return function handle of an argument type function for ArgumentParser checking a range:
        min_value <= arg <= max_value

    Parameters
    ----------
    value_type  - value-type to convert arg to
    min_value   - minimum acceptable argument
    max_value   - maximum acceptable argument

    Returns
    -------
    function handle of an argument type function for ArgumentParser


    Usage
    -----
        ranged_type(float, 0.0, 1.0)

    """

    def range_checker(arg: str):
        try:
            f = value_type(arg)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f'[-] must be a valid {value_type}'
            )
        if f < min_value or f > max_value:
            raise argparse.ArgumentTypeError(
                f'[-] must be within [{min_value}, {min_value}]'
            )
        return f

    # Return function handle to checking function
    return range_checker


def print_completion(string: str) -> None:
    """
    Output a completion string to stdout, replacing backslash-n
    with actual newline characters.
    """
    print(string.replace('\\n', '\n'))


def open_browser(
    page=None,
    browser=None,
    force=False,
    logger=None,
):
    """
    Open web browser to specified page.
    """
    if not sys.stdin.isatty() and not force:
        raise RuntimeError(
            "[-] use --force to open browser when stdin is not a TTY"
        )
    if page is None:
        raise RuntimeError("[-] not page specified")
    which = "system default" if browser is None else browser
    if logger is not None:
        logger.info("[+] opening browser '%s' for %s", which, page)
    if browser is not None:
        controller = webbrowser.get(using=browser)
        controller.open_new_tab(page)
    else:
        webbrowser.open(page, new=1)

# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :
