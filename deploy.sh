#!/bin/bash
# 腾讯云一键部署脚本 - 布匹中介获客工具
# 用法: sudo bash deploy.sh
# 前提: 1) 代码已克隆到 /opt/fabric-lead-finder
#       2) 已手动创建 /opt/fabric-lead-finder/.env (含 AMAP_KEY, ADMIN_PASSWORD, JWT_SECRET)

set -e

APP_DIR="/opt/fabric-lead-finder"

echo "===== 布匹中介获客工具 - 部署开始 ====="

# ---- 1. 系统依赖 ----
echo "[1/7] 安装系统依赖..."
apt-get update -qq
apt-get install -y python3.9 python3.9-venv python3-pip nginx git
echo "  -> 系统依赖安装完成"

# ---- 2. 确认代码和环境变量 ----
echo "[2/7] 检查代码和配置..."
if [ ! -f "$APP_DIR/requirements.txt" ]; then
    echo "  错误: 代码未部署到 $APP_DIR"
    exit 1
fi
if [ ! -f "$APP_DIR/.env" ]; then
    echo "  错误: 缺少 .env 文件，请先创建:"
    echo '    echo -e "AMAP_KEY=xxx\nADMIN_PASSWORD=xxx\nJWT_SECRET=xxx" > /opt/fabric-lead-finder/.env'
    exit 1
fi
cd "$APP_DIR"
echo "  -> 代码和配置就绪"

# ---- 3. Python 虚拟环境 ----
echo "[3/7] 创建 Python 虚拟环境..."
python3.9 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "  -> Python 依赖安装完成"

# ---- 4. systemd 服务 ----
echo "[4/7] 配置 systemd 服务..."
cat > /etc/systemd/system/fabric-lead-finder.service <<'SERVICEEOF'
[Unit]
Description=Fabric Lead Finder Web App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/fabric-lead-finder
EnvironmentFile=/opt/fabric-lead-finder/.env
ExecStart=/opt/fabric-lead-finder/venv/bin/uvicorn server.app:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICEEOF

systemctl daemon-reload
systemctl enable fabric-lead-finder
echo "  -> systemd 服务已配置"

# ---- 5. Nginx 反向代理 ----
echo "[5/7] 配置 Nginx..."
cat > /etc/nginx/sites-available/fabric-lead-finder <<'NGINXEOF'
# HTTP -> HTTPS 跳转
server {
    listen 80;
    server_name zhongyu.store www.zhongyu.store;
    return 301 https://$host$request_uri;
}

# HTTPS
server {
    listen 443 ssl;
    server_name zhongyu.store www.zhongyu.store;

    ssl_certificate /etc/nginx/ssl/zhongyu.store_bundle.pem;
    ssl_certificate_key /etc/nginx/ssl/zhongyu.store.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINXEOF

ln -sf /etc/nginx/sites-available/fabric-lead-finder /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
echo "  -> Nginx 配置完成"

# ---- 6. 启动服务 ----
echo "[6/7] 启动服务..."
systemctl restart nginx
systemctl restart fabric-lead-finder

# ---- 7. 验证 ----
echo "[7/7] 验证服务状态..."
sleep 2
if systemctl is-active --quiet fabric-lead-finder; then
    echo "  -> 服务运行正常"
else
    echo "  -> 服务启动失败，查看日志: journalctl -u fabric-lead-finder -n 50"
    exit 1
fi

echo ""
echo "====================================="
echo "  部署完成！"
echo "  访问地址: https://zhongyu.store"
echo ""
echo "  常用命令:"
echo "    查看日志: journalctl -u fabric-lead-finder -f"
echo "    重启服务: systemctl restart fabric-lead-finder"
echo "    服务状态: systemctl status fabric-lead-finder"
echo "====================================="
