try:
    from interactions.ext import Base, Version, VersionAuthor, build
except ImportError:
    import pip

    pip.main(["install", "git+https://github.com/Toricane/library@unstable"])
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
    "setup_requires": ["discord-py-interactions"],
    "classifiers": [
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    "license": "MIT",
    "author": "Toricane",
    "author_email": "prjwl028@gmail.com",
    "long_description_content_type": "text/markdown",
}

build(Base(**data))
