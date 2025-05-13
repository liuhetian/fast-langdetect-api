# 语言检测API服务

这是一个基于FastAPI和fast-langdetect的语言检测REST API服务。

## 功能

- 单一语言检测
- 多语言检测
- 默认使用大模型以提高准确性
- Docker支持

## 本地运行

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
uvicorn main:app --reload
```

访问 http://localhost:8000/docs 查看API文档。

## Docker部署

### 构建镜像

```bash
docker build -t langdetect-api .
```

### 运行容器

```bash
docker run -p 8000:8000 langdetect-api
```

## API使用

### 单语言检测

```bash
curl -X 'POST' \
  'http://localhost:8000/detect' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "你好，世界！",
  "low_memory": false
}'
```

### 多语言检测

```bash
curl -X 'POST' \
  'http://localhost:8000/detect-multilingual' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "Hello 世界 こんにちは",
  "low_memory": false,
  "k": 3
}'
```
