"""爬取服务 - 封装现有爬虫为后台任务"""

import json
import threading
import logging
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from scraper_map import search_amap
from server.database import SessionLocal
from server.models import Lead, ScrapeTask
from server.routers.amap_keys import get_active_key, increment_key_usage

logger = logging.getLogger(__name__)


def _run_scrape(task_id: int):
    """在后台线程中执行爬取任务"""
    db = SessionLocal()
    try:
        task = db.query(ScrapeTask).filter(ScrapeTask.id == task_id).first()
        if not task:
            return

        task.status = "running"
        task.started_at = datetime.now()
        db.commit()

        keywords = task.get_keywords()
        regions = task.get_regions()
        total_found = 0
        new_added = 0
        progress = 0

        def on_api_call(key_value):
            """每次 API 调用后增加计数"""
            increment_key_usage(db, key_value)

        for region in regions:
            for keyword in keywords:
                try:
                    # 每次搜索前获取当前可用 key
                    amap_key = get_active_key(db)
                    if not amap_key:
                        logger.error("所有高德 Key 额度已用完")
                        task.status = "failed"
                        task.error_msg = "所有高德 Key 额度已用完"
                        task.finished_at = datetime.now()
                        db.commit()
                        return

                    results = search_amap(keyword, region, amap_key=amap_key, on_api_call=on_api_call)
                    total_found += len(results)

                    # 写入数据库，去重
                    for item in results:
                        name = item.get("name", "").strip()
                        if not name:
                            continue

                        existing = db.query(Lead).filter(Lead.name == name).first()
                        if existing:
                            # 如果现有记录没电话但新记录有，更新
                            if not existing.phone and item.get("phone"):
                                existing.phone = item["phone"]
                                existing.updated_at = datetime.now()
                        else:
                            lead = Lead(
                                name=name,
                                phone=item.get("phone", ""),
                                city=item.get("city", ""),
                                district=item.get("district", ""),
                                address=item.get("address", ""),
                                region=item.get("region", ""),
                                industry=item.get("industry", ""),
                                location=item.get("location", ""),
                                source=item.get("source", ""),
                                search_keyword=keyword,
                                search_region=region,
                            )
                            db.add(lead)
                            new_added += 1

                    db.commit()

                except Exception as e:
                    logger.error(f"爬取 {region}-{keyword} 失败: {e}")
                    db.rollback()

                progress += 1
                task.progress = progress
                task.total_found = total_found
                task.new_added = new_added
                db.commit()

        task.status = "completed"
        task.finished_at = datetime.now()
        db.commit()
        logger.info(f"任务 #{task_id} 完成: 找到 {total_found}, 新增 {new_added}")

    except Exception as e:
        logger.error(f"任务 #{task_id} 失败: {e}")
        try:
            task = db.query(ScrapeTask).filter(ScrapeTask.id == task_id).first()
            if task:
                task.status = "failed"
                task.error_msg = str(e)
                task.finished_at = datetime.now()
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


def start_scrape_task(task_id: int):
    """启动后台爬取线程"""
    thread = threading.Thread(target=_run_scrape, args=(task_id,), daemon=True)
    thread.start()
