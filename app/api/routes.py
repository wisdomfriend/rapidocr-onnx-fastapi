"""
API 路由注册
"""
from fastapi import APIRouter

from app.api.endpoints import health, ocr, upload

# 创建路由
api_router = APIRouter()

# 注册健康检查路由
api_router.add_api_route("/health", health.health_check, methods=["GET"], tags=["health"])
api_router.add_api_route("/", health.root, methods=["GET"], tags=["health"])

# 注册OCR路由
api_router.add_api_route("/v1/ocr", ocr.ocr_endpoint_v1, methods=["POST"], tags=["ocr"])
api_router.add_api_route("/ocr", ocr.ocr_endpoint, methods=["POST"], tags=["ocr"])
api_router.add_api_route("/paddleocr", ocr.paddleocr_endpoint, methods=["POST"], tags=["ocr"])
api_router.add_api_route("/easyocr", ocr.easyocr_endpoint, methods=["POST"], tags=["ocr"])
api_router.add_api_route("/binary_ocr", ocr.binary_ocr_endpoint, methods=["POST"], tags=["ocr"])
api_router.add_api_route("/fast_ocr", ocr.fast_ocr_endpoint, methods=["POST"], tags=["ocr"])

# 注册文件上传路由
api_router.add_api_route("/upload", upload.upload_file, methods=["POST"], tags=["upload"])
api_router.add_api_route("/upload_pdf", upload.upload_file_pdf, methods=["POST"], tags=["upload"])

