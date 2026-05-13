import os
import json
import logging
import time
import re
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
    logging.info("Sending request directly to your model pool with reasoning support...")

    url = "https://" + "openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "HTTP-Referer": "https://localhost:3000",
        "X-Title": "Local Text Processor Script"
    }

    # Пул ваших моделей, запрашиваемый поочередно локально
    models_pool = [
        "z-ai/glm-4.5-air:free",
        "openai/gpt-oss-120b:free",
        "baidu/qianfan-cobuddy:free"
    ]

    response = None
    successful_model = None

    for model in models_pool:
        logging.info(f"Trying model: {model}...")
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": user_prompt}],
            # ГАРАНТИРУЕМ ВКЛЮЧЕНИЕ МЫШЛЕНИЯ НА УРОВНЕ API ДЛЯ СНЯТИЯ ОШИБКИ 400
            "include_reasoning": True
        }

        try:
            res = requests.post(url, headers=headers, json=payload, timeout=60)

            if res.status_code == 200:
                response = res
                successful_model = model
                logging.info(f"🟢 Success with model: {model}")
                break
            else:
                logging.warning(f"🔴 Model {model} failed (Status {res.status_code}). Response: {res.text}")

        except requests.exceptions.RequestException as e:
            logging.warning(f"⚠️ Network issue with model {model}: {e}")

    # === ОБРАБОТКА И ЗАПИСЬ ОТВЕТА ===
    if response and response.status_code == 200:
        try:
            response_data = response.json()
            ai_response = response_data['choices'][0]['message']['content']

            # Автоматически полностью вырезаем блок рассуждений <think>...</think>
            clean_response = re.sub(r'<think>.*?</think>', '', ai_response, flags=re.DOTALL).strip()

            usage = response_data.get('usage', {})
            total_tokens = usage.get('total_tokens', 0)

            api_metadata = {
                "timestamp": datetime.now().isoformat(),
                "actual_responding_model": successful_model,
                "reasoning_filtered": True,
                "usage": {
                    "prompt_tokens": usage.get('prompt_tokens', 0),
                    "completion_tokens": usage.get('completion_tokens', 0),
                    "total_tokens": total_tokens
                }
            }

            logging.info(f"API METADATA: {json.dumps(api_metadata, ensure_ascii=False)}")

            # Записываем исключительно чистый текст
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(clean_response)

            logging.info(f"Success! Clean response saved to {output_file}.")
            logging.info(f"Final execution model: {successful_model} | Tokens: {total_tokens}")

        except Exception as e:
            logging.error(f"Error parsing response: {e}", exc_info=True)
    else:
        logging.error("❌ Critical failure: All premium free models returned errors or were unavailable.")


if __name__ == "__main__":
    process_text_via_ai()
