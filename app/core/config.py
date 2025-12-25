"""
OCR服务配置文件
"""
import os

# 文件上传配置
MAX_FILE_SIZE = int(os.getenv("OCR_MAX_FILE_SIZE", "10485760"))  # 10MB, upload_file中使用
ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/jpg", 
    "image/png",
    "image/bmp",
    "image/tiff",
    "image/webp"
]  # upload_file中使用

# 模型预热配置
WARMUP_ENABLED = os.getenv("OCR_WARMUP_ENABLED", "true").lower() == "true"
WARMUP_IMAGE_PATH = os.getenv("OCR_WARMUP_IMAGE_PATH", None)

