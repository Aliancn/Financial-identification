import json
from math import log
from os import getenv
from traceback import print_tb
from matplotlib import category
from numpy import extract
import pandas as pd
import re
from ocr_receipt.app import predict
from log import logger
from dotenv import load_dotenv, find_dotenv
from zhipuai import ZhipuAI
from pprint import pprint

from me_req import req_chat
_ = load_dotenv(find_dotenv())
default_classification_file_path = "./whu/classification_standard.xlsx"

prompt_template = """
你将接收到商品详细信息，并需要将其分类到相应的科目名称中。请确保输出格式为 JSON，并包含以下字段：

- 商品详细信息
- 科目名称（如果有多个科目名称，可以输出多个为数组）
- 理由

示例输入：
商品详细信息：“*电子元件*八通道ADC芯片AD9257S”

示例输出：
```json
{
  "商品详细信息": "*电子元件*八通道ADC芯片AD9257S",
  "科目名称": "商品和服务支出_维修(护)费_设备维修费",
  "理由": [
    "电子元件：这类商品通常用于电子设备的维修或升级。",
    "八通道ADC芯片AD9257S：这是一种特定的电子元件，用于数据采集和转换，常见于各种电子设备和系统中。",
    "因此，将其归类到“设备维修费”科目是合理的，因为这类元件的采购通常与设备的维修、升级或维护相关。",
    "如果该元件是用于特定的科研项目或设备的研发，也可以考虑归类到“商品和服务支出_其他商品和服务支出_小额设备（科研项目）”科目，但基于提供的信息，归类到“设备维修费”更为直接和符合常规分类逻辑。"
  ]
}
请根据以下商品详细信息生成类似的 JSON 输出：
"""

# 加载分类标准


def load_classification_standard(file_path):
    """
    加载发票分类表格，并将其转化为字典或数据框以供后续分类使用。
    """
    classification_df = pd.read_excel(file_path)
    # 修改列名
    classification_df.columns = ["category_id", "category", "items"]
    # 根据实际表格结构选择加载方式
    return classification_df


classification_standard = load_classification_standard(
    default_classification_file_path)


# 构建分类上下文
def build_classification_context(classification_df):
    """
    构建分类的上下文信息，将表格转换为大模型的输入上下文。
    """
    context = ""
    for index, row in classification_df.iterrows():
        # 假设表格中包含 "商品名称" 和 "分类" 列
        context += f"相关对应商品: {row['items']} -> 科目名称: {row['category']}\n"

    prompt = "根据发票上的商品名称，将其分类到相应的科目名称中。\n"
    prompt += context
    return prompt


# 构建分类上下文
context_prompt = build_classification_context(classification_standard)

# 发票分类


def classify_invoice(prompt, commodityDetails):
    """
    根据提取的字段和分类标准，对发票进行分类。
    """
    item = ""
    for commodity in commodityDetails:
        item += commodity + " "
    response = req_chat(prompt, prompt_template + item)
    return response


def extract_json_from_response(response_text):
    """
    从大模型的回答中提取出 JSON 格式的数据。

    参数:
    response_text (str): 大模型的回答文本。

    返回:
    dict: 提取出的 JSON 数据，解析为 Python 字典。
    """
    # 使用正则表达式提取 JSON 部分
    json_pattern = re.compile(r'\{.*?\}', re.DOTALL)
    match = json_pattern.search(response_text)

    if match:
        json_str = match.group(0)
        try:
            # 解析 JSON 字符串为 Python 字典
            json_data = json.loads(json_str)
            return json_data
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}")
            return None
    else:
        print("未找到 JSON 格式的数据")
        return None


# 7. 主流程控制函数
def process_invoice(image_path, classification_file_path=default_classification_file_path):
    """
    主流程控制函数，处理单张发票的所有步骤。
    """

    # OCR 识别
    # ocr_text = perform_ocr(image_path, src="baidu")
    # ocr_text = ocr_chat(image_path)
    ocr_text = predict(image_path)
    logger.info(f"ocr_text:::::::::::\n {ocr_text}\n")

    # 字段提取
    # extracted_fields = extract_fields(ocr_text)
    extracted_fields = ocr_text
    logger.info(f"extracted_fields:::::::::::\n {extracted_fields} \n")

    # 分类
    category_json = []
    category = classify_invoice(
        context_prompt, extracted_fields["CommodityDetails"])
    logger.info(f"category:::::::::::::::\n {category} \n")

    category_json = extract_json_from_response(category)
    logger.info(f"category_json::::::::::::\n {category_json} \n")
    # 返回处理结果
    return {
        "extracted_fields": extracted_fields,
        "category": category_json
    }


def func_ocr(image_path):
    ocr_text = predict(image_path)
    logger.info(f"ocr_text:::::::::::\n {ocr_text}\n")

    return ocr_text


def func_classify(extracted_fields):
    category_json = []
    category = classify_invoice(
        context_prompt, extracted_fields["CommodityDetails"])
    logger.info(f"category:::::::::::::::\n {category} \n")

    category_json = extract_json_from_response(category)
    logger.info(f"category_json::::::::::::\n {category_json} \n")

    return category_json


# 运行示例
if __name__ == "__main__":
    image_path = "./whu/image4.jpg"
    classification_file_path = "./whu/classification_standard.xlsx"
    result = process_invoice(image_path, classification_file_path)
    pprint(result["extracted_fields"])
    pprint(result["category"])
