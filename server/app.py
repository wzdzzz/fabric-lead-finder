"""FastAPI 应用入口"""

import os
import sys
import logging

# 确保项目根目录在 path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from server.database import init_db
from server.routers import auth, leads, tasks, export

from config import KEYWORDS, TARGET_REGIONS
from paths import STATIC_DIR

logger = logging.getLogger(__name__)

app = FastAPI(title="布匹中介获客工具 - 管理后台", version="2.0")

# CORS
allowed_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
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
logger.info(f"STATIC_DIR = {STATIC_DIR}, exists = {os.path.isdir(STATIC_DIR)}")
if os.path.isdir(STATIC_DIR):
    # 挂载所有静态资源（js/css/图片等）
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")
    logger.info("Mounted /assets from %s", os.path.join(STATIC_DIR, "assets"))

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        """SPA fallback: 所有非 API 路由返回 index.html"""
        file_path = os.path.join(STATIC_DIR, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
else:
    logger.warning("Frontend not found at %s - SPA routes not registered", STATIC_DIR)


@app.on_event("startup")
def startup():
    init_db()
