import os
import json
import importlib
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- إعداد المسارات ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "processed_docs")
OUTPUT_DIR = os.path.join(BASE_DIR, "chunks_output")

# استيراد دالة الـ Preprocessing من الملف الثاني بطريقة آمنة
try:
    prep_module = importlib.import_module("02_preprocessing")
    preprocess_text = getattr(prep_module, "preprocess_text")
except Exception as e:
    print(f"⚠️ تنبيه أثناء استيراد 02_preprocessing: {e}")
    def preprocess_text(text): return text.lower()


def ensure_directories():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def build_chunks():
    print(f"\n✂️ [03_chunking] جاري تقطيع المستندات وتجهيز بيانات الـ Search...\n")

    json_input_path = os.path.join(INPUT_DIR, "documents.json")
    if not os.path.exists(json_input_path):
        print(f"❌ لم يتم العثور على {json_input_path}. يرجى تشغيل الخطوات السابقة أولاً!")
        return []

    with open(json_input_path, "r", encoding="utf-8") as f:
        documents = json.load(f)

    # إعداد الـ Text Splitter الاحترافي
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n## ", "\n# ", "\n\n", "\n", " ", ""],
    )

    rows = []
    all_txt_chunks = []

    for document in documents:
        doc_id = document.get("id", "doc")
        title = document.get("title", doc_id)
        is_current = document.get("is_current", True)
        cleaned_text = document.get("cleaned_text", document.get("text", ""))

        # تقطيع النص
        chunks = text_splitter.split_text(cleaned_text)
        print(f" 📄 {doc_id} -> تم تقسيمه إلى {len(chunks)} Chunk")

        for chunk_number, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_{chunk_number}"

            # الهيكل المطلوب والمطابق لكود الدكتور
            chunk_item = {
                "chunk_id": chunk_id,
                "document_id": doc_id,
                "title": title,
                "is_current": is_current,
                "chunk_text": chunk,
                # سر دقة الدكتور: إضافة العنوان للنص المجهز للبحث
                "search_text": preprocess_text(f"{title} {chunk}")
            }
            rows.append(chunk_item)

            # تجهيز النسخة النصية العادية للعرض
            all_txt_chunks.append(
                f"--- CHUNK {chunk_id} | SOURCE: {doc_id} ---\n{chunk}\n\n"
            )

    # 1. حفظ الهيكلية المنظمة (JSON) لاستخدامها في VectorStore والـ Ground Truth
    json_output_path = os.path.join(OUTPUT_DIR, "chunks.json")
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=4)

    # 2. حفظ النسخة النصية (TXT)
    txt_output_path = os.path.join(OUTPUT_DIR, "all_chunks.txt")
    with open(txt_output_path, "w", encoding="utf-8") as f:
        f.write("".join(all_txt_chunks))

    print(f"\n🎉 تم تقطيع كل المستندات بنجاح إلى {len(rows)} Chunks!")
    print(f"📁 تم حفظ ملف الـ JSON في: {json_output_path}")
    print(f"📁 تم حفظ ملف الـ TXT في: {txt_output_path}\n")

    return rows


if __name__ == "__main__":
    ensure_directories()
    chunks = build_chunks()