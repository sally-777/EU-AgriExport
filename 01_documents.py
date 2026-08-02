import os
import json

# --- 1. إعداد مسارات المجلدات ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "processed_docs")


def ensure_directories():
    """تأكيد وجود مجلد processed_docs"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_documents_as_structured_data():
    """
    قراءة الملفات الـ 9 المجهزة سابقاً في processed_docs
    وتحويلها إلى هيكل بيانات منظم (List of Dicts) مطابق لمواصفات الدكتور.
    """
    print(f"\n📦 جاري قراءة الملفات التسعة المجهزة وتنسيقها...")
    documents = []

    if not os.path.exists(OUTPUT_DIR):
        print(f"❌ المجلد {OUTPUT_DIR} غير موجود!")
        return documents

    # قراءة كل ملفات الـ md التسعة المعلم عليها بالأصفر
    for file_name in sorted(os.listdir(OUTPUT_DIR)):
        if file_name.endswith(".md"):
            file_path = os.path.join(OUTPUT_DIR, file_name)
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            doc_id = os.path.splitext(file_name)[0]
            clean_title = doc_id.replace("_", " ").title()

            # القاموس هنا يطابق المطلوب من الدكتور تماماً
            doc_item = {
                "id": doc_id,
                "title": clean_title,
                "is_current": True,  # مطابقة لهيكل الدكتور
                "text": content,
                "file_name": file_name
            }
            documents.append(doc_item)

    # حفظ مخرجات القائمة في ملف JSON لتسهيل استدعائه في الملفات التالية
    json_path = os.path.join(OUTPUT_DIR, "documents.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=4)

    print(f"✨ تم العثور على {len(documents)} ملفات وتنسيقها بنجاح!")
    print(f"📁 تم حفظ الهيكلية في: {json_path}\n")
    return documents


if __name__ == "__main__":
    ensure_directories()
    # تشغيل التحويل المباشر دون معالجة أو تعديل للـ PDFs
    docs = load_documents_as_structured_data()