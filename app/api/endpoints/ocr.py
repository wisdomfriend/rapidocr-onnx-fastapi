"""
OCR 相关端点
"""
import logging
import numpy as np
from fastapi import UploadFile, File, Form, HTTPException

from app.models.schemas import (
    OCRRequest, OCRResponse, PaddleOCRRequest, EasyOCRRequest
)
from app.services.ocr_service import (
    process_ocr_request, process_binary_ocr, process_ocr_result
)

logger = logging.getLogger(__name__)


async def ocr_endpoint_v1(request: OCRRequest) -> OCRResponse:
    """V1 OCR端点 - 标准接口"""
    results, total_time, image_size = process_ocr_request(
        request.image,
        request.use_det,
        request.use_cls,
        request.use_rec,
        request.text_score,
        request.box_thresh,
        request.unclip_ratio,
        request.return_word_box
    )

    return OCRResponse(
        success=True,
        results=results,
        processing_time=round(total_time, 4),
        image_size=image_size
    )


async def ocr_endpoint(request: OCRRequest) -> OCRResponse:
    """标准OCR端点"""
    return await ocr_endpoint_v1(request)


async def paddleocr_endpoint(request: PaddleOCRRequest):
    """PaddleOCR兼容接口"""
    results, total_time, image_size = process_ocr_request(
        request.image,
        use_cls=request.use_angle_cls,
        box_thresh=request.det_db_box_thresh,
        unclip_ratio=request.det_db_unclip_ratio
    )

    # 转换为PaddleOCR格式
    paddle_results = []
    for result in results:
        paddle_results.append({
            "text": result.text,
            "confidence": result.confidence,
            "bbox": result.bbox
        })

    return {
        "success": True,
        "results": paddle_results,
        "processing_time": round(total_time, 4),
        "image_size": image_size
    }


async def easyocr_endpoint(request: EasyOCRRequest):
    """EasyOCR兼容接口"""
    results, total_time, image_size = process_ocr_request(
        request.image,
        use_det=True,
        use_cls=True,
        use_rec=True,
        text_score=request.text_threshold
    )

    # 转换为EasyOCR格式
    easyocr_results = []
    for result in results:
        easyocr_results.append([
            result.bbox,  # 边界框
            result.text,  # 文本
            result.confidence  # 置信度
        ])

    return {
        "success": True,
        "results": easyocr_results,
        "processing_time": round(total_time, 4),
        "image_size": image_size
    }


async def binary_ocr_endpoint(
    image_data: UploadFile = File(...),
    height: int = Form(...),
    width: int = Form(...)
) -> OCRResponse:
    """最快的二进制传输OCR接口"""
    from app.core.lifespan import get_ocr_model
    
    ocr_model = get_ocr_model()
    if ocr_model is None:
        raise HTTPException(500, "OCR model not initialized")

    try:
        # 读取二进制数据
        image_bytes = await image_data.read()
        file_size_mb = len(image_bytes) / (1024 * 1024)
        logger.info(f"文件读取完成 | 大小: {file_size_mb:.2f}MB")

        # 处理OCR
        results, total_time, image_size = process_binary_ocr(image_bytes, height, width)

        return OCRResponse(
            success=True,
            results=results,
            processing_time=round(total_time, 4),
            image_size=image_size
        )

    except Exception as e:
        logger.exception(f"Binary OCR处理错误: {str(e)}")
        raise HTTPException(500, f"Binary OCR processing error: {str(e)}")


async def fast_ocr_endpoint(
    image_data: UploadFile = File(...),
    height: int = Form(...),
    width: int = Form(...),
    use_det: bool = Form(True),
    use_cls: bool = Form(True),
    use_rec: bool = Form(True),
    text_score: float = Form(0.5),
    box_thresh: float = Form(0.5),
    unclip_ratio: float = Form(1.6),
    return_word_box: bool = Form(False)
) -> OCRResponse:
    """适配业务调用方法的快速OCR接口"""
    from app.core.lifespan import get_ocr_model
    import numpy as np
    import time
    
    ocr_model = get_ocr_model()
    if ocr_model is None:
        raise HTTPException(500, "OCR model not initialized")

    try:
        start_time = time.time()
        
        # 读取UploadFile的内容
        image_bytes = await image_data.read()

        # 使用调用方式
        img_array = np.frombuffer(image_bytes, dtype=np.uint8).reshape(height, width, 3)

        # 执行OCR
        ocr_result = ocr_model(
            img_array,
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
            f"Fast OCR完成 | 耗时: {total_time:.3f}s | "
            f"图片尺寸: {width}x{height} | 识别文本数: {len(results)}"
        )

        return OCRResponse(
            success=True,
            results=results,
            processing_time=round(total_time, 4),
            image_size={"width": width, "height": height}
        )

    except Exception as e:
        logger.exception(f"Fast OCR处理错误: {str(e)}")
        raise HTTPException(500, f"Fast OCR processing error: {str(e)}")

