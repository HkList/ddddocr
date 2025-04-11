# 基础镜像：使用官方 Python 3.10
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# 拷贝文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 启动 FastAPI 服务（监听 0.0.0.0）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
