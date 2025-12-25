"""
健康检查端点
"""
import logging
import onnxruntime as ort
from fastapi import HTTPException

from app.core.lifespan import get_ocr_model

logger = logging.getLogger(__name__)


async def health_check():
    """健康检查端点"""
    ocr_model = get_ocr_model()
    if ocr_model is None:
        raise HTTPException(503, "OCR model not initialized")
    
    return {
        "status": "healthy",
        "model": "PaddleOCRV4",
        "providers": ort.get_available_providers(),
    }


async def root():
    """根端点"""
    return {
        "message": "RapidOCR API Service",
        "version": "1.0.0",
        "endpoints": [
            "/ocr",
            "/v1/ocr",
            "/binary_ocr",
            "/fast_ocr",
            "/paddleocr",
            "/easyocr",
            "/upload",
            "/health"
        ],
        "features": [
            "ROCM GPU support",
            "Multiple OCR API compatibility",
            "Base64 image input",
            "File upload support"
        ]
    }

