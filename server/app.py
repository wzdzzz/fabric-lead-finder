"""FastAPI 应用入口"""

import os
import sys
import logging

# 确保项目根目录在 path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from server.database import init_db
from server.routers import auth, leads, tasks, export

from config import KEYWORDS, TARGET_REGIONS
from paths import STATIC_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="布匹中介获客工具 - 管理后台", version="2.0")

# CORS
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://zhongyu.store",
    "http://www.zhongyu.store",
    "https://zhongyu.store",
    "https://www.zhongyu.store",
]
# 服务器部署时允许对应域名
if os.environ.get("RENDER_EXTERNAL_URL"):
    allowed_origins.append(os.environ["RENDER_EXTERNAL_URL"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(tasks.router)
app.include_router(export.router)


@app.get("/api/config/keywords")
def get_keywords():
    return {"keywords": KEYWORDS}


@app.get("/api/config/regions")
def get_regions():
    return {"regions": TARGET_REGIONS}


# 生产模式：托管前端静态文件
logger.info("STATIC_DIR = %s, exists = %s", STATIC_DIR, os.path.isdir(STATIC_DIR))
assets_dir = os.path.join(STATIC_DIR, "assets")
if os.path.isdir(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    logger.info("Mounted /assets from %s", assets_dir)


@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    """SPA fallback: 所有非 API 路由返回 index.html"""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if not os.path.isfile(index_file):
        return JSONResponse(
            {"error": "Frontend not built", "static_dir": STATIC_DIR},
            status_code=503,
        )
    file_path = os.path.join(STATIC_DIR, full_path)
    if full_path and os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(index_file)


@app.on_event("startup")
def startup():
    init_db()
