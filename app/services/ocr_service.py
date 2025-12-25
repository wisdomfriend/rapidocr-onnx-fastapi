"""
OCR 业务逻辑服务
"""
import time
import logging
from typing import List, Tuple
import numpy as np
from fastapi import HTTPException

from app.core.lifespan import get_ocr_model
from app.models.schemas import OCRResult
from app.utils.image_utils import decode_base64_image

logger = logging.getLogger(__name__)


def process_ocr_result(ocr_result, return_word_box: bool = False) -> List[OCRResult]:
    """处理OCR结果"""
    if (
        ocr_result is None
        or not isinstance(ocr_result, (list, tuple))
        or len(ocr_result) == 0
        or ocr_result[0] is None
    ):
        return []

    results = []
    for item in ocr_result[0]:  # ocr_result[0]包含检测结果
        if len(item) >= 3:
            bbox = item[0]  # 边界框坐标
            text = item[1]  # 识别的文本
            confidence = item[2]  # 置信度

            results.append(OCRResult(
                text=text,
                confidence=float(confidence),
                bbox=bbox
            ))

    return results


def process_ocr_request(
    image_base64: str,
    use_det: bool = True,
    use_cls: bool = True,
    use_rec: bool = True,
    text_score: float = 0.5,
    box_thresh: float = 0.5,
    unclip_ratio: float = 1.6,
    return_word_box: bool = True
) -> Tuple[List[OCRResult], float, dict]:
    """处理OCR请求的通用函数"""
    start_time = time.time()
    ocr_model = get_ocr_model()

    if ocr_model is None:
        raise HTTPException(500, "OCR model not initialized")

    try:
        # 解码图片
        image = decode_base64_image(image_base64)
        image_size = {"width": image.shape[1], "height": image.shape[0]}

        # 执行OCR
        ocr_result = ocr_model(
            image,
            use_det=use_det,
            use_cls=use_cls,
            use_rec=use_rec,
            text_score=text_score,
            box_thresh=box_thresh,
            unclip_ratio=unclip_ratio,
            return_word_box=return_word_box
        )

        # 处理结果
        results = process_ocr_result(ocr_result, return_word_box)

        total_time = time.time() - start_time
        logger.info(
            f"OCR完成 | 耗时: {total_time:.3f}s | "
            f"图片尺寸: {image_size['width']}x{image_size['height']} | "
            f"识别文本数: {len(results)}"
        )

        return results, total_time, image_size

    except Exception as e:
        logger.exception(f"OCR处理错误: {str(e)}")
        raise HTTPException(500, f"OCR processing error: {str(e)}")


def process_binary_ocr(
    image_bytes: bytes,
    height: int,
    width: int
) -> Tuple[List[OCRResult], float, dict]:
    """处理二进制OCR请求"""
    start_time = time.time()
    ocr_model = get_ocr_model()

    if ocr_model is None:
        raise HTTPException(500, "OCR model not initialized")

    try:
        # 直接使用二进制数据
        img_array = np.frombuffer(image_bytes, dtype=np.uint8).reshape(height, width, 3)

        # 执行OCR
        ocr_result = ocr_model(img_array)

        # 处理结果
        results = process_ocr_result(ocr_result)

        total_time = time.time() - start_time
        logger.info(
            f"Binary OCR完成 | 耗时: {total_time:.3f}s | "
            f"图片尺寸: {width}x{height} | 识别文本数: {len(results)}"
        )

        return results, total_time, {"width": width, "height": height}

    except Exception as e:
        logger.exception(f"Binary OCR处理错误: {str(e)}")
        raise HTTPException(500, f"Binary OCR processing error: {str(e)}")

