import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pymongo import MongoClient

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB = os.getenv("MONGODB_DB", "nvoin_chat_db")

class MongoDBHandler:
    """Pengelola penyimpanan MongoDB untuk Riwayat Percakapan (Conversation History)."""
    def __init__(self, uri: str = MONGODB_URI, db_name: str = MONGODB_DB):
        self.client = None
        self.db = None
        self.uri = uri
        self.db_name = db_name
        self.connect()

    def connect(self):
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=2000)
            self.db = self.client[self.db_name]
        except Exception as e:
            print(f"[MongoDB Warning] Tidak dapat terhubung ke MongoDB ({e}). Penyimpanan histori memori aktif fallback.")

    def save_conversation_turn(
        self,
        session_id: str,
        project_id: str,
        user_id: Optional[str],
        user_prompt: str,
        ai_response: str,
        subagent_logs: List[Dict[str, Any]],
        confidence_score: float = 1.0,
        requires_clarification: bool = False,
        implementation_plan: Optional[str] = None
    ) -> bool:
        """Menyimpan satu giliran percakapan (turn) ke dalam dokumen sesi MongoDB."""
        if self.db is None:
            return False

        try:
            collection = self.db["conversation_history"]
            turn_doc = {
                "timestamp": datetime.utcnow(),
                "user_prompt": user_prompt,
                "ai_response": ai_response,
                "subagent_logs": subagent_logs,
                "confidence_score": confidence_score,
                "requires_clarification": requires_clarification,
                "implementation_plan": implementation_plan
            }

            collection.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "project_id": project_id,
                        "user_id": user_id or "anonymous",
                        "updated_at": datetime.utcnow()
                    },
                    "$setOnInsert": {
                        "created_at": datetime.utcnow()
                    },
                    "$push": {
                        "turns": turn_doc
                    }
                },
                upsert=True
            )
            return True
        except Exception as e:
            print(f"[MongoDB Error] Gagal menyimpan percakapan: {e}")
            return False

    def get_conversation_history(self, project_id: str) -> List[Dict[str, Any]]:
        """Mengambil seluruh riwayat percakapan untuk suatu project_id."""
        if self.db is None:
            return []

        try:
            collection = self.db["conversation_history"]
            cursor = collection.find({"project_id": project_id}).sort("updated_at", -1)
            results = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                results.append(doc)
            return results
        except Exception as e:
            print(f"[MongoDB Error] Gagal mengambil histori percakapan: {e}")
            return []

# Singleton instance
mongo_handler = MongoDBHandler()
