from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from fast_langdetect import detect, detect_multilingual, LangDetector, LangDetectConfig, DetectError

app = FastAPI(
    title="语言检测API",
    description="基于fast_langdetect的语言检测服务",
    version="0.0.1"
)

# 配置检测器
config = LangDetectConfig(
    cache_dir="/app/cache",
    allow_fallback=False  # 启用回退到小模型
)
detector = LangDetector(config)

class TextRequest(BaseModel):
    text: str
    model: Literal['fast-langdetect', 'auto', 'llm'] = Field(default='fast-langdetect', description="检测模型")
    fast_langdetect_min_score: float | None = Field(default=None, ge=0.0, le=1.0, description="fast-langdetect最小置信度，低于这个值就会用大模型再检测一次")
    

class LanguageResult(BaseModel):
    lang: str
    score: float


@app.post("/detect", response_model=LanguageResult)
async def detect_language(request: TextRequest):
    """
    检测文本的语言
    """
    traces = [] 
    if request.model in ('fast-langdetect', 'auto'):
        try:
            # 处理多行文本
            processed_text = request.text.replace("\n", " ")
            result = detector.detect(processed_text, low_memory=request.low_memory)
            return LanguageResult.model_validate(result)
        except DetectError as e:
            raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")
    # 开始使用大模型

    res = await chain_detect.ainvoke(request.text)

# @app.post("/detect-multilingual", response_model=MultiLanguageResponse)
# async def detect_multiple_languages(request: TextRequest):
#     """
#     检测文本中的多种语言
#     """
#     try:
#         # 处理多行文本
#         processed_text = request.text.replace("\n", " ")
#         k = request.k if request.k is not None else 3  # 默认返回前3种语言
#         results = detect_multilingual(processed_text, low_memory=request.low_memory, k=k)
        
#         # 转换结果格式
#         language_results = [LanguageResult.model_validate(item) for item in results]
#         return MultiLanguageResponse(results=language_results)
#     except DetectError as e:
#         raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")

@app.get("/")
async def root():
    return {"message": "欢迎使用语言检测API，访问 /docs 查看文档"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)