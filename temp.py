import os
import json
import logging
import time
from datetime import datetime
import requests

# 1. Настройка логирования в файл и консоль
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("api_session.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

s = "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"
api_key = s


def process_text_via_ai():
    input_file = "temp.txt"
    output_file = "temp1.txt"

    if not os.path.exists(input_file):
        logging.error(f"File '{input_file}' not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        user_prompt = f.read().strip()

    if not user_prompt:
        logging.warning("File is empty. Request canceled.")
        return

    logging.info(f"Text read from {input_file} (Length: {len(user_prompt)} chars.)")

    # ГАРАНТИРОВАННОЕ НАЛИЧИЕ HTTPS ПРОТОКОЛА
    url = "https://" + "openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "HTTP-Referer": "https://localhost:3000",
        "X-Title": "Local Text Processor Script"
    }

    payload = {
        "model": "z-ai/glm-4.5-air:free",
        "messages": [{"role": "user", "content": user_prompt}]
    }

    max_retries = 3
    retry_delay = 4
    response = None

    for attempt in range(1, max_retries + 1):
        logging.info(f"Attempt {attempt} of {max_retries}: Sending request to GLM 4.5 Air...")
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=60)

            if res.status_code == 200:
                response = res
                break
            elif res.status_code in [429, 503]:
                logging.warning(f"GLM 4.5 Air is busy (Status {res.status_code}). Waiting {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                logging.error(f"API critical error (Status Code {res.status_code}): {res.text}")
                return

        except requests.exceptions.RequestException as e:
            logging.warning(f"Network issue on attempt {attempt}: {e}")
            time.sleep(retry_delay)
            retry_delay *= 2

    # === ОБРАБОТКА И ЗАПИСЬ ОТВЕТА ===
    if response and response.status_code == 200:
        try:
            response_data = response.json()
            ai_response = response_data['choices'][0]['message']['content']

            usage = response_data.get('usage', {})
            total_tokens = usage.get('total_tokens', 0)

            api_metadata = {
                "timestamp": datetime.now().isoformat(),
                "model": payload["model"],
                "usage": {
                    "prompt_tokens": usage.get('prompt_tokens', 0),
                    "completion_tokens": usage.get('completion_tokens', 0),
                    "total_tokens": total_tokens
                }
            }

            logging.info(f"API METADATA: {json.dumps(api_metadata, ensure_ascii=False)}")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(ai_response)

            logging.info(f"Success! Response saved to {output_file}.")
            logging.info(f"Tokens consumed: {total_tokens}")

        except Exception as e:
            logging.error(f"Error parsing response: {e}", exc_info=True)
    else:
        logging.error("Critical failure: GLM 4.5 Air was unavailable after all retries.")


if __name__ == "__main__":
    process_text_via_ai()
