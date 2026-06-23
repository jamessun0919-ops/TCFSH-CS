# Gunicorn 伺服器配置設定檔
import os

# 連線逾時設定（秒）
# 幾何生成與 SVG 繪製有時可能花費 30 秒以上，因此將超時上限調整為 120 秒以防止 Gunicorn 殺死工作進程
timeout = 120

# 工作進程數量
workers = 2

# 綁定位址與連接埠
port = os.environ.get("PORT", "5000")
bind = f"0.0.0.0:{port}"
