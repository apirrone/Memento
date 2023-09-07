from os import path
from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="memento",
    version="0.0.1",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "mss==9.0.1",
        "numpy==1.25.1",
        "opencv-contrib-python==4.8.0.74",
        "xlib==0.21",
        "av==10.0.0",
        "pygame==2.5.0",
        "TextTron==0.45",
        "thefuzz==0.19.0",
        "langchain==0.0.253",
        "openai==0.27.8",
        "tiktoken==0.4.0",
        "python-Levenshtein==0.21.1",
        "tesserocr==2.6.1",
        "pygame-textinput==1.0.1",
        "pyperclip==1.8.2",
        "Pillow==10.0.0",
        "chromadb==0.4.9"
    ],
    entry_points={
        "console_scripts": [
            "memento-bg = memento:bg",
            "memento-timeline = memento:tl",
        ]
    },
    author="Antoine Pirrone",
    author_email="antoine.pirrone@gmail.com",
    url="https://github.com/apirrone/memento",
    description="Memento is a Python app that records everything you do on your computer and lets you go back in time, search, and chat with a LLM (Large Language Model) to find back information about what you did.",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
