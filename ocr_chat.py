from pprint import pprint
from paddleocr import PaddleOCR
import requests
import json


def req_chat(prompt, content,  history=None, api_url='http://127.0.0.1:6006/api/chat'):
    # 请求数据
    data = {
        "prompt": prompt,
        "content": content,
        "history": [],  # 如果需要，可以传递历史对话记录
    }

    # 设置请求头
    headers = {
        "Content-Type": "application/json"
    }

    # 发送 POST 请求
    try:
        # log
        open('log.txt', 'a').write(f'prompt: {prompt}, content: "{content}"\n')
        response = requests.post(
            api_url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # 检查是否有 HTTP 错误

        # 解析返回数据
        response_data = response.json()['response']
        return response_data

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def ocr2content(img_path):
    # need to run only once to download and load model into memory
    ocr = PaddleOCR(lang='ch')
    content = ""
    result = ocr.ocr(img_path, cls=False)
    for idx in range(len(result)):
        res = result[idx]
        for (bbox, (text, prob)) in res:
            bbox_str = str(bbox)
            text_str = str(text)
            content += f"{bbox_str} {text_str}\n"
    return content


ocr_chat_prompt = """
#### 背景信息：
您需要从发票图像的文本识别结果中提取以下关键信息。以下是目标字段和说明：
- InvoiceNum: 发票号。
- InvoiceDate: 开票日期。
- NoteDrawer: 开票人名称。
- TotalAmount: 发票总金额。
- TotalTax: 发票总税额。
- PurchaserName: 购买方名称。
- PurchaserRegisterNum: 购买方纳税人识别号。
- SellerName: 销售方名称。
- SellerRegisterNum: 销售方纳税人识别号。
- CommodityDetails: 包括发票中商品详情。
输入是由 OCR 输出的文字和坐标列表，如下：
```
[([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], "文本内容")]
```
其中，第一个元素是文本框的四个顶点坐标，第二个元素是识别出的文本内容。
#### 输出要求：
根据输入的位置信息和具体的字段，提取所需信息，输出如下结构化字典：
```
fields = {
    "InvoiceNum": "24422000000113017597",
    "InvoiceDate": "2024年08月30日",
    "NoteDrawer": "开票人姓名",
    "TotalAmount": "1000.00",
    "TotalTax": "100.00",
    "TotalAmountWithTax": "1100.00",
    "SellerName": "销售方名称",
    "SellerRegisterNum": "123456789012345",
    "PurchaserName": "购买方名称",
    "PurchaserRegisterNum": "987654321098765",
    "CommodityDetails": [
        {"Name": "商品1", "Quantity": "2", "UnitPrice": "50.00", "Amount": "100.00"},
        {"Name": "商品2", "Quantity": "1", "UnitPrice": "900.00", "Amount": "900.00"}
    ]
}
```
"""

ocr_chat_prompt_o = """

提取所需信息并填入相应字段，严格按格式输出如下json字典，不要输出多余的信息：
fields = {
    "发票号": "24422000000113017597",
    "开票日期": "2024年08月30日",
    "开票人名称": "张三",
    "发票总金额": "1000.00",
    "发票总税额": "100.00",
    "价税合计": "1100.00",
    "购买方名称。": "购买方名称",
    "购买方纳税人识别号。": "987654321098765",
    "销售方名称": "销售方名称",
    "销售方纳税人识别号。": "123456789012345",
    "商品详情": [
        {"Name": "商品1", "Quantity": "2", "UnitPrice": "50.00", "Amount": "100.00"},
        {"Name": "商品2", "Quantity": "1", "UnitPrice": "900.00", "Amount": "900.00"}
    ]
}
"""


def ocr_chat(img_path):
    content = ocr2content(img_path)
    response = req_chat(content=content, prompt=ocr_chat_prompt_o)
    return response


if __name__ == '__main__':
    img_path = './whu/test2/3.jpg'
    response = ocr_chat(img_path)
    pprint(response)
