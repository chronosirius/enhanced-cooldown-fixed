from setuptools import setup
from re import search, MULTILINE

with open("interactions/ext/better_interactions/__init__.py") as f:
    version = search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), MULTILINE
    ).group(1)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="better-interactions",
    version=version,
    description="Better interactions for discord-py-interactions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Toricane/better-interactions",
    author="Toricane",
    author_email="prjwl028@gmail.com",
    license="MIT",
    packages=["interactions.ext.better_interactions"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "discord-py-interactions>=4.0.1",
        "interactions-wait-for",
    ],
)
