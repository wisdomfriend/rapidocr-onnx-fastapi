"""
FastAPI 应用主入口
"""
import logging
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.core.logging_config import setup_logging
from app.core.lifespan import lifespan
from app.core.middleware import log_requests_middleware
from app.core.exceptions import (
    not_found_handler,
    global_exception_handler,
    validation_exception_handler
)
from app.api.routes import api_router

# 配置日志
setup_logging()
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="RapidOCR API Service",
    description="High-performance OCR service based on RapidOCR with ROCM support",
    version="1.0.0",
    lifespan=lifespan
)

# 注册中间件
app.middleware("http")(log_requests_middleware)

# 注册异常处理器
app.add_exception_handler(404, not_found_handler)
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# 注册路由
app.include_router(api_router)

