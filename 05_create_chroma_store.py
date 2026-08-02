import importlib
from pathlib import Path
import chromadb
from chromadb.config import Settings

# استيراد موديول التمثيل الاتجاهي (الملف الرابع 04_vectorstore)
vectors = importlib.import_module("04_vectorstore")

# جعل المسار ديناميكياً داخل مجلد مشروعك مباشرة
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "chroma_db"

COLLECTION_NAME = "eu_agriexport_docs"


def create_vector_store():
    print(f"\n💾 [05_create_chroma_store] جاري إنشاء قاعدة بيانات Chroma Vector Store...")

    client = chromadb.PersistentClient(
        path=str(DB_PATH),
        settings=Settings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection(COLLECTION_NAME)

    # رفع الـ Chunks والمستندات والـ Embeddings بنفس طريقة الدكتور بالضبط
    collection.upsert(
        ids=[chunk["chunk_id"] for chunk in vectors.chunks],
        documents=[chunk["chunk_text"] for chunk in vectors.chunks],
        metadatas=[
            {
                "document_id": chunk["document_id"],
                "title": chunk["title"],
                "is_current": str(chunk["is_current"]),
            }
            for chunk in vectors.chunks
        ],
        embeddings=vectors.chunk_embeddings.tolist(),
    )

    return collection


if __name__ == "__main__":
    create_vector_store()
    print("🎉 Chroma vector store created successfully.")