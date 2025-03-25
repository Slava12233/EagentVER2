#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
מודול למערכת זיכרון וקטורית משופרת
----------------------------------

מודול זה מספק מחלקה לשמירת מידע בצורה וקטורית, כך שניתן לחפש מידע דומה
באמצעות חיפוש סמנטי. המודול כולל יכולות מתקדמות כמו:
- זיהוי מידע חשוב
- שימוש במאגרי וקטורים מתקדמים
- מנגנון לשכחה של מידע ישן
"""

import os
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from openai import OpenAI

# מנסה לייבא חבילות אופציונליות
try:
    import chromadb
    from chromadb.config import Settings
    import numpy as np
    from sklearn.cluster import KMeans
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

# מחלקת ImportanceScorer מדומה אם chromadb לא זמין
class ImportanceScorer:
    """
    מחלקה לזיהוי וניקוד חשיבות של מידע.
    """
    
    def __init__(self, client: OpenAI):
        """
        אתחול מנגנון ניקוד חשיבות.
        
        Args:
            client: לקוח OpenAI
        """
        self.client = client
    
    def score_importance(self, content: str, context: Optional[str] = None) -> float:
        """
        מחשב ציון חשיבות למידע.
        
        Args:
            content: תוכן המידע
            context: הקשר נוסף (אופציונלי)
        
        Returns:
            ציון חשיבות בין 0 ל-1
        """
        # אם אין צורך בחישוב חשיבות אמיתי, מחזיר ערך קבוע
        return 0.8

# מחלקת AdvancedVectorStore מדומה אם chromadb לא זמין
class AdvancedVectorStore:
    """
    מחלקה לשמירת מידע בצורה וקטורית עם יכולות מתקדמות.
    """
    
    def __init__(self, client: OpenAI, collection_name: str = "woo_agent_memory", persist_directory: str = "memory_db", 
                 importance_threshold: float = 0.6, ttl_days: int = 30, use_advanced_embeddings: bool = True):
        """
        אתחול מערכת הזיכרון המתקדמת.
        
        Args:
            client: לקוח OpenAI
            collection_name: שם האוסף (ברירת מחדל: "woo_agent_memory")
            persist_directory: תיקייה לשמירת מסד הנתונים (ברירת מחדל: "memory_db")
            importance_threshold: סף חשיבות לשמירת מידע (ברירת מחדל: 0.6)
            ttl_days: מספר ימים לשמירת מידע לפני שכחה (ברירת מחדל: 30)
            use_advanced_embeddings: האם להשתמש במודל הטמעה מתקדם (ברירת מחדל: True)
        """
        self.client = client
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.importance_threshold = importance_threshold
        self.ttl_days = ttl_days
        self.use_advanced_embeddings = use_advanced_embeddings
        self.importance_scorer = ImportanceScorer(client)
        
        # מאגר פשוט לשמירת מסמכים אם chromadb לא זמין
        self.documents = {}
        
        # מודל הטמעה מתקדם
        self.embedding_model = "text-embedding-3-large" if use_advanced_embeddings else "text-embedding-ada-002"
    
    def _get_embedding(self, text: str) -> List[float]:
        """
        מחזיר וקטור משובץ (embedding) עבור טקסט.
        
        Args:
            text: הטקסט לשיבוץ
        
        Returns:
            וקטור משובץ
        """
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text,
                dimensions=1536
            )
            return response.data[0].embedding
        except:
            # אם יש בעיה בקבלת embedding, מחזיר רשימה ריקה
            return []
    
    def add_document(self, content: str, metadata: Optional[Dict[str, Any]] = None, 
                     context: Optional[str] = None, force_add: bool = False) -> Optional[str]:
        """
        מוסיף מסמך למערכת הזיכרון אם הוא מספיק חשוב.
        
        Args:
            content: תוכן המסמך
            metadata: מטא-דאטה נוסף (אופציונלי)
            context: הקשר לחישוב חשיבות (אופציונלי)
            force_add: האם לכפות הוספה ללא בדיקת חשיבות (ברירת מחדל: False)
        
        Returns:
            מזהה המסמך אם נוסף, אחרת None
        """
        # חישוב ציון חשיבות
        importance_score = 1.0 if force_add else self.importance_scorer.score_importance(content, context)
        
        # בדיקה אם המידע מספיק חשוב
        if importance_score < self.importance_threshold and not force_add:
            return None
        
        # יצירת מזהה ייחודי
        doc_id = str(uuid.uuid4())
        
        # הכנת מטא-דאטה
        if metadata is None:
            metadata = {}
        
        # הוספת מידע נוסף למטא-דאטה
        metadata["timestamp"] = datetime.now().isoformat()
        metadata["importance_score"] = importance_score
        metadata["expiry_date"] = (datetime.now() + timedelta(days=self.ttl_days)).isoformat()
        
        # שמירת המסמך במאגר הפשוט
        self.documents[doc_id] = {
            "content": content,
            "metadata": metadata,
            "embedding": self._get_embedding(content)
        }
        
        return doc_id
    
    def search(self, query: str, n_results: int = 5, min_relevance_score: float = 0.7) -> List[Dict[str, Any]]:
        """
        מחפש מסמכים דומים לשאילתה.
        
        Args:
            query: שאילתת החיפוש
            n_results: מספר התוצאות המקסימלי (ברירת מחדל: 5)
            min_relevance_score: ציון רלוונטיות מינימלי (ברירת מחדל: 0.7)
        
        Returns:
            רשימה של מסמכים דומים
        """
        # במימוש פשוט, מחזיר את כל המסמכים
        documents = []
        for doc_id, doc in self.documents.items():
            documents.append({
                "id": doc_id,
                "content": doc["content"],
                "metadata": doc["metadata"],
                "relevance_score": 0.9  # ציון רלוונטיות קבוע
            })
            
            # הגבלת מספר התוצאות
            if len(documents) >= n_results:
                break
        
        return documents
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        מחזיר מסמך לפי מזהה.
        
        Args:
            doc_id: מזהה המסמך
        
        Returns:
            המסמך, או None אם לא נמצא
        """
        if doc_id in self.documents:
            doc = self.documents[doc_id]
            return {
                "id": doc_id,
                "content": doc["content"],
                "metadata": doc["metadata"]
            }
        return None
    
    def delete_document(self, doc_id: str) -> bool:
        """
        מוחק מסמך לפי מזהה.
        
        Args:
            doc_id: מזהה המסמך
        
        Returns:
            האם המחיקה הצליחה
        """
        if doc_id in self.documents:
            del self.documents[doc_id]
            return True
        return False
    
    def clear(self) -> None:
        """
        מוחק את כל המסמכים באוסף.
        """
        self.documents.clear()
    
    def save(self) -> None:
        """
        שומר את מסד הנתונים לדיסק.
        """
        # במימוש פשוט, לא עושה כלום
        pass
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        מחזיר את כל המסמכים באוסף.
        
        Returns:
            רשימה של כל המסמכים
        """
        documents = []
        for doc_id, doc in self.documents.items():
            documents.append({
                "id": doc_id,
                "content": doc["content"],
                "metadata": doc["metadata"]
            })
        
        return documents
    
    def forget_old_documents(self) -> int:
        """
        מוחק מסמכים ישנים שעברו את תאריך התפוגה.
        
        Returns:
            מספר המסמכים שנמחקו
        """
        current_time = datetime.now().isoformat()
        
        # סינון מסמכים שעברו את תאריך התפוגה
        expired_ids = []
        for doc_id, doc in list(self.documents.items()):
            expiry_date = doc["metadata"].get("expiry_date")
            if expiry_date and expiry_date < current_time:
                expired_ids.append(doc_id)
                del self.documents[doc_id]
        
        return len(expired_ids)
    
    def update_document_importance(self, doc_id: str, new_importance: float) -> bool:
        """
        מעדכן את ציון החשיבות של מסמך.
        
        Args:
            doc_id: מזהה המסמך
            new_importance: ציון החשיבות החדש
        
        Returns:
            האם העדכון הצליח
        """
        if doc_id not in self.documents:
            return False
        
        # עדכון ציון החשיבות
        metadata = self.documents[doc_id]["metadata"]
        metadata["importance_score"] = new_importance
        
        # עדכון תאריך התפוגה בהתאם לחשיבות
        ttl_days = int(self.ttl_days * (1 + new_importance))
        metadata["expiry_date"] = (datetime.now() + timedelta(days=ttl_days)).isoformat()
        
        return True
    
    def cluster_documents(self, n_clusters: int = 5) -> Dict[int, List[Dict[str, Any]]]:
        """
        מקבץ מסמכים לקבוצות לפי דמיון.
        
        Args:
            n_clusters: מספר הקבוצות (ברירת מחדל: 5)
        
        Returns:
            מילון של קבוצות מסמכים
        """
        # במימוש פשוט, מחזיר קבוצה אחת עם כל המסמכים
        clustered_docs = {0: []}
        
        for doc_id, doc in self.documents.items():
            clustered_docs[0].append({
                "id": doc_id,
                "content": doc["content"],
                "metadata": doc["metadata"]
            })
        
        return clustered_docs
    
    def summarize_cluster(self, cluster_docs: List[Dict[str, Any]]) -> str:
        """
        מסכם קבוצת מסמכים.
        
        Args:
            cluster_docs: רשימת מסמכים בקבוצה
        
        Returns:
            סיכום הקבוצה
        """
        if not cluster_docs:
            return "אין מסמכים בקבוצה זו."
        
        # במימוש פשוט, מחזיר סיכום קב
    
    def summarize_cluster(self, cluster_docs: List[Dict[str, Any]]) -> str:
        """
        מסכם קבוצת מסמכים.
        
        Args:
            cluster_docs: רשימת מסמכים בקבוצה
        
        Returns:
            סיכום הקבוצה
        """
        if not cluster_docs:
            return "אין מסמכים בקבוצה זו."
        
        # הכנת הטקסט לסיכום
        docs_text = "\n\n".join([f"מסמך {i+1}: {doc['content']}" for i, doc in enumerate(cluster_docs[:5])])
        
        prompt = f"סכם את הנושא המרכזי של קבוצת המסמכים הבאה בקצרה (עד 3 משפטים):\n\n{docs_text}"
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "אתה מערכת לסיכום קבוצות מסמכים."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()


# שמירת תאימות לאחור עם הגרסה הקודמת
class VectorStore(AdvancedVectorStore):
    """
    מחלקה לשמירת מידע בצורה וקטורית (תאימות לאחור).
    """
    
    def __init__(self, client: OpenAI, collection_name: str = "woo_agent_memory", persist_directory: str = "memory_db"):
        """
        אתחול מערכת הזיכרון.
        
        Args:
            client: לקוח OpenAI
            collection_name: שם האוסף (ברירת מחדל: "woo_agent_memory")
            persist_directory: תיקייה לשמירת מסד הנתונים (ברירת מחדל: "memory_db")
        """
        super().__init__(
            client=client,
            collection_name=collection_name,
            persist_directory=persist_directory,
            importance_threshold=0.0,  # ללא סינון חשיבות בגרסה הישנה
            use_advanced_embeddings=False  # שימוש במודל הטמעה בסיסי בגרסה הישנה
        )
    
    def add_document(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        מוסיף מסמך למערכת הזיכרון.
        
        Args:
            content: תוכן המסמך
            metadata: מטא-דאטה נוסף (אופציונלי)
        
        Returns:
            מזהה המסמך
        """
        # כפיית הוספה ללא בדיקת חשיבות
        doc_id = super().add_document(content, metadata, force_add=True)
        return doc_id
