from fastapi import FastAPI
from pydantic import BaseModel
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import shutil
import fitz  # PyMuPDF
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import paddlehub as hub
import cv2
import os
import numpy as np
import requests

app = FastAPI()
# 加载模型和 tokenizer
model_id = "Llama3.1-8B-Chinese-Chat"
dtype = torch.float16

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="cuda",
    torch_dtype=dtype,
)
session_history = {}
prompt = """
现在你将接收到增值税发票或火车票的ocr识别内容：
### 增值税发票信息提取
1. **发票基本信息**：
   - 发票代码
   - 发票号码
   - 开票日期
   - 校验码

2. **买方信息**：
   - 名称
   - 纳税人识别号
   - 地址、电话
   - 开户行及账号

3. **销售方信息**：
   - 名称
   - 纳税人识别号
   - 地址、电话
   - 开户行及账号

4. **货物或应税劳务信息**：
   - 项目名称
   - 单位
   - 数量（必须是整数）
   - 单价
   - 金额
   - 税率（百分数形式）
   - 税额

5. **合计金额**：
   - 合计金额
   - 合计税额
   - 价税合计（小写）
   - 价税合计（大写）

6. **其他信息**：
   - 收款人
   - 复核
   - 开票人
   - 审核人

### 火车票信息提取
1. **乘客姓名**：
2. **身份证号**：
3. **出发站**：
4. **到达站**：
5. **车次**：
6. **出发日期**：
7. **出发时间**：
8. **座位信息**：
9. **票价**：
10. **备注**：

### 注意事项
- **增值税发票**：
  - 数量必须是整数。
  - 税率是百分数。
  - 如果某些信息缺失，返回 `null` 或空字符串。

- **火车票**：
  - 出发站和到达站使用中文。

### 输出格式
确保只返回json格式数据即可，不要解释说明例如：

```json
{
  "发票基本信息": {
    "发票代码": "123456789",
    "发票号码": "987654321",
    "开票日期": "2024-05-20",
    "校验码": "ABC123"
  },
  ...
}
```

或者对于火车票：

```json
{
  "乘客姓名": "张三",
  "身份证号": "110101199001011234",
  "出发站": "北京",
  "到达站": "上海",
  "车次": "G123",
  "出发日期": "2024-05-20",
  "出发时间": "08:00",
  "座位信息": "二等座",
  "票价": "500.00",
  "备注": "无"
}
```

请确保按照上述字段格式输出，并将相关的发票信息从文本中提取填充。
"""


# 定义生成回复的函数
def generate_response(input_text: str, system_prompt: str) -> str:
    chat = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": input_text},
    ]

    # 处理输入，将其转换为模型可以接受的格式
    input_ids = tokenizer.apply_chat_template(
        chat, tokenize=True, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)

    # 模型生成
    outputs = model.generate(
        input_ids,
        max_new_tokens=8192,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
    )

    # 解码生成的文本
    response_ids = outputs[0][input_ids.shape[-1]:]
    return tokenizer.decode(response_ids, skip_special_tokens=True)


def multiple_dialogue(input_text: str, system_prompt: str, session_id: str) -> str:
    # 检查会话ID是否存在，如果不存在，初始化会话
    if session_id not in session_history:
        session_history[session_id] = ""

    # 添加用户输入到会话历史
    session_history[session_id] += input_text + "\n"

    chat = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": session_history[session_id]},
    ]

    # 处理输入，将其转换为模型可以接受的格式
    input_ids = tokenizer.apply_chat_template(
        chat, tokenize=True, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)

    # 模型生成
    outputs = model.generate(
        input_ids,
        max_new_tokens=8192,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
    )

    # 解码生成的文本
    response_ids = outputs[0][input_ids.shape[-1]:]
    response_text = tokenizer.decode(response_ids, skip_special_tokens=True)

    # 更新会话历史
    session_history[session_id] += response_text + "\n"

    return response_text


def ocr(img_path, rotate=False, degrees=0):
    if rotate and degrees != 0:

        # 读取图像
        img = cv2.imread(img_path)
        # 获取图像尺寸
        (h, w) = img.shape[:2]
        # 计算旋转矩阵
        center = (w / 2, h / 2)
        M = cv2.getRotationMatrix2D(center, degrees, 1.0)

        # 计算旋转后的图像尺寸
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))

        # 调整旋转矩阵以包含所有内容
        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]

        # 进行旋转
        rotated = cv2.warpAffine(img, M, (new_w, new_h))

        # 保存旋转后的图像
        rotated_path = f"temp_rotated_{img_path}"
        cv2.imwrite(rotated_path, rotated)
        # 使用旋转后的图像进行 OCR
        ocr = hub.Module(name="chinese_ocr_db_crnn_server", enable_mkldnn=True)
        result = ocr.recognize_text(images=[rotated])
        # 清理旋转后的临时图像
        os.remove(rotated_path)
    else:
        # 直接使用原始图像进行 OCR
        result = hub.Module(
            name="chinese_ocr_db_crnn_server", enable_mkldnn=True)
        result = result.recognize_text(images=[cv2.imread(img_path)])
    return result


# 将PDF页面转换为图片
def pdf_to_images(pdf_path):
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        img = page.get_pixmap()
        img_path = f"temp_page_{page.number}.png"
        img.save(img_path)
        images.append(img_path)
    doc.close()
    return images


def list_to_text(result):
    # 初始化一个空字符串用于存储纯文本
    plain_text = ""
    # 遍历OCR结果列表
    for res in result:
        # 确保result_dict是一个字典，并且包含'data'键
        if isinstance(res, dict) and 'data' in res:
            # 遍历每个结果中的'data'列表
            for item in res['data']:
                # 将每个item的'text'添加到纯文本字符串中
                # 可以根据需要在每个文本之间添加空格或换行符
                plain_text += item['text'] + " "
    # 打印出纯文本字符串
    return (plain_text)


@app.post("/ocr/")
async def ocr_endpoint(file: UploadFile = File(...), file_type: str = File(...), rotate: bool = File(...),
                       degrees: int = File(...)):
    # 保存上传的文件
    file_path = f"temp_{file.filename}"
    responses = []
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        if file_type == "image":
            # 直接进行 OCR 处理
            result = ocr(file_path, rotate, degrees)
            plain_text = list_to_text(result)
            response = generate_response(plain_text, prompt)
            responses.append(response)
        elif file_type == "pdf":
            # 将PDF转换为图片并进行OCR处理
            image_paths = pdf_to_images(file_path)
            results = []
            for img_path in image_paths:
                result = ocr(img_path, rotate, degrees)
                results.append(result)
            # 清理临时图片
            for img_path in image_paths:
                os.remove(img_path)
            for res in results:
                plain_text = list_to_text(res)
                response = generate_response(plain_text, prompt)
                responses.append(response)
        else:
            raise HTTPException(
                status_code=400, detail="Unsupported file type")
    finally:
        os.remove(file_path)
    # 返回响应
    return JSONResponse(content=responses)


class RequestData(BaseModel):
    prompt: str
    input_text: str
    session_id: str


@app.post("/generate/")
async def generate(request_data: RequestData):
    response = multiple_dialogue(
        request_data.input_text, request_data.prompt, request_data.session_id)
    return JSONResponse(content={"response": response})


@app.get("/reset/{session_id}")
async def reset_session(session_id: str):
    if session_id in session_history:
        del session_history[session_id]
        return JSONResponse(content={"message": "Session reset"})
    else:
        raise HTTPException(status_code=404, detail="Session not found")
