"""
Pydantic 数据模型
"""
from typing import List, Optional
from pydantic import BaseModel


# OCR 请求和响应模型
class OCRRequest(BaseModel):
    """OCR 请求模型"""
    image: str  # base64编码的图片
    use_det: bool = True
    use_cls: bool = True
    use_rec: bool = True
    text_score: float = 0.5
    box_thresh: float = 0.5
    unclip_ratio: float = 1.6
    return_word_box: bool = False


class OCRResult(BaseModel):
    """OCR 结果模型"""
    text: str
    confidence: float
    bbox: List[List[float]]


class OCRResponse(BaseModel):
    """OCR 响应模型"""
    success: bool
    results: List[OCRResult]
    processing_time: float
    image_size: dict


# PDF OCR 模型
class OCRPDFResult(BaseModel):
    """PDF OCR 结果模型"""
    page: int
    index: int
    result: List[OCRResult]
    bbox_image: List[float]
    processing_time: float
    image_size: dict


class OCRPDFResponse(BaseModel):
    """PDF OCR 响应模型"""
    success: bool
    results: List[OCRPDFResult]


# 兼容 PaddleOCR 的请求模型
class PaddleOCRRequest(BaseModel):
    """PaddleOCR 兼容请求模型"""
    image: str  # base64编码的图片
    use_angle_cls: bool = True  # 检测文本是否倒置（0° 或 180°），并自动校正
    lang: str = "ch"  # 指定语言（如 "ch" 中文、"en" 英文）,实际未使用
    det_db_thresh: float = 0.3  # 控制文本区域检测的敏感度，值越小越敏感
    det_db_box_thresh: float = 0.5  # 过滤低置信度的检测框，值越大越严格
    det_db_unclip_ratio: float = 1.6  # 扩展检测框以包含完整文本，值越大扩展越多
    rec_char_dict_path: Optional[str] = None  # 自定义字符字典（用于特殊字符集）, 实际未使用
    rec_batch_num: int = 6  # 识别模型的批处理大小, 一次处理多少个文本区域，影响速度和内存, 实际未使用
    cls_batch_num: int = 6  # 分类模型的批处理大小, 一次处理多少个文本区域进行方向分类, 实际未使用
    cls_thresh: float = 0.9  # 方向分类的置信度阈值, 判断文本方向分类的置信度，值越大越严格, 实际未使用


# 兼容 EasyOCR 的请求模型
class EasyOCRRequest(BaseModel):
    """EasyOCR 兼容请求模型"""
    image: str  # base64编码的图片
    languages: List[str] = ["ch_sim", "en"]
    gpu: bool = True
    model_storage_directory: Optional[str] = None
    download_enabled: bool = True
    paragraph: bool = False
    contrast_ths: float = 0.1
    adjust_contrast: float = 0.5
    text_threshold: float = 0.7
    link_threshold: float = 0.4
    low_text: float = 0.4
    canvas_size: int = 2560
    mag_ratio: float = 1.0
