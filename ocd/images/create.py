# -*- coding: utf-8 -*-

"""
Create one or more images from a prompt.
"""

# Standard imports
import base64
import io
import logging

from pathlib import Path

# External imports
from cliff.command import Command
from PIL import Image

# Local imports
import openai
from ocd.utils import (
    Defaults,
    open_browser,
    ranged_type,
)

defaults = Defaults()
logger = logging.getLogger(__name__)


def fail_if_file_exists(file_path: Path):
    """
    Check to see if a file exists with the specified
    name and raise an exception if so.
    """
    if file_path.exists():
        raise FileExistsError(
            "[-] file exists (use '--force' to over-write):"
            f" {str(file_path)}"
        )

def write_image_to_file(filename, b64_json, verbose=False):
    """
    Convert Base64 JSON to image data and write to a file.
    """
    image_data = base64.b64decode(b64_json)
    image = Image.open(io.BytesIO(image_data))
    image.save(filename)
    if verbose:
        logger.info("[+] wrote image to file: %s", filename)


class ImagesCreate(Command):
    """
    Create one or more images from a prompt.
    """

    logger = logging.getLogger(__name__)

    def get_parser(self, prog_name):  # noqa
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--prompt",
            default=None,
            required=True,
            help="text description of the desired image(s)",
        )
        parser.add_argument(
            "--basename",
            default="IMAGE",
            help="basename of the generated image(s)",
        )
        parser.add_argument(
            "-n",
            default=defaults.IMAGES_N,
            type=ranged_type(int, 1, defaults.MAX_IMAGES_N),
            help="sampling temperature to use",
        )
        parser.add_argument(
            "--size",
            default=defaults.IMAGES_SIZES[0],
            choices=defaults.IMAGES_SIZES,
            help="sampling temperature to use",
        )
        parser.add_argument(
            "--response-format",
            default=defaults.IMAGES_RESPONSE_FORMATS[0],
            choices=defaults.IMAGES_RESPONSE_FORMATS,
            help="format in which the generated image(s) are returned",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help="over-write existing files if they exist",
        )
        return parser

    def take_action(self, parsed_args):  # noqa
        if len(parsed_args.prompt) > defaults.MAX_IMAGES_PROMPT:
            raise ValueError(
                "[-] prompt cannot exceed "
                f"{defaults.MAX_IMAGES_PROMPT} characters"
            )
        image_file_path = []
        if parsed_args.response_format != "b64_json":
            # Pre-generate file names and prevent wasting time creating
            # images if writing would fail because '--force' is False.
            for i in range(0, parsed_args.n):
                file_path = Path(f"{parsed_args.basename}_{i}.png")
                if not parsed_args.force:
                    fail_if_file_exists(file_path)
                image_file_path.append(file_path)
        response = openai.Image.create(
            prompt=parsed_args.prompt,
            n=parsed_args.n,
            size=parsed_args.size,
            response_format=parsed_args.response_format,
        )
        for i, image in enumerate(response.data):  # type: ignore
            if "b64_json" in image:
                write_image_to_file(
                    image_file_path[i],
                    image.b64_json,
                    verbose=self.app_args.verbose_level > 1,
                )
                url_path = f"file://{image_file_path[i].absolute()}"
            elif "url" in image:
                url_path = image.url
            else:
                raise ValueError("[-] unsupported image type")
            open_browser(
                page=url_path,
                browser=self.app_args.browser,
                force=self.app_args.force_browser,
                logger=logger,
            )


# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :
