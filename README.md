# Local Chat with Ollama

### A local multimodal chat interface with streaming responses.

A compact Python application connecting a Chainlit interface to Ollama. It supports text and image input, retains recent conversation turns in session memory, and exposes generation settings through environment variables.

## How it works

1. Chainlit receives a message and optional image attachments.
2. The application adds them to the session conversation.
3. Ollama generates a response using the configured local model.
4. Tokens stream into the interface; conversation history is trimmed to a bounded number of messages.

Inference runs locally when Ollama is configured locally. Installing dependencies and downloading model weights require network access. Session history is in memory rather than a persistent conversation database.

## Quick start

Prerequisites: Python 3.11+, [Ollama](https://ollama.com/), and hardware with enough memory for the selected model.

```bash
git clone https://github.com/mahasmrtiadhuri/local-chatgpt-ollama.git
cd local-chatgpt-ollama
python -m venv .venv
source .venv/bin/activate
python -m pip install pydantic==2.10.1 chainlit ollama
ollama pull llama3.2-vision
chainlit run app.py -w
```

Ensure the Ollama service is running, then open the local URL printed by Chainlit. Model download size and inference speed depend on the selected model and hardware.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_MODEL` | `llama3.2-vision` | Local model name |
| `SYSTEM_PROMPT` | `You are a helpful assistant.` | Initial system message |
| `MAX_TURNS` | `12` | Recent user/assistant turns retained |
| `TEMPERATURE` | `0.2` | Sampling temperature |
| `TOP_P` | `0.9` | Nucleus sampling setting |
| `NUM_PREDICT` | `512` | Generation token limit |

Example:

```bash
OLLAMA_MODEL=llama3.2-vision MAX_TURNS=6 chainlit run app.py -w
```

## Code map

| Function in `app.py` | Responsibility |
|---|---|
| `ensure_session` | Initialize conversation state |
| `trim_interaction` | Preserve the system message and recent history |
| `stream_from_ollama` | Forward generated tokens to the interface |
| `start_chat` | Initialize the chat interface |
| `main` | Handle messages and image attachments |

## Scope and limitations

History is bounded by message count, not token count. The current inference loop uses the synchronous Ollama client inside an async handler; concurrent sessions may block during generation. Dependency versions are not fully locked. A useful next iteration is an asynchronous model adapter with tests for streaming response formats and failure handling.
