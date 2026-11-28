"""ma profile - 玩家资料卡"""
import asyncio, datetime
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.log import logger
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.player.info import get_player_info
from ...MalodyAPI.ranking.player.all import get_ranking_player_all
from ...MalodyAPI.player.search import search_player
from ...render.components import profile_card

async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user: await bot.send(event, BIND_GUIDE_TEXT); return
    touid, name_hint = uid, user.get("username", uid)
    if args.strip():
        kw = args.strip()
        if kw.isdigit(): touid = kw
        else:
            try:
                r = await asyncio.to_thread(search_player, keyword=kw, access_token=user["access_token"], uid=uid, limit=1)
                d = r.get("data", [])
                if d and d[0].get("uid"): touid = str(d[0]["uid"]); name_hint = d[0].get("username", touid)
            except: pass
    try:
        info = await asyncio.to_thread(get_player_info, touid=touid, access_token=user["access_token"], uid=uid)
        rank_data = None
        try:
            rank_data = await asyncio.to_thread(get_ranking_player_all, touid=touid, access_token=user["access_token"], uid=uid)
        except: pass
        gender_map = {0:"保密",1:"男",2:"女"}
        reg_ts = info.get("playTime",0)
        reg_str = datetime.datetime.fromtimestamp(reg_ts).strftime("%Y-%m-%d") if reg_ts else "?"
        rank_rows = []
        if rank_data:
            mn = ["Key","Step","DJ","Catch","Pad","Taiko","Ring","Slide"]
            for item in rank_data.get("data",[])[:8]:
                rank_rows.append((mn[item.get("mode",0)] if item.get("mode",0) < 8 else f"M{item.get('mode',0)}",
                    str(item.get("rank","?")), str(item.get("level","?")),
                    str(item.get("pc",0)), f"{item.get('acc',0):.1f}", str(item.get("combo",0))))
        img = await profile_card(
            username=info.get("username",touid), uid=touid,
            avatar_hash=info.get("avatar",""),
            gold=str(info.get("gold",0)), playtime=reg_str,
            played=f"{info.get('playedTime',0)}s",
            gender=gender_map.get(info.get("gender",0),""),
            rank_rows=rank_rows)
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"profile: {e}"); await bot.send(event, "获取失败")
