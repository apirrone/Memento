# Poor man's rewind.ai

A reimplementation or rewind.ai using chromadb

https://github.com/apirrone/poor_mans_rewind/assets/6552564/e48a6415-ed9c-46c0-bac1-6a364044372e


https://github.com/apirrone/poor_mans_rewind/assets/6552564/f2f42333-df4f-4d5a-affb-4db0f1ca6be0





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


## TODO / Ideas
- langchain llm to chat with the timeline
- summary of your day (?)
- activity stats
  
