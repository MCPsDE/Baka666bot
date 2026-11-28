"""用户凭证获取工具（从 malody.top 云端接口按 QQ 号实时获取 session token）。"""
from ...MalodyAPI.database import db
from ...MalodyAPI.core import SITE_BASE

BIND_GUIDE_TEXT = (
    f"请先前往 {SITE_BASE} 注册并绑定 Malody 账号后关联当前 QQ 号，"
    "绑定后即可直接使用 Bot 指令。"
)


async def get_user_creds(qq: str, force_refresh: bool = False):
    """获取绑定的用户凭证。返回 (uid, user_dict) 或 (None, None)。"""
    user = await db.get_user_by_qq(qq, force_refresh=force_refresh)
    if not user or not user.get("access_token"):
        return None, None
    return str(user["uid"]), user