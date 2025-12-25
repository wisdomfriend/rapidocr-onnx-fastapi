"""
文件上传端点
"""
import logging
import base64
from fastapi import UploadFile, File, Form, HTTPException

from app.models.schemas import OCRResponse, OCRPDFResponse
from app.services.ocr_service import process_ocr_request
from app.services.pdf_service import process_pdf_ocr
from app.core.config import MAX_FILE_SIZE, ALLOWED_IMAGE_TYPES


logger = logging.getLogger(__name__)


async def upload_file(
    file: UploadFile = File(...),
    use_det: bool = Form(True),
    use_cls: bool = Form(True),
    use_rec: bool = Form(True),
    text_score: float = Form(0.5),
    box_thresh: float = Form(0.5),
    unclip_ratio: float = Form(1.6),
    return_word_box: bool = Form(True)
) -> OCRResponse:
    """文件上传OCR端点"""
    # 检查文件类型
    if not file.content_type or file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            400,
            f"File type not allowed. Allowed types: {ALLOWED_IMAGE_TYPES}, "
            f"this type: {file.content_type}"
        )

    # 检查文件大小
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(400, f"File too large. Max size: {MAX_FILE_SIZE} bytes")

    try:
        # 读取文件内容
        file_content = await file.read()
        image_base64 = base64.b64encode(file_content).decode('utf-8')

        # 处理OCR
        results, total_time, image_size = process_ocr_request(
            image_base64,
            use_det,
            use_cls,
            use_rec,
            text_score,
            box_thresh,
            unclip_ratio,
            return_word_box
        )

        return OCRResponse(
            success=True,
            results=results,
            processing_time=round(total_time, 4),
            image_size=image_size
        )

    except Exception as e:
        logger.exception(f"文件上传OCR错误: {str(e)}")
        raise HTTPException(500, f"File OCR processing error: {str(e)}")


async def upload_file_pdf(
    file: UploadFile = File(...),
    use_det: bool = Form(True),
    use_cls: bool = Form(True),
    use_rec: bool = Form(True),
    text_score: float = Form(0.5),
    box_thresh: float = Form(0.5),
    unclip_ratio: float = Form(1.6),
    return_word_box: bool = Form(True)
) -> OCRPDFResponse:
    """PDF文件上传OCR端点"""
    # 检查文件类型
    if not file.content_type or file.content_type not in ["application/pdf", "image/pdf"]:
        raise HTTPException(
            400,
            f"File type not allowed. Allowed types: ['application/pdf', 'image/pdf'], "
            f"this type: {file.content_type}"
        )

    # 检查文件大小, 最大10G
    if file.size and file.size > 1024 * 1024 * 1024 * 10:
        raise HTTPException(400, f"File too large. Max size: 10GB")

    try:
        # 读取PDF内容
        file_content = await file.read()
        
        # 处理PDF OCR
        result_pages = process_pdf_ocr(
            file_content,
            use_det,
            use_cls,
            use_rec,
            text_score,
            box_thresh,
            unclip_ratio,
            return_word_box
        )

        return OCRPDFResponse(
            success=True,
            results=result_pages
        )
    except Exception as e:
        logger.exception(f"文件上传OCR错误: {str(e)}")
        raise HTTPException(500, f"File OCR processing error: {str(e)}")

