from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="better-interactions",
    version="1.3.2",
    description="Better components for discord-py-interactions",
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
        "discord-py-interactions",
        "interactions-wait-for",
    ],
)
