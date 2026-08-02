import os
import re
import json
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# --- تنزيل حزم NLTK تلقائياً إن لم تكن موجودة ---
try:
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('wordnet', quiet=True)
except Exception:
    pass

# --- إعداد المسارات ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "processed_docs")
OUTPUT_DIR = os.path.join(BASE_DIR, "cleaned_docs")

# --- إعدادات كود الدكتور للـ Preprocessing (مخصصة للوائح الزراعة والتصدير) ---
lemmatizer = WordNetLemmatizer()
translator = str.maketrans("", "", string.punctuation)

# كلمات النفي المحمية من الحذف لأهميتها القاطعة في القوانين واللوائح
protected_negation_words = {"no", "not", "nor", "never"}

# قاموس الـ Lemmatization الاحتياطي المخصص لمصطلحات الفراولة والـ EU Regulations
fallback_lemma_map = {
    ("strawberries", "n"): "strawberry",
    ("pesticides", "n"): "pesticide",
    ("residues", "n"): "residue",
    ("regulations", "n"): "regulation",
    ("requirements", "n"): "requirement",
    ("standards", "n"): "standard",
    ("inspections", "n"): "inspection",
    ("contaminants", "n"): "contaminant",
    ("limits", "n"): "limit",
    ("exporting", "v"): "export",
    ("exported", "v"): "export",
    ("sampling", "v"): "sample",
    ("sampled", "v"): "sample",
    ("inspecting", "v"): "inspect",
}

try:
    stop_words = set(stopwords.words("english"))
except LookupError:
    stop_words = {"the", "is", "and", "a", "an", "of", "to", "in", "for", "with", "on"}


def ensure_directories():
    """تأكيد وجود مجلد الحفظ cleaned_docs"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


# --- [1]: تنظيف شكل وتنسيق الماركداون ---
def clean_markdown_text(text: str) -> str:
    """تنظيف نصوص الماركداون المخرجة وتنسيقها"""
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [line.rstrip() for line in text.splitlines()]
    text = "\n".join(lines)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    return text.strip()


# --- [2]: دوال المعالجة اللغوية NLP (مطابقة لمفهوم كود الدكتور) ---
def safe_word_tokenize(text: str):
    try:
        return word_tokenize(text)
    except LookupError:
        return re.findall(r"\b\w+\b", text)


def safe_lemmatize(token: str, pos: str = "v"):
    token = token.lower()
    try:
        return lemmatizer.lemmatize(token, pos=pos)
    except LookupError:
        pass

    if (token, pos) in fallback_lemma_map:
        return fallback_lemma_map[(token, pos)]
    if token.endswith("ing") and len(token) > 4:
        base = token[:-3]
        if len(base) >= 2 and base[-1] == base[-2]:
            base = base[:-1]
        return base
    if token.endswith("ed") and len(token) > 3:
        return token[:-2]
    if token.endswith("s") and not token.endswith("ss") and len(token) > 3:
        return token[:-1]
    return token


def preprocess_text(text: str) -> str:
    """الدالة المعالجة لغوياً الشاملة (تنظيف الروابط، إزالة الـ Stopwords، والـ Lemmatization)"""
    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", "", text)
    text = text.translate(translator)
    text = re.sub(r"\s+", " ", text).strip()

    tokens = safe_word_tokenize(text)
    tokens = [
        token for token in tokens
        if token not in stop_words or token in protected_negation_words
    ]
    tokens = [safe_lemmatize(token, pos="v") for token in tokens]
    return " ".join(tokens)


# --- العملية الرئيسية ---
def process_cleaning_and_preprocessing():
    print(f"\n🧹 [02_preprocessing] جاري تنظيف ومعالجة الملفات من: {INPUT_DIR}...\n")
    cleaned_count = 0

    json_input_path = os.path.join(INPUT_DIR, "documents.json")
    
    # تحديث documents.json بالنصوص النظيفة والمجهزة
    if os.path.exists(json_input_path):
        with open(json_input_path, "r", encoding="utf-8") as f:
            documents = json.load(f)

        for doc in documents:
            raw_text = doc.get("text", "")
            cleaned = clean_markdown_text(raw_text)
            preprocessed = preprocess_text(cleaned)

            doc["cleaned_text"] = cleaned
            doc["preprocessed_text"] = preprocessed

            # حفظ نسخة الماركداون المنظفة في مجلد cleaned_docs
            output_file_path = os.path.join(OUTPUT_DIR, f"{doc['id']}.md")
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(cleaned)
            cleaned_count += 1

        # حفظ تحديث الـ JSON الشامل
        with open(json_input_path, "w", encoding="utf-8") as f:
            json.dump(documents, f, ensure_ascii=False, indent=4)

        print(f"✨ تم معالجة وتحديث {cleaned_count} مستند بنجاح!")
        print(f"📁 تم حفظ الملفات المنظفة في: {OUTPUT_DIR}\n")

    else:
        # مسار احتياطي لقراءة ملفات الماركداون مباشرة
        for file_name in os.listdir(INPUT_DIR):
            if file_name.endswith(".md"):
                file_path = os.path.join(INPUT_DIR, file_name)
                output_file_path = os.path.join(OUTPUT_DIR, file_name)

                with open(file_path, "r", encoding="utf-8") as f:
                    raw_content = f.read()

                cleaned_content = clean_markdown_text(raw_content)

                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write(cleaned_content)

                cleaned_count += 1

        print(f"🎉 تم تنظيف {cleaned_count} ملف وحفظهم داخل {OUTPUT_DIR}!")


if __name__ == "__main__":
    ensure_directories()
    process_cleaning_and_preprocessing()  