# Local ChatGPT (Fully Offline)

Local ChatGPT is a **100% offline ChatGPT-style application** built using **Chainlit** and **Ollama**, powered by the **Llama 3.2 Vision** model.  
It allows you to chat with a large language model locally on your machine, without using any external APIs or cloud services.

This project supports:
- Text-based conversations
- Image-based queries (vision model)
- Streaming responses
- Local session-based memory

---

## What This Project Does

- Runs an AI chat assistant **entirely on your local system**
- Uses **Ollama** to run open-source LLMs locally
- Uses **Chainlit** to provide a clean ChatGPT-like web UI
- Streams responses in real time
- Maintains conversation context across messages
- Supports multimodal input (text + images)

This project is useful for:
- Learning how local LLM applications work
- Experimenting with open-source models
- Building privacy-friendly AI tools
- Understanding chat memory and streaming responses

---

## How It Works (High Level)

1. The user interacts with a web-based chat UI powered by Chainlit
2. Messages (and images, if provided) are stored in session memory
3. The conversation history is sent to a local LLM via Ollama
4. The model generates responses, which are streamed back to the UI
5. Conversation history is trimmed to avoid unlimited context growth

---

## Requirements

- Python **3.11 or later**
- Ollama installed locally
- A machine capable of running Llama 3.2 Vision

---

## Installation & Setup

### 1. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
Pull the required model:
ollama pull llama3.2-vision
Install Python Dependencies
pip install pydantic==2.10.1 chainlit ollama
Run the Application
From the project directory:
chainlit run app.py -w
Once started, open the provided local URL in your browser to access the chat interface.

License

This project is licensed under the MIT License.
