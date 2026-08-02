import importlib
import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
from prompts import build_prompt

load_dotenv()

try:
    context_module = importlib.import_module("06_context_builder")
    build_context = getattr(context_module, "build_context")
except Exception as e:
    print(f"⚠️ تنبيه أثناء استيراد 06_context_builder: {e}")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# موديلات احتياطية أخيرة لو تعذر الاتصال بقائمة OpenRouter الحية
STATIC_FALLBACK_MODELS = [
    "meta-llama/llama-3.2-3b-instruct:free",
    "google/gemma-3-4b-it:free",
    "mistralai/mistral-7b-instruct:free",
]


def get_live_free_models() -> list:
    """جلب قائمة الموديلات المجانية الفعلية من OpenRouter لحظياً (بتتغير باستمرار)"""
    try:
        resp = requests.get("https://openrouter.ai/api/v1/models", timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [])

        free_models = []
        for model in data:
            pricing = model.get("pricing", {})
            prompt_price = pricing.get("prompt", "1")
            completion_price = pricing.get("completion", "1")
            model_id = model.get("id", "")
            if prompt_price == "0" and completion_price == "0" and model_id.endswith(":free"):
                free_models.append(model_id)

        # تفضيل موديلات معروفة الجودة لو موجودة في القائمة الحية
        preferred_keywords = ["llama-3.1-8b", "llama-3.2", "gemma", "qwen", "mistral"]
        free_models.sort(
            key=lambda m: any(k in m for k in preferred_keywords), reverse=True
        )
        return free_models[:8] if free_models else STATIC_FALLBACK_MODELS
    except Exception as e:
        print(f"⚠️ تعذر جلب قائمة الموديلات الحية: {e}")
        return STATIC_FALLBACK_MODELS


def ask_openrouter(prompt: str) -> str:
    """استدعاء الموديل عبر OpenRouter مع تجربة الموديلات المجانية المتاحة فعلياً"""
    if not OPENROUTER_API_KEY:
        return "⚠️ خطأ: لم يتم العثور على OPENROUTER_API_KEY في ملف .env"

    api_key = OPENROUTER_API_KEY.strip().strip('"')
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    models_to_try = get_live_free_models()
    last_error = None

    for model_name in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            print(f"✅ نجح الاتصال بالموديل: {model_name}")
            return response.choices[0].message.content
        except Exception as e:
            last_error = e
            print(f"⚠️ فشل الموديل {model_name}: {e}")
            continue

    return f"❌ خطأ أثناء الاتصال بكل الموديلات المتاحة: {last_error}"


ask_llm = ask_openrouter


def answer_question(question: str):
    context_data = build_context(question)

    if isinstance(context_data, dict):
        context = context_data.get("context_text", "")
        sources = context_data.get("selected_chunks", [])
    else:
        context, sources = context_data

    prompt = build_prompt(question, context)
    answer = ask_openrouter(prompt)
    return answer, sources


if __name__ == "__main__":
    test_q = (
        "ما هي الحدود المسموحة للمبيدات (MRL) في الفراولة المصدرة للاتحاد"
        " الأوروبي؟"
    )
    print(f"\n❓ السؤال: {test_q}\n")
    print("🤖 جاري توليد الإجابة...\n")
    ans, src = answer_question(test_q)
    print("--- 📝 الإجابة النهائية ---")
    print(ans)