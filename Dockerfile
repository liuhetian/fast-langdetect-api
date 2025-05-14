FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY pyproject.toml .

# 创建缓存目录
RUN mkdir -p /app/volume/dbs
RUN mkdir -p /app/volume/logs
RUN mkdir -p /app/models


# 安装依赖
RUN pip install --no-cache-dir .

# 复制应用代码
COPY main.py .

COPY /app/models/fast_langdetect/lid.176.bin /app/models/

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]