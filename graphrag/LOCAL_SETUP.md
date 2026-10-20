# Local schema extraction

The extractor uses `qwen2.5:7b` served by Ollama at
`http://127.0.0.1:11434/v1`. Neo4j's `OpenAILLM` adapter supplies the
OpenAI-compatible protocol; requests go to this local endpoint. The dummy
`ollama` API key does not require an OpenAI account.

Install the protocol client into the project's virtual environment:

```sh
venv/bin/python -m pip install 'neo4j-graphrag[openai]'
```

Install Ollama, then start its server in a terminal:

```sh
ollama serve
```

In another terminal, download the model (about 4.7 GB):

```sh
ollama pull qwen2.5:7b
```

From the repository root, run the one-sentence extraction example:

```sh
venv/bin/python -m graphrag.extract_schema
```

