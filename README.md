# Memento (working title)

Memento is a Python app that records everything you do on your computer and lets you go back in time, search, and chat with a LLM (Large Language Model) to find back information about what you did.

https://github.com/apirrone/Memento/assets/6552564/d256a3a9-fa44-4b73-8b8e-b02a5473540b

How it works:
- The app takes a screenshot every 2 seconds
- It compiles the screenshots into h264 video segments for storage efficiency
- It uses OCR to extract text from the images
- It indexes the text in a sqlite3 database and a vectordb
- It uses FTS5 to search the text
- It uses a LLM (GPT through OpenAI's API) to chat with the timeline


This project is heavily inspired by [rewind.ai](https://rewind.ai/)




## Installation

This project was tested on Ubuntu 22.04.

```console
$ pip install -e .
```

You also need to install `tesseract-ocr` on your system. To install latest version (tesseract 5.x.x):

```console
$ sudo apt update
$ sudo add-apt-repository ppa:alex-p/tesseract-ocr-devel
$ sudo apt install tesseract-ocr
```
Then install the language packs you need, for example:

```console
$ sudo apt install tesseract-ocr-eng
$ sudo apt install tesseract-ocr-fra
```

You also need to set an environment variable :
(This is the path on my system, it may be different on yours)
```console
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/
```

## Usage
### Background process
Run in a terminal  
```console
$ memento-bg
```

### Show the timeline:

```console
$ memento-timeline
```

Then use `ctrl+f` to search.

If you want to chat with the timeline through a llm, you need an openai api key in your env as `OPENAI_API_KEY`.
Then use `ctrl+t` to open the chatbox.
  
