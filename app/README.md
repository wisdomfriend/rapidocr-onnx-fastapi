# OCR Service 项目结构

## 目录结构

```
app/
├── __init__.py
├── main.py                 # FastAPI 应用主入口
├── core/                   # 核心模块
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── lifespan.py        # 应用生命周期管理
│   ├── middleware.py      # 中间件
│   └── exceptions.py      # 异常处理
├── models/                 # 数据模型
│   ├── __init__.py
│   └── schemas.py         # Pydantic 模型
├── services/               # 业务逻辑服务层
│   ├── __init__.py
│   ├── ocr_service.py     # OCR 业务逻辑
│   └── pdf_service.py     # PDF 处理服务
├── utils/                  # 工具函数
│   ├── __init__.py
│   └── image_utils.py     # 图片处理工具
└── api/                    # API 路由
    ├── __init__.py
    ├── routes.py          # 路由注册
    └── endpoints/         # API 端点
        ├── __init__.py
        ├── health.py      # 健康检查端点
        ├── ocr.py         # OCR 相关端点
        └── upload.py      # 文件上传端点
```

## 模块说明

### core/ - 核心模块
- **config.py**: 应用配置（从环境变量读取）
- **lifespan.py**: 应用生命周期管理（模型初始化、清理）
- **middleware.py**: HTTP 中间件（请求日志、性能监控）
- **exceptions.py**: 全局异常处理器

### models/ - 数据模型
- **schemas.py**: 所有 Pydantic 数据模型（请求/响应模型）

### services/ - 业务逻辑层
- **ocr_service.py**: OCR 核心业务逻辑
- **pdf_service.py**: PDF 处理业务逻辑

### utils/ - 工具函数
- **image_utils.py**: 图片处理工具函数

### api/ - API 路由层
- **routes.py**: 路由注册和聚合
- **endpoints/**: 各个 API 端点实现

## 设计原则

1. **分层架构**: 严格按照 Controller-Service-Utils 分层
2. **单一职责**: 每个模块只负责一个功能
3. **依赖注入**: 通过函数参数传递依赖，避免全局变量
4. **可测试性**: 业务逻辑与框架解耦，便于单元测试
5. **可扩展性**: 模块化设计，易于添加新功能

## API 接口

### PDF 上传接口

#### 接口地址
```
POST /upload_pdf
```

#### 功能说明
上传 PDF 文件并进行 OCR 识别，支持多页 PDF 文档的批量识别。

#### 请求参数

**文件参数（multipart/form-data）:**
- `file` (required): PDF 文件，支持 `application/pdf` 或 `image/pdf` 类型
- `use_det` (optional, default: `True`): 是否启用文本检测
- `use_cls` (optional, default: `True`): 是否启用文本方向分类
- `use_rec` (optional, default: `True`): 是否启用文本识别
- `text_score` (optional, default: `0.5`): 文本置信度阈值
- `box_thresh` (optional, default: `0.5`): 文本框检测阈值
- `unclip_ratio` (optional, default: `1.6`): 文本框扩展比例
- `return_word_box` (optional, default: `False`): 是否返回单词级别的文本框

#### 文件限制
- **文件类型**: `application/pdf` 或 `image/pdf`
- **最大文件大小**: 10GB

#### 响应格式

**成功响应 (200):**
```json
{
  "success": true,
  "results": [
    {
      "page": 1,
      "index": 0,
      "result": [
        {
          "text": "识别的文本内容",
          "confidence": 0.95,
          "bbox": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        }
      ],
      "bbox_image": [x, y, width, height],
      "processing_time": 0.1234,
      "image_size": {
        "width": 1920,
        "height": 1080
      }
    }
  ]
}
```

**错误响应 (400/500):**
```json
{
  "detail": "错误信息描述"
}
```

#### 使用示例

**cURL:**
```bash
curl -X POST "http://localhost:8000/upload_pdf" \
  -F "file=@document.pdf" \
  -F "use_det=true" \
  -F "use_cls=true" \
  -F "use_rec=true" \
  -F "text_score=0.5" \
  -F "box_thresh=0.5" \
  -F "unclip_ratio=1.6" \
  -F "return_word_box=false"
```

**Python requests:**
```python
import requests

url = "http://localhost:8000/upload_pdf"
files = {"file": open("document.pdf", "rb")}
data = {
    "use_det": True,
    "use_cls": True,
    "use_rec": True,
    "text_score": 0.5,
    "box_thresh": 0.5,
    "unclip_ratio": 1.6,
    "return_word_box": False
}

response = requests.post(url, files=files, data=data)
result = response.json()
```

#### 注意事项
- PDF 文件会被逐页处理，每页的 OCR 结果会单独返回
- 处理时间取决于 PDF 页数和每页的复杂度
- 大文件处理可能需要较长时间，建议设置合适的超时时间

## 使用方式

### 开发环境
```bash
python run.py
```

### 生产环境
```bash
gunicorn -k uvicorn.workers.UvicornWorker app.main:app
```

### Docker
```bash
docker-compose up -d
```

