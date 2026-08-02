# 🍓 EU AgriExport RAG System

منصة ذكية تعتمد على تقنية **RAG (Retrieval-Augmented Generation)** لمساعدة شركات ومزارع تصدير الحاصلات الزراعية على معرفة اشتراطات ولوائح الاتحاد الأوروبي بدقة وسرعة، بالاعتماد الحصري على مصادر قانونية موثقة بدلاً من البحث اليدوي في عدة مستندات ومصادر متفرقة.

**نطاق النسخة الحالية:** الفراولة (Strawberries) المُصدَّرة لدول الاتحاد الأوروبي، مع إمكانية التوسع لمحاصيل أخرى لاحقاً.

---

## 🎯 فكرة المشروع

بدل ما يدور المستخدم (شركة التصدير أو المزارع) في عدة قوانين ولوائح متفرقة عشان يعرف اشتراط معين، بيسأل النظام سؤاله بشكل طبيعي، والنظام:
1. يفتش في تسع مستندات رسمية معتمدة (لوائح EU الخاصة بالصحة النباتية، حدود المبيدات MRL، الرقابة الرسمية، ...إلخ).
2. يستخرج الأجزاء الأكثر صلة بالسؤال.
3. يولّد إجابة دقيقة مبنية **فقط** على النصوص المسترجعة (بدون تخمين)، مع ذكر المصدر.
4. لو المعلومة غير موجودة في المصادر، يصرّح بذلك بدل اختلاق إجابة.

---

## 🏗️ الهيكل العام (Pipeline)

```
01_documents.py          → تحويل المستندات التسعة إلى هيكل بيانات موحد (JSON)
02_preprocessing.py      → تنظيف النصوص + معالجة لغوية (Lemmatization / Stopwords)
03_chunking.py           → تقطيع المستندات إلى Chunks (chunk_size=1000, overlap=150)
04_vectorstore.py        → محرك بحث BM25 (Keyword Search)
05_create_chroma_store.py→ بناء قاعدة بيانات Vector (Semantic Search) عبر Chroma + sentence-transformers
06_context_builder.py    → بناء السياق النهائي (Context) بحد أقصى 400 كلمة
07_ground_truth.py       → بيانات تقييم (أسئلة + إجابات مرجعية على مستوى المستند)
08_llm_generation.py     → استدعاء الـ LLM عبر OpenRouter (مع Fallback ديناميكي بين الموديلات المجانية)
09_error_analysis.py     → تشخيص طبقة الفشل (Retrieval / Context / Prompt / Generation)
010_retrieval_eval.py    → حساب مقاييس الأداء (Precision@k, Recall@k, MRR, Hit Rate)
prompts.py                → إدارة البرومبتات + الحواجز الأمنية ضد الـ Hallucination
app.py                    → واجهة Streamlit التفاعلية
```

---

## ⚙️ خطوات التشغيل

### 1. تجهيز البيئة
```bash
python -m venv venv
venv\Scripts\activate        # على ويندوز
pip install -r requirements.txt
```

### 2. إعداد مفاتيح الـ API
انسخي `.env.example` باسم `.env` وحطي مفتاحك الفعلي من [OpenRouter](https://openrouter.ai/keys):
```
OPENROUTER_API_KEY="مفتاحك هنا"
```
⚠️ **لا ترفعي ملف `.env` أبداً على GitHub** — موجود بالفعل في `.gitignore`.

### 3. تشغيل الـ Pipeline بالترتيب (أول مرة فقط أو بعد إضافة مستندات جديدة)
```bash
python 01_documents.py
python 02_preprocessing.py
python 03_chunking.py
python 05_create_chroma_store.py    # اختياري - لو محتاجة Semantic Search
```

### 4. تشغيل الموقع
```bash
streamlit run app.py
```

### 5. (اختياري) تقييم دقة النظام
```bash
python 010_retrieval_eval.py
```

---

## 🧠 أهم القرارات التصميمية

| القرار | السبب |
|---|---|
| `chunk_size=1000` / `overlap=150` | موازنة بين تماسك السياق (فقرة/مادة قانونية كاملة) وحجم مناسب لحدود الموديل |
| BM25 كمحرك بحث أساسي | دقة عالية مع المصطلحات القانونية المحددة (أسماء مبيدات، أرقام لوائح)، سريع وخفيف |
| `max_words=400` في Context Builder | تحكم في حجم السياق المرسل للموديل + منع تكرار نفس المستند لضمان تنوع المصادر |
| أولوية `is_current` قبل الـ score | تفضيل اللوائح السارية على القديمة حتى لو الأخيرة أعلى في درجة التطابق |
| Ground Truth على مستوى المستند | مناسب لحجم المصادر الحالي (9 مستندات)، متسق مع طريقة الحساب في `010_retrieval_eval.py` |
| Fallback ديناميكي بين الموديلات | الموديلات المجانية على OpenRouter بتتغير باستمرار، فالنظام بيجيب القائمة الحية لحظة كل طلب |
| `temperature=0.1` | تقليل العشوائية والـ Hallucination في دومين قانوني/تنظيمي حساس |

---

## 🚧 نقاط تحتاج تطوير مستقبلي

- **دمج Hybrid Search حقيقي:** حالياً BM25 و Semantic Search (Chroma) شغالين منفصلين. الخطوة القادمة دمج الاثنين بـ Score موحد (Min-Max Normalization) للحصول على أفضل نتائج من الاثنين.
- **معالجة الأرقام والوحدات:** خطوة الـ Preprocessing الحالية بتشيل النقطة العشرية من الأرقام (زي `0.02` → `002`) في نسخة البحث فقط، وده محتاج معالجة خاصة للحفاظ على دقة القيم الرقمية في البحث.
- **Ground Truth على مستوى الـ Chunk:** للحصول على تقييم أدق لجودة الاسترجاع بدل التقييم على مستوى المستند بالكامل.
- **دعم محاصيل إضافية:** البنية الحالية جاهزة للتوسع — فقط أضيفي ملفات المحصول الجديد في `processed_docs` وشغّلي الـ Pipeline من جديد.

---

## 🔐 ملاحظة أمان مهمة

لو سبق ورفعتِ أو شاركتِ مفاتيح API فعلية (OpenRouter / Gemini) في أي مكان (چات، رسالة، كود)، اعتبريها مكشوفة وقومي بعمل **Regenerate** لها فوراً من لوحة تحكم كل خدمة.

---

## 📁 هيكل الملفات

```
simple_rag_lab/
├── 01_documents.py
├── 02_preprocessing.py
├── 03_chunking.py
├── 04_vectorstore.py
├── 05_create_chroma_store.py
├── 06_context_builder.py
├── 07_ground_truth.py
├── 08_llm_generation.py
├── 09_error_analysis.py
├── 010_retrieval_eval.py
├── app.py
├── prompts.py
├── all_code_combined.py      # كل الأكواد مجمعة في ملف واحد للمرجعية
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

✨ **EU AgriExport RAG Engine**
