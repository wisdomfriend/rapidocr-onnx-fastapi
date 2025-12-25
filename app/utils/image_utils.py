"""
图片处理工具函数
"""
import base64
import io
import numpy as np
import cv2
from PIL import Image
from fastapi import HTTPException


def decode_base64_image(image_base64: str) -> np.ndarray:
    """解码base64图片"""
    try:
        # 移除可能的data:image/xxx;base64,前缀
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]

        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))

        # 转换为OpenCV格式
        if image.mode != 'RGB':
            image = image.convert('RGB')

        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        return cv_image
    except Exception as e:
        raise HTTPException(400, f"Invalid image format: {str(e)}")

