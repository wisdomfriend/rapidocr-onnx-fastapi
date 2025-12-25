"""
应用生命周期管理
"""
import os
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from rapidocr_onnxruntime_run import RapidOCR

from app.core.config import (
    WARMUP_ENABLED, WARMUP_IMAGE_PATH
)

logger = logging.getLogger(__name__)

# 全局变量存储OCR模型
ocr_model = None


def get_ocr_model():
    """获取OCR模型实例"""
    global ocr_model
    return ocr_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global ocr_model
    
    logger.info("Initializing OCR model...")
    start_time = time.time()
    
    try:

        ocr_model = RapidOCR()

        # 模型预热
        if WARMUP_ENABLED and WARMUP_IMAGE_PATH and os.path.exists(WARMUP_IMAGE_PATH):
            logger.info("Warming up OCR model...")
            try:
                ocr_model(WARMUP_IMAGE_PATH)
                logger.info("Model warmup completed")
            except Exception as e:
                logger.warning(f"Model warmup failed: {str(e)}")

        logger.info(f"OCR model loaded in {time.time() - start_time:.2f}s")
    except Exception as e:
        logger.exception(f"OCR model initialization failed: {str(e)}")
        raise
    
    yield
    
    # 清理资源
    if ocr_model is not None:
        del ocr_model
        ocr_model = None
        logger.info("OCR model resources released")

