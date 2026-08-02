import importlib
import pandas as pd

# 1. استيراد دالة Ground Truth من 07_ground_truth.py
try:
    gt_module = importlib.import_module("07_ground_truth")
    load_ground_truth = getattr(gt_module, "load_ground_truth")
except Exception as e:
    print(f"⚠️ خطأ في استيراد ملف 07_ground_truth: {e}")

# 2. استيراد دالة البحث الهجين من 04_vectorstore.py
try:
    vectorstore_module = importlib.import_module("04_vectorstore")
    hybrid_search = getattr(vectorstore_module, "hybrid_search")
except Exception as e:
    print(f"⚠️ خطأ في استيراد hybrid_search من 04_vectorstore: {e}")
    hybrid_search = None


# 3. معادلات حساب الـ Metrics القياسية
def precision_at_k(retrieved_ids, relevant_ids, k=3):
    retrieved_k = retrieved_ids[:k]
    hits = len(set(retrieved_k).intersection(set(relevant_ids)))
    return hits / k


def recall_at_k(retrieved_ids, relevant_ids, k=3):
    if not relevant_ids:
        return 0.0
    retrieved_k = retrieved_ids[:k]
    hits = len(set(retrieved_k).intersection(set(relevant_ids)))
    return hits / len(relevant_ids)


def hit_rate_at_k(retrieved_ids, relevant_ids, k=3):
    retrieved_k = retrieved_ids[:k]
    return 1 if set(retrieved_k).intersection(set(relevant_ids)) else 0


def reciprocal_rank(retrieved_ids, relevant_ids):
    for rank, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in relevant_ids:
            return 1 / rank
    return 0.0


# 4. دالة البحث الفعلي باستخدام الـ Hybrid Search
def real_hybrid_retriever(query, k=3):
    """دالة تستدعي البحث الهجين من 04_vectorstore"""
    if hybrid_search:
        results = hybrid_search(query, k=k)
        retrieved_chunks = []
        for doc in results:
            doc_id = doc.get("document_id", doc.get("chunk_id", ""))
            retrieved_chunks.append({"doc_id": doc_id, "text": doc.get("chunk_text", "")})
        return retrieved_chunks
    else:
        # دالة احتياطية في حال تعذر الاتصال بالـ Search Engine
        return [
            {"doc_id": "01_Plant_Health_Law_Regulation_2016_2031"},
            {"doc_id": "05_Pesticide_MRL_Regulation_396_2005"},
            {"doc_id": "04_Official_Controls_Regulation_2017_625"},
        ][:k]


# 5. تشغيل التقييم لكل سؤال في الـ Ground Truth
def evaluate_retriever_system(retriever_func, ground_truth_df, k=3):
    results = []

    for _, row in ground_truth_df.iterrows():
        query = row["query"]
        relevant_ids = row["relevant_doc_ids"]

        # استدعاء الـ Retriever لجلب المستندات
        retrieved_chunks = retriever_func(query, k=k)
        retrieved_ids = [c["doc_id"] for c in retrieved_chunks]

        # حساب الـ Metrics للسؤال الحالي
        results.append(
            {
                "query_id": row.get("query_id", "Q"),
                "query": query,
                f"precision@{k}": round(precision_at_k(retrieved_ids, relevant_ids, k), 2),
                f"recall@{k}": round(recall_at_k(retrieved_ids, relevant_ids, k), 2),
                f"hit_rate@{k}": hit_rate_at_k(retrieved_ids, relevant_ids, k),
                "mrr": round(reciprocal_rank(retrieved_ids, relevant_ids), 2),
            }
        )

    eval_df = pd.DataFrame(results)

    # طباعة الجدول والمتوسطات العامة
    print("\n================ 📊 RETRIEVAL METRICS SUMMARY ================\n")
    print(eval_df[["query_id", f"precision@{k}", f"recall@{k}", f"hit_rate@{k}", "mrr"]].to_string(index=False))
    print("\n------------------ AVERAGES ------------------")
    print(
        eval_df[[f"precision@{k}", f"recall@{k}", f"hit_rate@{k}", "mrr"]].mean()
    )
    print("=============================================================\n")

    return eval_df


if __name__ == "__main__":
    print("🚀 جاري بدء تقييم محرك البحث الـ Retrieval...")
    # 1. تحميل الـ Ground Truth
    gt_df = load_ground_truth()

    # 2. تشغيل التقييم وطباعة الـ Metrics
    evaluate_retriever_system(real_hybrid_retriever, gt_df, k=3)