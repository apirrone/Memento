# Poor man's rewind.ai

A reimplementation or rewind.ai using chromadb

TODO Demo video





## Install

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
$ pmr-bg
```

### Timeline mode: 

```console
$ pmr-timeline
```

Then use `ctrl+f` to search.

If you want to chat with the timeline through a llm, you need an openai api key in your env as `OPENAI_API_KEY`.
Then use `ctrl+t` to open the chatbox.
  
