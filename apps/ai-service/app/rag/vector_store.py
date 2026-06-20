"""
向量存储服务 - Milvus 集成
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
import hashlib
import json


class VectorStore:
    """向量存储服务"""

    def __init__(self, host: str = "localhost", port: int = 19530):
        self.host = host
        self.port = port
        self.collections: Dict[str, List[Dict]] = {}
        self.connected = False

    async def connect(self):
        """连接 Milvus 服务"""
        try:
            # TODO: 实际连接 Milvus
            # from pymilvus import connections
            # connections.connect(host=self.host, port=self.port)
            self.connected = True
        except Exception as e:
            print(f"Milvus 连接失败: {e}")
            self.connected = False

    async def disconnect(self):
        """断开连接"""
        self.connected = False

    def _get_embedding(self, text: str) -> List[float]:
        """获取文本向量（模拟）"""
        # TODO: 使用实际的 embedding 模型
        import hashlib

        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        # 将哈希值映射到 128 维向量
        vector = [b / 255.0 for b in hash_bytes]
        # 扩展到 768 维
        while len(vector) < 768:
            vector.extend(vector[: min(768 - len(vector), len(vector))])
        return vector[:768]

    def index_documents(
        self,
        documents: List[Dict],
        collection_name: str = "brainspark_knowledge",
    ) -> int:
        """
        索引文档到向量库

        Args:
            documents: 文档列表，每项包含 id, text, metadata
            collection_name: 集合名称

        Returns:
            索引的文档数量
        """
        if collection_name not in self.collections:
            self.collections[collection_name] = []

        indexed = 0
        for doc in documents:
            doc_id = doc.get("id", hashlib.md5(doc.get("text", "").encode()).hexdigest())
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})

            vector_entry = {
                "id": doc_id,
                "text": text,
                "vector": self._get_embedding(text),
                "metadata": metadata,
                "indexed_at": datetime.utcnow().isoformat(),
            }

            self.collections[collection_name].append(vector_entry)
            indexed += 1

        return indexed

    def search(
        self,
        query: str,
        collection_name: str = "brainspark_knowledge",
        top_k: int = 5,
    ) -> List[Dict]:
        """
        搜索知识库

        Args:
            query: 查询文本
            collection_name: 集合名称
            top_k: 返回结果数

        Returns:
            搜索结果列表
        """
        if collection_name not in self.collections:
            return []

        query_vector = self._get_embedding(query)
        documents = self.collections[collection_name]

        # 计算余弦相似度
        scored_docs = []
        for doc in documents:
            score = self._cosine_similarity(query_vector, doc["vector"])
            scored_docs.append((score, doc))

        # 排序并返回 top_k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        results = scored_docs[:top_k]

        return [
            {
                "id": doc["id"],
                "text": doc["text"],
                "score": round(score, 4),
                "metadata": doc["metadata"],
            }
            for score, doc in results
        ]

    def _cosine_similarity(
        self, vec1: List[float], vec2: List[float]
    ) -> float:
        """计算余弦相似度"""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def delete_collection(self, collection_name: str):
        """删除集合"""
        if collection_name in self.collections:
            del self.collections[collection_name]

    def get_collection_stats(self, collection_name: str) -> Dict:
        """获取集合统计信息"""
        if collection_name not in self.collections:
            return {"exists": False, "document_count": 0}

        docs = self.collections[collection_name]
        return {
            "exists": True,
            "document_count": len(docs),
            "vector_dimension": len(docs[0]["vector"]) if docs else 0,
        }