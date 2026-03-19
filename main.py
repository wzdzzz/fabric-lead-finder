#!/usr/bin/env python3
"""
============================================
  布匹中介获客工具 v2.0
  数据源：高德地图 POI API（稳定可靠）
============================================

使用方式:
  python main.py                    # 全量采集
  python main.py --quick            # 快速模式（5城市×4关键词）
  python main.py -k 服装厂 制衣厂   # 指定关键词
  python main.py -r 广州 东莞       # 指定地区
  python main.py -k 服装厂 -r 广州  # 组合使用
"""

import sys
import argparse
import logging
from datetime import datetime

from config import (
    KEYWORDS, TARGET_REGIONS,
    QUICK_KEYWORDS, QUICK_REGIONS,
)
from scraper_map import search_amap
from exporter import export_to_excel

# 日志 - 用 utf-8 避免 Windows 乱码
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(stream=open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False)),
        logging.FileHandler("scraper.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def run(keywords, regions):
    """执行采集"""
    all_results = []
    total = len(keywords) * len(regions)
    done = 0

    for region in regions:
        for keyword in keywords:
            done += 1
            try:
                results = search_amap(keyword, region)
                all_results.extend(results)
                logger.info(f"[{done}/{total}] {region} - {keyword}: {len(results)} 条")
            except KeyboardInterrupt:
                logger.info("用户中断，保存已采集数据...")
                return all_results
            except Exception as e:
                logger.error(f"[{done}/{total}] {region} - {keyword} 失败: {e}")

    return all_results


def main():
    parser = argparse.ArgumentParser(description="布匹中介获客工具 - 服装企业信息采集")
    parser.add_argument("--quick", action="store_true", help="快速模式")
    parser.add_argument("-k", "--keyword", nargs="+", help="搜索关键词")
    parser.add_argument("-r", "--region", nargs="+", help="搜索城市")
    parser.add_argument("-o", "--output", help="输出文件名")
    args = parser.parse_args()

    # 确定参数
    keywords = args.keyword or (QUICK_KEYWORDS if args.quick else KEYWORDS)
    regions = args.region or (QUICK_REGIONS if args.quick else TARGET_REGIONS)

    print()
    print("=" * 50)
    print("  布匹中介获客工具 v2.0")
    print("  数据源: 高德地图 POI API")
    print("=" * 50)
    print(f"  关键词({len(keywords)}): {', '.join(keywords[:5])}{'...' if len(keywords)>5 else ''}")
    print(f"  城市({len(regions)}):  {', '.join(regions[:5])}{'...' if len(regions)>5 else ''}")
    print(f"  预计搜索: {len(keywords) * len(regions)} 次")
    print("=" * 50)
    print()

    start = datetime.now()
    results = run(keywords, regions)
    elapsed = (datetime.now() - start).total_seconds()

    if results:
        filepath = export_to_excel(results, args.output)
        # 统计
        unique_names = set(r["name"] for r in results)
        with_phone = sum(1 for r in results if r.get("phone"))

        print()
        print("=" * 50)
        print(f"  采集完成!")
        print(f"  原始记录: {len(results)} 条")
        print(f"  去重后:   ~{len(unique_names)} 家企业")
        print(f"  有电话:   {with_phone} 条")
        print(f"  耗时:     {elapsed:.0f} 秒")
        print(f"  文件:     {filepath}")
        print("=" * 50)
    else:
        print()
        print("未采集到数据，请检查:")
        print("  1. 网络是否正常")
        print("  2. API Key 是否有效")
        print("  3. 今日配额是否用完")


if __name__ == "__main__":
    main()
