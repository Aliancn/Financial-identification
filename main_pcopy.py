import json
from math import log
import os
from traceback import print_tb
from click import prompt
from matplotlib import category
from numpy import extract
import pandas as pd
import re
from ocr_receipt.app import predict
from log import logger
from dotenv import load_dotenv, find_dotenv
from zhipuai import ZhipuAI
from pprint import pprint
from rag_policy.regular_expression import regex_match
from rag_policy.req import get_policy_prompt
from me_req import req_chat, req_chat_long
from pprint import pprint
_ = load_dotenv(find_dotenv())


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


# 主流程控制函数
def process_invoice(image_path):
    """
    主流程控制函数，处理单张发票的所有步骤。
    """

    # OCR 识别
    ocr_text = predict(image_path)
    # logger.info(f"ocr_text:::::::::::\n {ocr_text}\n")

    # 字段提取
    extracted_fields = ocr_text
    # logger.info(f"extracted_fields:::::::::::\n {extracted_fields} \n")

    # 分类
    coms = extracted_fields["CommodityDetails"]
    # logger.info(f"coms::::::::::::\n {coms} \n")
    com_str = ""
    for com in extracted_fields["CommodityDetails"]:
        com_str += com
    category = regex_match(com_str)
    if category is None:
        logger.info("category is None")

    # prompt
    prompt = get_policy_prompt(
        policy_file_path="./rag_policy/policy.pdf", invoice_info=extracted_fields)

    # ask for llvm
    response = req_chat_long(prompt=prompt)

    # response_json = extract_json_from_response(response)
    # logger.info(f"category_json::::::::::::\n {response_json} \n")
    # 返回处理结果
    return {
        "extracted_fields": extracted_fields,
        "category": category,
        "response": response
    }


# 运行示例
if __name__ == "__main__":
    image_path = "./whu/image.png"
    image_path = os.path.abspath(image_path)
    result = process_invoice(image_path)
    logger.info(f"result::::::::::::\n {result} \n")
    pprint(result)
