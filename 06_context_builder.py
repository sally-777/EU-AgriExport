import importlib
import json
import os

# محاولة استيراد دالة البحث
try:
    vectorstore_module = importlib.import_module("04_vectorstore")
    hybrid_search = getattr(vectorstore_module, "hybrid_search", None)
except Exception as e:
    print(f"⚠️ تنبيه استيراد hybrid_search من 04_vectorstore: {e}")
    hybrid_search = None


def build_context(question: str, k: int = 5, max_words: int = 400):
    """بناء السياق (Context Builder) بتنسيق الدكتور مع التحكم الذكي في ميزانية عدد الكلمات (Word Budget)"""
    retrieved_chunks = []

    # 1️⃣ جلب نتائج البحث
    if hybrid_search:
        try:
            retrieved_chunks = hybrid_search(question, k=k)
        except Exception as e:
            print(f"⚠️ خطأ أثناء البحث الهجين: {e}")

    # Fallback سريع في حالة عدم إرجاع نتائج من البحث الهجين لمنع التعليق
    if not retrieved_chunks:
        chunks_path = os.path.join("chunks_output", "chunks.json")
        if os.path.exists(chunks_path):
            with open(chunks_path, "r", encoding="utf-8") as f:
                all_chunks = json.load(f)
            # أخذ عينة مباشرة سريعة
            retrieved_chunks = all_chunks[:k]

    # 2️⃣ الترتيب بحسب الأحدث (is_current) ثم الأعلى درجة (score)
    retrieved_chunks = sorted(
        retrieved_chunks,
        key=lambda row: (row.get("is_current", True), row.get("score", 0)),
        reverse=True,
    )

    selected_chunks = []
    seen_documents = set()
    used_words = 0

    # 3️⃣ تصفية المستندات ومراعاة ميزانية الكلمات (Word Budget)
    for chunk in retrieved_chunks:
        doc_id = chunk.get("document_id")
        text = chunk.get("chunk_text", chunk.get("text", ""))
        words = len(text.split())

        # تجنب التكرار من نفس المستند
        if doc_id in seen_documents:
            continue

        # التوقف إذا تجاوزنا عدد الكلمات المسموح
        if used_words + words > max_words and len(selected_chunks) > 0:
            break

        seen_documents.add(doc_id)
        selected_chunks.append(chunk)
        used_words += words

    # 4️⃣ صياغة النص النهائي بتنسيق المصادر المنظم للدكتور
    context_blocks = []
    for source_number, chunk in enumerate(selected_chunks, start=1):
        status = "CURRENT" if chunk.get("is_current", True) else "OUTDATED"
        title = chunk.get("title", chunk.get("document_id", "Document"))
        chunk_text = chunk.get("chunk_text", chunk.get("text", ""))

        block = f"[Source {source_number}] {title} ({status})\n{chunk_text}"
        context_blocks.append(block)

    context_str = "\n\n--- SOURCE BLOCK ---\n\n".join(context_blocks)

    return {
        "context_text": context_str,
        "used_words": used_words,
        "num_sources": len(selected_chunks),
        "selected_chunks": selected_chunks,
    }


if __name__ == "__main__":
    test_question = (
        "What is the MRL limit for pesticides in strawberry exports?"
    )
    print(
        f"\n📦 [07_context_builder] تجربة بناء السياق للسؤال:"
        f" '{test_question}'\n"
    )

    result = build_context(test_question)

    print("--- Context Text الناتج ---")
    print(result["context_text"])
    print("\n---------------------------")
    print(f"📊 عدد الكلمات المستقلة: {result['used_words']}")
    print(f"📚 عدد المصادر المختارة: {result['num_sources']}")