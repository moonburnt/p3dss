from setuptools import find_packages, setup

VERSION = "0.4.0"

with open("README.md") as f:
    long_description = f.read()

setup(
    name="p3dss",
    version=VERSION,
    description="p3dss - the spritesheet handling library for Panda3D",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/moonburnt/p3dss",
    author="moonburnt",
    author_email="moonburnt@disroot.org",
    license="MIT",
    classifiers=["Programming Language :: Python :: 3"],
    packages=find_packages(),
    install_requires=["panda3d>=1.10"],
    )
