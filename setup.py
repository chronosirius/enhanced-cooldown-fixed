from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="enhanced",
    version="3.3.0-rc.1",
    description="Enhanced interactions for interactions.py",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/interactions-py/enhanced",
    author="Toricane",
    author_email="prjwl028@gmail.com",
    license="MIT",
    packages=["interactions.ext.enhanced"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "discord-py-interactions>=4.1.1rc.1",
        "typing_extensions",
    ],
)
