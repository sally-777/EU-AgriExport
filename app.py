import importlib
import os
import streamlit as st

# =========================================================
# ⚙️ 1. إعدادات الصفحة والـ Custom CSS
# =========================================================
st.set_page_config(
    page_title="EU AgriExport AI | منصة تصدير الحاصلات الزراعية",
    page_icon="🍓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .hero-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155; border-radius: 16px;
        padding: 2rem; text-align: center; margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .hero-title { color: #38bdf8; font-size: 2.2rem; font-weight: 800; margin-bottom: 0.5rem; }
    .hero-subtitle { color: #94a3b8; font-size: 1.1rem; }
    .answer-card {
        background: #1e293b; border-right: 5px solid #10b981;
        border-radius: 12px; padding: 1.5rem; margin-top: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        line-height: 1.8; direction: rtl; text-align: right;
    }
    .stButton > button {
        background-color: #0284c7 !important; color: #ffffff !important;
        font-weight: bold !important; border-radius: 8px !important;
        border: none !important; padding: 0.6rem 1rem !important;
    }
    .stButton > button:hover { background-color: #0369a1 !important; }
    </style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# 🧠 2. تحميل المحركات والـ Modules
# =========================================================
@st.cache_resource(show_spinner="⚡ جاري تحميل محرك البحث والـ LLM...")
def get_backend_engine():
    context_builder = importlib.import_module("06_context_builder")
    llm_gen = importlib.import_module("08_llm_generation")
    prompts = importlib.import_module("prompts")
    return {
        "build_context": getattr(context_builder, "build_context"),
        "ask_openrouter": getattr(llm_gen, "ask_openrouter"),
        "prompts": prompts
    }

# =========================================================
# 🎛️ 3. القائمة الجانبية (Sidebar)
# =========================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/590/590685.png", width=70)
    st.title("لوحة التحكم")
    st.markdown("---")
    st.subheader("🌾 المحصول الحالي:")
    st.success("🍓 الفراولة (European Union Market)")
    st.subheader("⚙️ إعدادات المحرك:")
    top_k = st.slider("عدد المستندات المرجعية (Top K):", min_value=1, max_value=8, value=4)
    st.markdown("---")
    st.markdown("#### 💡 أسئلة سريعة مقترحة:")
    if st.button("حدود مبيد Fludioxonil"):
        st.session_state.preset_query = "ما هو الحد الأقصى المسموح به MRL لمبيد Fludioxonil في الفراولة؟"
    if st.button("اشتراطات شهادة الصحة النباتية"):
        st.session_state.preset_query = "ما هي شروط الفحص الحجري وشهادة الصحة النباتية بالتفصيل؟"

# =========================================================
# 🏛️ 4. الهيكل الرئيسي والـ Tabs
# =========================================================
st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">🍓 EU AgriExport RAG System</div>
        <div class="hero-subtitle">المنصة الذكية لمطابقة لوائح تصدير الحاصلات الزراعية للاتحاد الأوروبي</div>
    </div>
""",
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["💬 المساعد الذكي (RAG Chat)", "🔬 الفحص السريع للمبيدات (MRL Checker)"])

# ---------------------------------------------------------
# TAB 1: نظام RAG الرئيسي
# ---------------------------------------------------------
with tab1:
    st.subheader("💬 اسأل المساعد الذكي عن لوائح وشروط التصدير")
    default_query = st.session_state.get("preset_query", "")

    with st.form(key="rag_search_form"):
        user_query = st.text_input(
            "ادخل سؤالك هنا:",
            value=default_query,
            placeholder="مثال: ما هي شروط استيراد الفراولة في المانيا؟",
        )
        submit_search = st.form_submit_button("استعلام وإجابة 🚀")

    if submit_search:
        if not user_query.strip():
            st.warning("⚠️ يرجى كتابة السؤال أولاً.")
        else:
            with st.spinner("جاري استخراج البيانات وتحليل اللوائح... ⏳"):
                try:
                    engine = get_backend_engine()
                    context_data = engine["build_context"](user_query)
                    
                    if isinstance(context_data, tuple):
                        context_text, sources = context_data
                    else:
                        context_text = context_data.get("context_text", "")
                        sources = context_data.get("selected_chunks", [])

                    prompt = engine["prompts"].get_rag_main_prompt(
                        user_query=user_query, context_text=context_text
                    )
                    
                    # استدعاء الـ LLM
                    final_answer = engine["ask_openrouter"](prompt)

                    st.markdown("### 📜 الإجابة المعتمدة:")
                    st.markdown(f'<div class="answer-card">{final_answer}</div>', unsafe_allow_html=True)

                    st.write("")
                    # تحميل النص كتقرير TXT آمن ليدعم اللغة العربية بنسبة 100% بدون أخطاء ترميز
                    st.download_button(
                        label="📥 تحميل تقرير التصدير الفني (TXT File)",
                        data=final_answer.encode("utf-8"),
                        file_name="EU_Export_Technical_Report.txt",
                        mime="text/plain; charset=utf-8",
                    )

                    with st.expander("📚 عرض اللوائح والمصادر المرجعية المستخرجة"):
                        for idx, chunk in enumerate(sources, 1):
                            doc_id = chunk.get("document_id", chunk.get("chunk_id", f"مصدر {idx}"))
                            text = chunk.get("chunk_text", chunk.get("text", ""))
                            st.info(f"**مصدر [{idx}]: {doc_id}**\n\n{text}")
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء المعالجة: {e}")

# ---------------------------------------------------------
# TAB 2: MRL Checker
# ---------------------------------------------------------
with tab2:
    st.subheader("⚡ أداة الفحص اللحظي لمتبقيات المبيدات (MRL Checker)")
    with st.form(key="mrl_checker_form"):
        pesticide_input = st.text_input(
            "اسم المبيد / المادة الفعالة (باللغة الإنجليزية):",
            placeholder="مثال: Boscalid, Cyprodinil, Fludioxonil",
        )
        check_pesticide = st.form_submit_button("فحص المادة الفعالة 🔍")

    if check_pesticide:
        if not pesticide_input.strip():
            st.warning("⚠️ يرجى كتابة اسم المبيد أولاً.")
        else:
            with st.spinner(f"جاري فحص المبيد {pesticide_input}... ⚡"):
                try:
                    engine = get_backend_engine()
                    search_term = f"Strawberry Pesticide MRL Entry Active Ingredient: {pesticide_input}"
                    context_data = engine["build_context"](search_term)
                    
                    if isinstance(context_data, tuple):
                        context_text, _ = context_data
                    else:
                        context_text = context_data.get("context_text", "")

                    mrl_prompt = engine["prompts"].get_mrl_checker_prompt(
                        pesticide_name=pesticide_input, context_text=context_text
                    )
                    mrl_result = engine["ask_openrouter"](mrl_prompt)

                    st.success(f"📊 نتائج الفحص المعتمدة للمادة الفعالة: **{pesticide_input}**")
                    st.markdown(f'<div class="answer-card">{mrl_result}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ حدث خطأ: {e}")

st.divider()
st.caption("✨ EU AgriExport RAG Engine — All rights reserved.")