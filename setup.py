from os import path
from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pmr",
    version="0.0.1",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "mss==9.0.1",
        "numpy==1.25.1",
        "opencv-contrib-python==4.8.0.74",
        "chromadb==0.4.3",
        "pytesseract==0.3.10",
        "xlib==0.21",
        "av==10.0.0",
        "pygame==2.5.0"
    ],
    entry_points={
        "console_scripts": [
            "pmr-bg = pmr:bg",
            "pmr-query = pmr:query",
            "pmr-timeline = pmr:timeline",
        ]
    },
    author="Antoine Pirrone",
    author_email="antoine.pirrone@gmail.com",
    url="https://github.com/apirrone/poor_mans_rewind",
    description="Poor man's rewind.ai",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
