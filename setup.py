from re import MULTILINE, search

from setuptools import setup
from torch import long

with open("interactions/ext/better_interactions/__init__.py") as f:
    version = search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), MULTILINE).group(1)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


from interactions.ext import Base, Version, VersionAuthor, build

# gets the long description from the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# data for pypi:
version = Version(
    major=3,
    minor=0,
    patch=0,
    author=VersionAuthor(name="Toricane", email="prjwl028@gmail.com"),
)

data = {
    "name": "better_interactions",
    "description": "Better interactions for interactions.py",
    "long_description": long_description,
    "version": version,
    "link": "https://github.com/Toricane/better-interactions",
    "dependencies": ["interactions.ext.better_interactions"],
    "requirements": ["discord-py-interactions>=4.1.0"],
}

build(Base(**data))
