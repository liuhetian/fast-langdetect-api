FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY pyproject.toml .

# 创建缓存目录
RUN mkdir -p /volume/dbs
RUN mkdir -p /volume/logs
RUN mkdir -p /models


# 安装依赖
RUN pip install --no-cache-dir .

# 复制应用代码
COPY main.py .

COPY models/lid.176.bin /models/lid.176.bin

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]