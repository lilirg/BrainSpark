"""健康检查接口测试"""

from __future__ import annotations

from httpx import AsyncClient, ASGITransport
import pytest


@pytest.mark.asyncio
async def test_health_check():
    """测试健康检查接口"""
    from main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data