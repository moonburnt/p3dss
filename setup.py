from os.path import join
from setuptools import setup

VERSION = 0.1

WORKDIR = "."
README = join(WORKDIR, "README.md")
DESCRIPTION_TYPE = "text/markdown"

# Iirc python's default encoding is already utf-8, but just in case
with open(README, encoding = 'utf-8') as f:
    long_description = f.read()

setup(
    name = "p3dss",
    version = VERSION,
    description = "p3dss - the spritesheet handling library for Panda3D",
    long_description = long_description,
    long_description_content_type = DESCRIPTION_TYPE,
    url = "https://github.com/moonburnt/p3dss",
    author = "moonburnt",
    license = "MIT",
    classifiers = [ "Programming Language :: Python :: 3" ],
    packages = [ 'p3dss' ],
    install_requires=[ "panda3d>=1.10" ]
    )
