"""
Error Analysis & Failure Layer Diagnosis Module
يقوم بتحليل أسباب فشل الإجابة وتحديد الطبقة المتسببة في الخطأ
"""

def diagnose_failure_layer(has_retrieved_correct_chunk: bool, is_in_context: bool, is_prompt_followed: bool, is_answer_correct: bool = True) -> str:
    """
    تشخيص طبقة الفشل في منظومة الـ RAG:
    - Layer 1: failure in Retrieval / Embeddings
    - Layer 2: failure in Context Building / Word Budget
    - Layer 3: failure in Prompt Following / Guardrails
    - Layer 4: LLM Generation / Hallucination
    """
    if not has_retrieved_correct_chunk:
        return "❌ Layer 1 Failure: Retrieval / Embeddings Failure (Correct chunk missing)"
    
    elif not is_in_context:
        return "❌ Layer 2 Failure: Context Building Failure (Chunk filtered out or word budget exceeded)"
    
    elif not is_prompt_followed:
        return "❌ Layer 3 Failure: Prompt Engineering Failure (LLM ignored rules)"
    
    elif not is_answer_correct:
        return "❌ Layer 4 Failure: LLM Generation / Hallucination Failure"
    
    else:
        return "✅ SUCCESS: All layers executed perfectly!"


if __name__ == "__main__":
    print("🔍 [09_error_analysis] Failure Analysis framework ready.")
    
    # تجربة سريعة للتشخيص
    sample_diag = diagnose_failure_layer(
        has_retrieved_correct_chunk=True, 
        is_in_context=True, 
        is_prompt_followed=True, 
        is_answer_correct=True
    )
    print(f"نتيجة الاختبار: {sample_diag}")