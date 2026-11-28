# MalodyAPI/database.py
"""云端账号绑定客户端（通过 malody.top HTTPS API 读取与获取 session token）。"""
import aiohttp
from nonebot.log import logger
from .core import SITE_BASE, DEFAULT_TIMEOUT


class CloudDatabase:
    def __init__(self, site_base: str = None):
        self.site_base = (site_base or SITE_BASE).rstrip("/")
        self.session: aiohttp.ClientSession | None = None

    async def connect(self):
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=max(DEFAULT_TIMEOUT, 15))
            self.session = aiohttp.ClientSession(timeout=timeout)

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
        self.session = None

    async def fetch_session_by_qq(self, qq: str, force_refresh: bool = False) -> dict | None:
        """向 malody.top 请求该 QQ 号绑定的 Malody 账号及 session token。"""
        qq_str = str(qq or "").strip()
        if not qq_str:
            return None
        await self.connect()
        url = f"{self.site_base}/api/malody/bot/session-token"
        params = {"qq": qq_str}
        if force_refresh:
            params["refresh"] = "1"
        try:
            async with self.session.get(url, params=params) as resp:
                payload = await resp.json(content_type=None)
        except Exception as e:
            logger.error(f"请求 malody.top session token 失败: {e}")
            return None

        if not isinstance(payload, dict) or not payload.get("success"):
            return None
        data = payload.get("data")
        if not isinstance(data, dict) or not data.get("access_token"):
            return None
        return data

    async def get_uid_by_qq(self, qq: str) -> str | None:
        data = await self.fetch_session_by_qq(qq)
        if not data:
            return None
        uid = data.get("uid")
        return str(uid) if uid is not None else None

    async def get_user_by_qq(self, qq: str, force_refresh: bool = False) -> dict | None:
        return await self.fetch_session_by_qq(qq, force_refresh=force_refresh)

    async def get_user(self, uid: str) -> dict | None:
        return None

    async def save_user(self, *args, **kwargs):
        return None

    async def bind_qq(self, uid: str, qq: str):
        return None

    async def unbind_qq(self, uid: str):
        return None

    async def get_qq_by_uid(self, uid: str) -> str | None:
        return None


db = CloudDatabase()