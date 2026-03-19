"""
高德地图 POI 搜索采集模块（主力数据源）
通过高德地图开放API搜索服装企业的公开信息
API文档: https://lbs.amap.com/api/webservice/guide/api/search
"""

import time
import random
import logging

import requests

from config import AMAP_KEY, REQUEST_DELAY, REQUEST_TIMEOUT, MAX_PAGES_PER_QUERY

logger = logging.getLogger(__name__)

# 服装相关关键词，用于过滤无关结果
RELEVANT_TERMS = {
    "服装", "制衣", "服饰", "成衣", "针织", "梭织", "纺织",
    "羽绒", "棉服", "女装", "男装", "童装", "内衣", "外套",
    "牛仔", "时装", "衬衫", "裤业", "毛衫", "皮草",
}


def _is_relevant(name, poi_type):
    """判断POI是否与服装行业相关"""
    text = name + poi_type
    return any(term in text for term in RELEVANT_TERMS)


def search_amap(keyword, city):
    """
    通过高德地图 POI 搜索服装企业
    返回 [{"name", "address", "phone", "region", ...}]
    """
    if not AMAP_KEY:
        logger.warning("[高德地图] 未配置 AMAP_KEY，请在 config.py 中填入")
        return []

    results = []
    page_size = 25  # 高德每页最多25条

    for page in range(1, MAX_PAGES_PER_QUERY + 1):
        try:
            delay = random.uniform(*REQUEST_DELAY)
            time.sleep(delay)

            params = {
                "key": AMAP_KEY,
                "keywords": keyword,
                "city": city,
                "citylimit": "true",
                "offset": page_size,
                "page": page,
                "output": "json",
                "extensions": "all",  # 返回更多字段
            }
            resp = requests.get(
                "https://restapi.amap.com/v3/place/text",
                params=params,
                timeout=REQUEST_TIMEOUT,
            )
            data = resp.json()

            if data.get("status") != "1":
                info = data.get("info", "未知错误")
                infocode = data.get("infocode", "")
                if infocode == "10044":
                    logger.error("[高德地图] 今日API配额已用完，明天再试")
                    return results
                logger.warning(f"[高德地图] API错误: {info} (code:{infocode})")
                break

            pois = data.get("pois", [])
            if not pois:
                break

            for poi in pois:
                name = poi.get("name", "")
                poi_type = poi.get("type", "")

                # 过滤无关结果
                if not _is_relevant(name, poi_type):
                    continue

                # 处理电话：高德可能返回 str / list / []
                tel_raw = poi.get("tel", "")
                if isinstance(tel_raw, list):
                    tel = " / ".join(t for t in tel_raw if t) if tel_raw else ""
                elif isinstance(tel_raw, str):
                    tel = "" if tel_raw in ("[]", "") else tel_raw.replace(";", " / ")
                else:
                    tel = str(tel_raw) if tel_raw else ""

                # 处理地址：同样可能是 list
                addr_raw = poi.get("address", "")
                if isinstance(addr_raw, list):
                    addr = addr_raw[0] if addr_raw else ""
                elif isinstance(addr_raw, str):
                    addr = "" if addr_raw in ("[]", "") else addr_raw
                else:
                    addr = str(addr_raw) if addr_raw else ""

                company = {
                    "name": name,
                    "phone": tel,
                    "region": poi.get("pname", "") + poi.get("cityname", "") + poi.get("adname", ""),
                    "city": poi.get("cityname", ""),
                    "district": poi.get("adname", ""),
                    "address": addr,
                    "industry": poi_type,
                    "source": "高德地图",
                    "search_keyword": keyword,
                    "search_region": city,
                    "location": poi.get("location", ""),
                }
                results.append(company)

            if len(pois) < page_size:
                break  # 已经是最后一页

        except requests.Timeout:
            logger.warning(f"[高德地图] 请求超时 (page={page})")
            break
        except requests.RequestException as e:
            logger.warning(f"[高德地图] 网络错误: {e}")
            break
        except Exception as e:
            logger.warning(f"[高德地图] 未知错误: {e}")
            break

    return results
