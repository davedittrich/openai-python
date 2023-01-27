import os

from setuptools import find_packages, setup

version_contents = {}
version_path = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "openai/version.py"
)
with open(version_path, "rt") as f:
    exec(f.read(), version_contents)  # nosec

with open("README.md", "r") as fh:
    long_description = fh.read()


DATA_LIBRARIES = [
    # These libraries are optional because of their size. See `openai/datalib.py`.
    "numpy",
    "pandas>=1.2.3",  # Needed for CLI fine-tuning data preparation tool
    "pandas-stubs>=1.1.0.11",  # Needed for type hints for mypy
    "openpyxl>=3.0.7",  # Needed for CLI fine-tuning data preparation tool xlsx format
]

setup(
    name="openai",
    description="Python client library for the OpenAI API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=version_contents["VERSION"],
    install_requires=[
        "cliff",  # For CLI framework
        "requests>=2.20",  # to get the patch for CVE-2018-18074
        "tqdm",  # Needed for progress bars
        "python-secrets",  # For flexibility in accessing secrets and state apart from source code
        'tiktoken',  # Needed for calculating number of tokens
        'typing_extensions;python_version<"3.8"',  # Needed for type hints for mypy
        "aiohttp",  # Needed for async support
        "Pillow",  # Needed for manipulating images
    ],
    extras_require={
        "dev": ["black~=21.6b0", "pytest==6.*", "pytest-asyncio", "pytest-mock"],
        "datalib": DATA_LIBRARIES,
        "wandb": [
            "wandb",
            *DATA_LIBRARIES,
        ],
        "embeddings": [
            "scikit-learn>=1.0.2",  # Needed for embedding utils, versions >= 1.1 require python 3.8
            "tenacity>=8.0.1",
            "matplotlib",
            "sklearn",
            "plotly",
            *DATA_LIBRARIES,
        ],
    },
    python_requires=">=3.7.1",
    entry_points={
        "console_scripts": [
            "openai=openai._openai_scripts:main",
            "ocd=ocd.__main__:main",
        ],
        "ocd": [
            "completions create=ocd.completions.create:CompletionsCreate",
            "edits create=ocd.edits.create:EditsCreate",
            "fine-tune list=ocd.fine_tune.list:FineTuneList",
            "images create=ocd.images.create:ImagesCreate",
            "models list=ocd.models.list:ModelsList",
            "models retrieve=ocd.models.retrieve:ModelsRetrieve",
            "models overview=ocd.models.overview:ModelsOverview",
            "text analyze=ocd.text.analyze:TextAnalyze",
        ]
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={
        "openai": [
            "py.typed",
        ]
    },
    author="OpenAI",
    author_email="support@openai.com",
    url="https://github.com/openai/openai-python",
)
