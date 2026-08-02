import pandas as pd

# 1. تحديد الأسئلة والـ Ground Truth مع ربطها بأسماء ملفات مشروعك الحقيقية
ground_truth_data = [
    {
        "query_id": "Q1",
        "query": "What are the plant health requirements for exporting strawberries?",
        "relevant_doc_ids": [
            "01_Plant_Health_Law_Regulation_2016_2031",
            "04_Official_Controls_Regulation_2017_625"
        ],
        "expected_answer": "Plant health requirements include a phytosanitary certificate and inspection for quarantine pests."
    },
    {
        "query_id": "Q2",
        "query": "What are the pesticide MRL limits for agricultural exports?",
        "relevant_doc_ids": [
            "05_Pesticide_MRL_Regulation_396_2005",
            "09_Strawberry_MRL_Database_excel"
        ],
        "expected_answer": "Maximum Residue Limits (MRLs) must not exceed EU safety thresholds."
    },
    {
        "query_id": "Q3",
        "query": "How are official controls performed on food products?",
        "relevant_doc_ids": [
            "04_Official_Controls_Regulation_2017_625"
        ],
        "expected_answer": "Official controls are performed regularly based on risk assessment without prior warning."
    }
]


def load_ground_truth():
    df = pd.DataFrame(ground_truth_data)
    print(f"✅ Loaded Ground Truth dataset with {len(df)} evaluation queries.\n")
    return df


if __name__ == "__main__":
    gt_df = load_ground_truth()
    print(gt_df[["query_id", "query", "relevant_doc_ids"]])