from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, model_validator
from pydantic import Field as pd_Field
from typing import List, Optional, Literal
from fast_langdetect import detect, detect_multilingual, LangDetector, LangDetectConfig, DetectError
from sqlmodel import SQLModel, create_engine, Session, Column, JSON, Field
from contextlib import asynccontextmanager
from langchain_openai import ChatOpenAI 
from langchain_core.prompts import ChatPromptTemplate 
from datetime import datetime, date
from loguru import logger 
import sys 
import opencc


logger.remove()
logger.add(sys.stdout, backtrace=False)
converter = opencc.OpenCC('t2s.json')
# print(converter.convert('漢字'))  # 汉字)

# 配置检测器
config = LangDetectConfig(
    cache_dir="/app/models",
    allow_fallback=False  # 启用回退到小模型
)
detector = LangDetector(config)

class Response[T](BaseModel):
    code: int = 200
    message: str = "success"
    data: T

from enum  import Enum 

class ModelType(str, Enum):
    FAST_LANGDETECT = 'fast-langdetect'
    AUTO = 'auto'
    LLM = 'llm'

class TextRequest(SQLModel):
    text: str
    model: ModelType = Field(default='fast-langdetect', description="检测模型")
    fast_langdetect_min_score: float | None = Field(default=None, ge=0.0, le=1.0, description="fast-langdetect最小置信度，低于这个值就会用大模型再检测一次")
    trans_code: bool = Field(default=True, description="是否转换语言代码")
    use_project: str | None = Field(default=None, description="使用本项目名称", index=True)
    # 增加一个检测，如果model为auto，那么fast_langdetct_min_score不能为None
    
    model_validator(mode='after')
    def check_fast_langdetect_min_score_when_auto(cls, values):
        if values.model == 'auto' and values.fast_langdetect_min_score is None:
            raise ValueError("当 model 为 'auto' 时，fast_langdetect_min_score 不能为 None")
        return values


class TextTable(TextRequest, table=True):
    id: int | None = Field(default=None, primary_key=True)
    lang_code: str | None = Field(default=None, description="检测到的语言")
    # lang_cn: str | None = Field(default=None, description="检测到的语言中文名")
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    use_model: str | None = None
    time_spend: float | None = None
    traces: list[str] = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.now)
    created_date: date = Field(default_factory=date.today)

class LanguageResult(BaseModel):
    # id: int | None = Field(default=None, primary_key=True)
    lang_code: str | None = Field(default=None, description="检测到的语言")
    lang_cn: str | None = Field(default=None, description="检测到的语言中文名")
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    use_model: str | None = None
    time_spend: float | None = None
    traces: list[str] = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.now)
    # created_date: date = Field(default_factory=date.today)

engine = create_engine("sqlite:////app/volume/dbs/database.db")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI应用的生命周期管理器
    """
    # 创建数据库引擎
    SQLModel.metadata.create_all(engine)
    yield 


app = FastAPI(
    title="语言检测API",
    description="基于fast_langdetect的语言检测服务",
    version="0.0.1",
    lifespan=lifespan,
)

code2lang_dict = {
    'zh-CN': '简体中文',
    'zh-TW': '繁体中文',
    'zh': '繁体中文',
    'cn': '简体中文',
    'en': '英语',
    'fr': '法语',
    'de': '德语',
    'pt': '葡萄牙语',
    'po': '葡萄牙语',  # 别名
    'id': '印尼语',
    'th': '泰语',
    'es': '西班牙语',
    'sp': '西班牙语',  # 别名
    'ru': '俄语',
    'tr': '土耳其语',
    'vi': '越南语',
    'it': '意大利语',
    'ar': '阿拉伯语',
    'ja': '日语',
    'jp': '日语',      # 别名
    'ko': '韩语',
    'kr': '韩语',      # 别名
    'ms': '马来语',
    'pl': '波兰语',
    'nl': '荷兰语',
    'fa': '波斯语',
    'ro': '罗马尼亚语',
    'uk': '乌克兰语',
    'tl': '菲律宾语'
}
code2code_dict = {
    'zh-CN': 'cn',
    'zh-TW': 'zh',
    'zh': 'zh',
    'cn': 'cn',
    'en': 'en',
    'fr': 'fr',
    'de': 'de',
    'pt': 'pt',
    'po': 'pt',  # 别名
    'id': 'id',
    'th': 'th',
    'es': 'es',
    'sp': 'es',  # 别名
    'ru': 'ru',
    'tr': 'tr',
    'vi': 'vi',
    'it': 'it',
    'ar': 'ar',
    'ja': 'ja',
    'jp': 'ja',  # 别名
    'ko': 'ko',
    'kr': 'ko',  # 别名
    'ms': 'ms',
    'pl': 'pl',
    'nl': 'nl',
    'fa': 'fa',
}


prompt_detect = ChatPromptTemplate.from_messages([
    ('system', 'Please help me identify the language of the text enclosed in triple backticks (```) and ignore any HTML content within it, only output the language code according to "ISO 639-1" like "en", no more words, use json format, like {{"lang": "en"}}'),
    ('human', '```{text}```')
])
import os 
model = ChatOpenAI(model=os.getenv("LLM_MODEL", "gpt-4o-mini"), temperature=0.4, max_tokens=10).with_structured_output(method='json_mode')
chain_detect = prompt_detect | model

from typing import Annotated

from typing import Callable, Generator

import asyncio 

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

def get_engine() -> Callable[[], Generator[Session, None, None]]:
    return engine


@app.post("/detect", response_model=Response[LanguageResult])
async def detect_language(
    request: TextRequest,
    engine: Annotated[Callable[[], Generator[Session, None, None]], Depends(get_engine)]
):
    """
    检测文本的语言
    """
    received_time = datetime.now()
    traces = [] 
    finish_flag = False 
    try:
        if request.model in ('fast-langdetect', 'auto'):
            # 处理多行文本
            use_model = 'fast-langdetect'
            traces.append("使用fast-langdetect模型进行检测")
            processed_text = request.text.replace("\n", " ")
            result = detector.detect(processed_text, low_memory=False)
            traces.append(f"检测结果: {result}")
            if request.model == 'fast-langdetect' or result['score'] >= request.fast_langdetect_min_score:
                finish_flag = True
            
        if not finish_flag:
            use_model = 'llm'
            traces.append("使用大模型进行检测")
            async with asyncio.timeout(11):
                result = await chain_detect.ainvoke(request.text)
                traces.append(f"大模型检测结果: {result}")

        # 识别繁体
        if result['lang'].lower() == 'zh':
            if converter.convert(request.text) == request.text:
                result['lang'] = 'cn'
            else:
                result['lang'] = 'zh'
        # 转换
        if request.trans_code:
            result['lang_code'] = code2code_dict.get(result['lang'].lower(), result['lang'].lower())
        else:
            result['lang_code'] = result['lang'].lower()

        data = TextTable(
            **request.model_dump(),
            **result,
            # lang_code=result['lang'],
            use_model=use_model,
            traces=traces,
            created_at=received_time,
            time_spend=(datetime.now() - received_time).total_seconds(),
        )
        rdata = LanguageResult.model_validate(data.model_dump())
        # session: Session
        with Session(engine) as session:
            session.add(data)
            session.commit()
            session.refresh(data)
        rdata.lang_cn = code2lang_dict.get(data.lang_code, "未知语言")  
        raise ValueError("检测失败")
        return Response(data=rdata)

    except Exception as e:
        logger.exception(e)
        traces.append(f"检测失败: {str(e)}")
        with Session(engine) as session:
            data = TextTable(
                **request.model_dump(),
                traces=traces,
                created_at=received_time,
                time_spend=(datetime.now() - received_time).total_seconds(),
            )
            logger.debug(data)
            rdata = LanguageResult.model_validate(data.model_dump())
            session.add(data)
            session.commit()
            session.refresh(data)
        return Response(
            code=500,
            message="检测失败",
            data=rdata
        )
    
from sqlmodel import select 

@app.get('/recent_fails', response_model=Response[List[LanguageResult]])
async def get_recent_fails(
    session: Session = Depends(get_session),
):
    """
    获取最近的失败记录
    """
    stmt = select(TextTable).where(TextTable.lang_code == None).order_by(TextTable.created_at.desc()).limit(10)
    results = session.exec(stmt).all()
    return Response(data=[LanguageResult.model_validate(result.model_dump()) for result in results])

from datetime import timedelta 
from sqlmodel import text 

@app.delete('/delete/month_ago')
async def delete_month_ago(
    session: Session = Depends(get_session),
):
    """
    删除一个月前的记录
    """
    month_ago = (datetime.now() - timedelta(days=30)).strftime('%F')
    stmt = text('DELETE FROM texttable WHERE created_date < :month_ago')
    session.exec(stmt, params={'month_ago': month_ago})
    session.commit()
    return Response(data="删除成功") 

@app.get("/")
async def root():
    return {"message": "欢迎使用语言检测API，访问 /docs 查看文档"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)