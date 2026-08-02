"""
Prompt Management Module for EU Agricultural Export RAG System
Handles system roles, strict guardrails, and context-augmented queries.
"""

# 1. System Role Definition
SYSTEM_ROLE_EXPERT = (
    "You are an expert legal and technical consultant specializing in European Union (EU) "
    "agricultural export regulations, phytosanitary requirements, and Pesticide Maximum Residue Limits (MRLs). "
    "Your responses must be precise, professional, directly answering the query, and strictly bound to the retrieved context."
)


# 2. Main RAG Prompt with Strict Guardrails
def get_rag_main_prompt(user_query: str, context_text: str) -> str:
    """Generates the primary RAG prompt equipped with hallucination filters and strict guardrails."""
    return f"""
{SYSTEM_ROLE_EXPERT}

User Query: {user_query}

Task Instructions:
1. Provide a direct, structured, and well-organized response in Modern Standard Arabic (العربية الفصحى).
2. Explicitly specify active ingredients (Pesticide Active Ingredients), Maximum Residue Limits (MRL in mg/kg), and phytosanitary quarantine rules if present in the text.
3. Cite your sources directly if available (e.g., [Source 1], [Source 2]).

🚨 STRICT GUARDRAILS & HALLUCINATION FILTERS:
- Rely ONLY and EXCLUSIVELY on the provided "Reference Context" below.
- Do NOT use external knowledge, guess, or extrapolate beyond the explicit facts in the reference text.
- Prefer CURRENT sources over OUTDATED sources.
- If the requested active ingredient, pesticide limit, or regulation is NOT explicitly mentioned in the context, your response MUST be strictly:
  "⚠️ عفواً، هذه المادة أو الشرط المطلوب غير مدرج في اللوائح وقواعد البيانات المتاحة حالياً بالمنصة."

Reference Context:
{context_text}
"""


# 3. دالة التوافق مع أسلوب الدكتور (Build Prompt Wrapper)
def build_prompt(question: str, context: str) -> str:
    """دالة توافقية تستدعي الـ Main RAG Prompt الصارم لتشغيل كود الدكتور بسلاسة"""
    return get_rag_main_prompt(user_query=question, context_text=context)


# 4. Dedicated Prompt for Export Checklist/Report Summary
def get_export_report_prompt(crop_name: str, context_text: str) -> str:
    """Generates a specialized prompt for summarizing comprehensive export compliance checklists for a given crop."""
    return f"""
{SYSTEM_ROLE_EXPERT}

Task: Generate a comprehensive, technical EU Agricultural Export Summary Report for the target crop: ({crop_name}).

Instructions:
- Write the final output report in Modern Standard Arabic (العربية الفصحى) using professional bullet points.
- Based ONLY on the provided reference context, summarize:
  1. Phytosanitary & Inspection Requirements (اشتراطات الصحة النباتية والفحص الحجري).
  2. Pesticide Maximum Residue Limits (MRLs) & Chemical Safety Thresholds (حدود متبقيات المبيدات).

Reference Context:
{context_text}
"""


# 5. Quick Pesticide Search Prompt (MRL Checker Widget)
def get_mrl_checker_prompt(pesticide_name: str, context_text: str) -> str:
    """Generates a structured prompt for instant pesticide MRL extraction."""
    return f"""
{SYSTEM_ROLE_EXPERT}

Task: Extract the exact MRL value and regulations for the chemical compound: ({pesticide_name}).

Instructions:
- Return the output in Arabic formatted as a quick reference summary.
- Specify the Active Ingredient Name, MRL value (mg/kg), and target crop/market if stated in the text.
- If ({pesticide_name}) is not mentioned in the reference context, state clearly that it is not available in the database.

Reference Context:
{context_text}
"""