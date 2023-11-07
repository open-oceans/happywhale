import setuptools
from setuptools import find_packages


def readme():
    with open("README.md") as f:
        return f.read()


setuptools.setup(
    name="happywhale",
    version="0.0.1",
    packages=find_packages(),
    url="https://github.com/samapriya/happywhale",
    install_requires=[
        "requests>=2.31.0",
        "pandas>=2.1.2",
        "pipgeo>=0.0.6;platform_system=='Windows'",
        "geojson >= 2.5.0",
    ],
    license="Apache 2.0",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Oceanography",
    ],
    author="Samapriya Roy",
    author_email="samapriya.roy@gmail.com",
    description="Simple CLI for HappyWhale.com",
    entry_points={
        "console_scripts": [
            "happywhale=happywhale.happywhale:main",
        ],
    },
)
