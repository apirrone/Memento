# Poor man's rewind.ai

A reimplementation or rewind.ai using chromadb



https://github.com/apirrone/poor_mans_rewind/assets/6552564/e48a6415-ed9c-46c0-bac1-6a364044372e



## Install

```console
$ pip install -e .
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
  
