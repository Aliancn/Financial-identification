from email.mime import image
import json
from math import log
from multiprocessing import process
from ocr_receipt.parse_with_json import extract_invoice_fields, find_with_json
from ocr_receipt.OCR import handle_uploaded_file, save_and_return_path
from ocr_receipt.QR import process_images
# from parse_with_json import extract_invoice_fields, find_with_json
# from OCR import handle_uploaded_file, save_and_return_path
# from QR import process_images
import os
from paddlex import create_pipeline
from log import logger

# 初始化模型
pipeline = create_pipeline(pipeline="table_recognition")


def predict(file_path):
    try:
        json_path = None
        # 处理pdf
        file_path = handle_uploaded_file(file_path)
        # logger.info(f"file_path:::::::::::\n {file_path}\n")
        
        
        output = pipeline.predict(file_path) # TODO
        # logger.info(f"output:::::::::::\n {output}\n")
        
        now_path = os.path.dirname(__file__)
        output_dir = os.path.join(now_path,"output")
        # logger.info(f"output_dir:::::::::::\n {output_dir}\n")

        # 处理预测结果
        for idx, res in enumerate(output):

            file_prefix = f"result_{idx}"
            paths = save_and_return_path(res, output_dir, file_prefix)
            # logger.info(f"paths:::::::::::\n {paths}\n")

            json_path = paths["json_path"]

            qr_data = process_images(file_path) # TODO
            # logger.info(f"qr_data:::::::::::\n {qr_data}\n")
            
            fields = find_with_json(json_path, qr_data)
            # logger.info(f"fields:::::::::::\n {fields}\n")

            # 如果提取成功，则添加到结果列表
            if fields:
                return fields

    except Exception as e:
        return {"error": str(e)}

    # finally:
        # 删除临时文件
        # if os.path.exists(img_path):
            # os.remove(img_path)
        # if os.path.exists(json_path):
        #     os.remove(json_path)
