"""
Malody API 公共模块：请求工具、常量、通用方法
所有配置从 Nonebot2 .env 读取，一处定义全局使用。
"""
import time
import requests
from typing import Optional
from nonebot import get_driver

_config = get_driver().config

API_BASE: str = getattr(_config, "malody_api_base", "https://api.mugzone.net")
SITE_BASE: str = getattr(_config, "malody_site_base", "https://malody.top").rstrip("/")
MALODY_VERSION: str = getattr(_config, "malody_version", "6.6.43")
VER: str = getattr(_config, "malody_ver", "394795")
STORE_API: int = int(getattr(_config, "malody_store_api", "202409"))
DEFAULT_TIMEOUT: int = int(getattr(_config, "malody_timeout", "10"))

HEADERS = {
    "User-Agent": f"Malody {MALODY_VERSION}",
    "Malody": MALODY_VERSION,
    "Accept-Encoding": "gzip, identity",
    "Connection": "Keep-Alive, TE",
    "TE": "identity",
}


def _get(
    path: str,
    params: dict,
    access_token: Optional[str] = None,
    uid: Optional[str] = None,
    use_store: bool = False,
    api_base: str = None,
    timeout: int = None,
) -> dict:
    """通用 GET 请求，自动附加认证参数和时间戳。"""
    api_base = api_base or API_BASE
    timeout = timeout or DEFAULT_TIMEOUT
    url = f"{api_base}/api/{path}"
    if use_store:
        params["api"] = STORE_API
        params["uid"] = uid
        params["key"] = access_token
    elif access_token:
        params["key"] = access_token
        params["uid"] = uid
    params["t"] = int(time.time())
    resp = requests.get(url, params=params, headers=HEADERS, verify=False, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"API {path} failed: {data}")
    return data


def _post(
    path: str,
    data: dict,
    access_token: Optional[str] = None,
    uid: Optional[str] = None,
    use_store: bool = False,
    api_base: str = None,
    timeout: int = None,
) -> dict:
    """通用 POST 请求，自动附加认证参数和时间戳。"""
    api_base = api_base or API_BASE
    timeout = timeout or DEFAULT_TIMEOUT
    url = f"{api_base}/api/{path}"
    params = {"t": int(time.time())}
    if use_store:
        params["api"] = STORE_API
        params["uid"] = uid
        params["key"] = access_token
    elif access_token:
        params["key"] = access_token
        params["uid"] = uid
    # 匹配客户端行为: 有 bver 时自动附加 ver
    if data and "bver" in data and "ver" not in data:
        data["ver"] = VER
    resp = requests.post(url, params=params, data=data, headers=HEADERS, verify=False, timeout=timeout)
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") != 0:
        raise RuntimeError(f"API {path} failed: {result}")
    return result


def _paginate(
    path: str,
    params: dict,
    access_token: Optional[str] = None,
    uid: Optional[str] = None,
    use_store: bool = False,
    start: int = 0,
    count: int = 100,
    timeout: int = None,
) -> tuple[list, int]:
    """自动翻页获取数据。返回 (全部数据列表, 实际获取数量)。
    从 start 位置开始，持续翻页直到凑满 count 条或无更多数据。
    支持 hasMore/next 分页机制的 API。"""
    timeout = timeout or DEFAULT_TIMEOUT
    all_data = []
    next_from = start
    max_pages = 20  # 安全上限
    while len(all_data) < count and max_pages > 0:
        max_pages -= 1
        p = dict(params)
        p["from"] = next_from
        p["limit"] = min(100, count - len(all_data))
        result = _get(path, p, access_token=access_token, uid=uid, use_store=use_store, timeout=timeout)
        page = result.get("data", [])
        if not page:
            break
        all_data.extend(page)
        if not result.get("hasMore"):
            break
        next_from = result.get("next", 0)
        if next_from == 0:
            break
    return all_data, len(all_data)
