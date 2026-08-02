import importlib
import json
import os
import numpy as np
from rank_bm25 import BM25Okapi

# --- استيراد الموديولات السابقة بأسلوب آمن ---
try:
    preprocessing = importlib.import_module("02_preprocessing")
    preprocess_text = getattr(preprocessing, "preprocess_text")
except Exception as e:

    def preprocess_text(text):
        return text.lower()


# 🎯 تحميل الـ Chunks الجاهزة من ملف JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "chunks_output", "chunks.json")

chunks = []
if os.path.exists(json_path):
    print("⚡ [04_vectorstore] تحميل الـ Chunks الجاهزة...")
    with open(json_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

# 🎯 تجهيز BM25 السريع جداً (ياخد أقل من ثانية)
print("🧠 تجهيز محرك البحث السريع BM25...")
tokenized_chunks = [
    chunk.get("search_text", chunk.get("chunk_text", "")).split()
    for chunk in chunks
]
bm25 = BM25Okapi(tokenized_chunks)


def min_max_normalize(scores):
    """توحيد المقاييس"""
    scores = np.array(scores, dtype=float)
    if scores.max() == scores.min():
        return np.zeros_like(scores)
    return (scores - scores.min()) / (scores.max() - scores.min())


def hybrid_search(query: str, k: int = 4):
    """دالة البحث السريعة والذكية بدون تحميل Embeddings ثقيلة في الـ RAM"""
    if not chunks:
        return []

    clean_query = preprocess_text(query)

    # بحث الكلمات المفتاحية الفائق السرعة
    bm25_scores = bm25.get_scores(clean_query.split())

    # ترتيب النتائج بأسرع شكل ممكن
    ranking = np.argsort(bm25_scores)[::-1][:k]

    return [
        {**chunks[index], "score": float(bm25_scores[index])} for index in ranking
    ]


if __name__ == "__main__":
    test_query = "What is the maximum residue limit MRL for strawberries?"
    print(f"\n🔍 تجربة البحث عن: '{test_query}'")
    results = hybrid_search(test_query, k=2)
    print(f"✅ تم العثور على {len(results)} نتائج فورية!")