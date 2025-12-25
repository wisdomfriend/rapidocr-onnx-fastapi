"""
PDF 处理服务
"""
import logging
import base64
from typing import List, Dict

logger = logging.getLogger(__name__)


def extract_images_from_pdf_bytes(pdf_bytes: bytes) -> List[Dict]:
    """
    从PDF中提取图片
    返回格式: [{"page": 1, "image": bytes, "bbox": (x0, y0, x1, y1), "index": 0}]
    """
    images = []
    try:
        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        for page_num in range(len(doc)):
            page = doc[page_num]
            try:
                # 获取页面上的所有图片信息
                image_list = page.get_image_info()

                for i, img_info in enumerate(image_list):
                    try:
                        # 获取图片边界框
                        bbox = img_info["bbox"]

                        # 检查bbox是否有效
                        if not bbox or len(bbox) != 4:
                            logger.warning(f"页面 {page_num + 1} 图片 {i} bbox无效: {bbox}")
                            continue

                        # 提取图片数据
                        pix = page.get_pixmap(matrix=fitz.Identity, clip=bbox)
                        img_data = pix.tobytes("png")

                        images.append({
                            "page": page_num + 1,
                            "image": img_data,
                            "bbox": bbox,
                            "index": i
                        })
                        logger.info(f"成功提取页面 {page_num + 1} 图片 {i}")

                    except Exception as e:
                        logger.warning(f"页面 {page_num + 1} 图片 {i} 提取失败: {str(e)}")
                        continue

            except Exception as e:
                logger.error(f"处理页面 {page_num + 1} 时出错: {str(e)}")
                continue

        doc.close()
    except Exception as e:
        logger.exception(f"extract_images_from_pdf_bytes error: {str(e)}")
    
    return images


def process_pdf_ocr(
    pdf_bytes: bytes,
    use_det: bool = True,
    use_cls: bool = True,
    use_rec: bool = True,
    text_score: float = 0.5,
    box_thresh: float = 0.5,
    unclip_ratio: float = 1.6,
    return_word_box: bool = False
) -> List[Dict]:
    """
    处理PDF OCR
    返回每页的OCR结果
    """
    from app.services.ocr_service import process_ocr_request
    
    images = extract_images_from_pdf_bytes(pdf_bytes)
    result_pages = []
    
    for image in images:
        # 将图片数据编码为base64
        image_base64 = base64.b64encode(image['image']).decode('utf-8')

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

        result_pages.append({
            "page": image['page'],
            "index": image['index'],
            "result": results,
            "bbox_image": image['bbox'],
            "processing_time": total_time,
            "image_size": image_size
        })
    
    return result_pages

