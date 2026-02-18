from openai import OpenAI
from dotenv import load_dotenv
import os
import re

from prompts import SYSTEM_PROMPT, JSON_PLAN_INSTRUCTION
from openai_client import safe_json_chat, safe_stream_chat, OpenAIRequestFailed
from utils import print_plan

def wants_plan(text: str) -> bool:
    t = text.lower()
    keywords = ["midterm", "exam", "test", "quiz", "study plan", "plan", "schedule", "behind"]
    return any(k in t for k in keywords)

def has_days(text: str) -> bool:
    t = text.lower()
    # matches: "6 days", "in 6 days", "6 day"
    return re.search(r"\b\d+\s*day(s)?\b", t) is not None

def main():
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    print("Study planner Bot. Type 'quit' to exit.\n")

    try:
        while True:
            user = input("You: ")
            if user.strip().lower() == 'quit':
                break

            messages.append({"role": "user", 'content': user})

            # Streamed response 
            print("\nAI (coach): ", end="", flush=True)
            coach_reply = safe_stream_chat(client, messages)
            messages.append({'role': 'assistant', "content": coach_reply})


            #Json plan
            if wants_plan(user) and has_days(user):
                json_messages = messages + [
                    {"role": 'user', "content": JSON_PLAN_INSTRUCTION}
                ]
                plan = safe_json_chat(client, json_messages)
                print_plan(plan)

    except KeyboardInterrupt:
        print("\nExiting safely.")
    except OpenAIRequestFailed as e:
        print(f"\nFatal error: {e}")

if __name__ == "__main__":
    main()