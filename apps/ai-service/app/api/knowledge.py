"""
知识库 API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from app.rag.vector_store import VectorStore

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
vector_store = VectorStore()


class IndexDocumentRequest(BaseModel):
    documents: List[Dict] = Field(..., description="文档列表")
    collection_name: str = Field("brainspark_knowledge", description="集合名称")


class SearchRequest(BaseModel):
    query: str = Field(..., description="查询文本")
    collection_name: str = Field("brainspark_knowledge", description="集合名称")
    top_k: int = Field(5, ge=1, le=20, description="返回结果数")


@router.post("/index")
async def index_documents(request: IndexDocumentRequest):
    """索引文档到向量库"""
    try:
        result = vector_store.index_documents(
            documents=request.documents,
            collection_name=request.collection_name,
        )
        return {
            "status": "success",
            "indexed_count": result,
            "collection": request.collection_name,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"索引失败: {str(e)}")


@router.post("/search")
async def search_knowledge(request: SearchRequest):
    """搜索知识库"""
    try:
        results = vector_store.search(
            query=request.query,
            collection_name=request.collection_name,
            top_k=request.top_k,
        )
        return {
            "query": request.query,
            "results": results,
            "total": len(results),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")