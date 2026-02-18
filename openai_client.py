import json
import random
import time

from openai import(
    APIConnectionError,
    APIError,
    RateLimitError,
    BadRequestError,
    AuthenticationError
)

class OpenAIRequestFailed(Exception):
    """Raised when openAi calls fail after a retry """
    pass

def _backoff_sleep(attempt: int, cap_seconds: float = 10.0 ) -> None:
    delay = min ((2** attempt) + random.random(), cap_seconds)
    time.sleep(delay)

def safe_stream_chat (client, messages, model: str = "gpt-4o-mini", max_retries:int = 3) -> str:
    """
    Streams (prints word one by one) the AI's reply to the console and returns the full reply
    Retries the entire request on the 3 attempts it has 
    """
    for attempt in range(1, max_retries + 1):
        try:
            stream= client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
            full_reply = ""
            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    print(delta.content, end="", flush=True)
                    full_reply += delta.content
            print()
            return full_reply
        except (RateLimitError, APIConnectionError, APIError) as e:
            print(f'\n[Retry {attempt}/{max_retries}] {type(e).__name__} - retrying...')
            _backoff_sleep(attempt)
            continue

        except AuthenticationError as e:
            raise OpenAIRequestFailed(f"Authentication failed: {e}")
        
        except BadRequestError as e:
            raise OpenAIRequestFailed(f"Bad Request: {e}")
        
    raise OpenAIRequestFailed("Streaming request failed after maximum retries")
            
def safe_json_chat(client, messages, model: str = "gpt-4o-mini", max_retries: int =3) -> dict:
    """
    Requests a JSON-only response, parses it inot a dict and return it.
    Retries on retryable errors and json parsing errors
    """
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"}
            )
            raw = response.choices[0].message.content
            return json.loads(raw)
        
        except json.JSONDecodeError:
            print(f"[Attempt {attempt}/{max_retries}] Invalid JSON — retrying...")
            _backoff_sleep(attempt)
            continue

        except (RateLimitError, APIConnectionError, APIError) as e:
            print(f"[Attempt {attempt}/{max_retries}] {type(e).__name__} — retrying...")
            _backoff_sleep(attempt)
            continue

        except AuthenticationError as e:
            raise OpenAIRequestFailed(f"Authentication failed: {e}")

        except BadRequestError as e:
            raise OpenAIRequestFailed(f"Bad request: {e}")

    raise OpenAIRequestFailed("JSON request failed after maximum retries.")