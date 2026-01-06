import os
import asyncio
import chainlit as cl
import ollama

# =========================
# Config (env overrides)
# =========================
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2-vision")
SYSTEM_PROMPT_DEFAULT = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant.")

# Keep only the last N turns (a turn ~ user + assistant). System prompt is always kept.
MAX_TURNS = int(os.getenv("MAX_TURNS", "12"))

# Generation options (Ollama supports these via "options")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
TOP_P = float(os.getenv("TOP_P", "0.9"))
NUM_PREDICT = int(os.getenv("NUM_PREDICT", "512"))  # approximate max tokens


def ensure_session() -> None:
    """Initialize chat state for the user session."""
    if cl.user_session.get("interaction") is None:
        cl.user_session.set(
            "interaction",
            [{"role": "system", "content": SYSTEM_PROMPT_DEFAULT}],
        )


def trim_interaction(interaction: list[dict]) -> list[dict]:
    """
    Prevent unbounded context growth:
    keep the system prompt + last MAX_TURNS*2 messages.
    """
    if not interaction:
        return [{"role": "system", "content": SYSTEM_PROMPT_DEFAULT}]

    # Ensure we have a system message first
    if interaction[0].get("role") != "system":
        interaction = [{"role": "system", "content": SYSTEM_PROMPT_DEFAULT}] + interaction

    system = interaction[0]
    rest = interaction[1:]

    keep = MAX_TURNS * 2  # user+assistant pairs
    if len(rest) > keep:
        rest = rest[-keep:]

    return [system] + rest


async def stream_from_ollama(messages: list[dict], ui_msg: cl.Message) -> str:
    """
    Stream completion tokens from Ollama into Chainlit UI.
    Returns the final concatenated text.
    """
    full_text = ""

    try:
        stream = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            stream=True,
            options={
                "temperature": TEMPERATURE,
                "top_p": TOP_P,
                "num_predict": NUM_PREDICT,
            },
        )

        for chunk in stream:
            token = ""
            if isinstance(chunk, dict):
                token = (chunk.get("message") or {}).get("content") or ""

            if token:
                full_text += token
                await ui_msg.stream_token(token)

        return full_text

    except Exception as e:
        err_text = (
            "⚠️ Error calling the local model.\n\n"
            f"**Model:** {MODEL_NAME}\n"
            f"**Error:** {type(e).__name__}: {e}\n\n"
            "Try: (1) ensure Ollama is running, (2) verify the model is pulled, "
            "(3) restart the app, or (4) send a shorter message."
        )
        await ui_msg.stream_token(err_text)
        return err_text


@cl.on_chat_start
async def start_chat():
    ensure_session()

    msg = cl.Message(content="")
    welcome = (
        f"Hello! I’m your **100% local** ChatGPT-style assistant running on **{MODEL_NAME}**.\n"
        "Send a message (and optionally an image) to get started."
    )

    for ch in welcome:
        await msg.stream_token(ch)
        await asyncio.sleep(0)  # yield to event loop

    await msg.send()


@cl.on_message
async def main(message: cl.Message):
    ensure_session()

    interaction = cl.user_session.get("interaction") or []
    interaction = trim_interaction(interaction)

    # Collect image paths (Chainlit provides elements with mime + path)
    images = [el for el in (message.elements or []) if getattr(el, "mime", "") and "image" in el.mime]
    image_paths = [img.path for img in images] if images else None

    # Append user message (with images if present)
    user_msg: dict = {"role": "user", "content": message.content}
    if image_paths:
        user_msg["images"] = image_paths

    interaction.append(user_msg)

    # Create an empty assistant message and stream into it
    ui_msg = cl.Message(content="")
    await ui_msg.send()

    assistant_text = await stream_from_ollama(interaction, ui_msg)

    # Save assistant response in memory
    interaction.append({"role": "assistant", "content": assistant_text})

    # Trim again in case response was long
    interaction = trim_interaction(interaction)
    cl.user_session.set("interaction", interaction)


