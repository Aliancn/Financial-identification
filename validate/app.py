from email.mime import image
import json
from math import log
from multiprocessing import process
# from parse_with_json import extract_invoice_fields, find_with_json
from validate.OCR import handle_uploaded_file, save_and_return_path
from validate.QR import process_images

import os
from validate.val_baidu import vaild


def predict(file_path):
    try:
        json_path = None
        # 处理pdf
        file_path = handle_uploaded_file(file_path)
        # logger.info(f"file_path:::::::::::\n {file_path}\n")

        now_path = os.path.dirname(__file__)
        output_dir = os.path.join(now_path, "output")
        # logger.info(f"output_dir:::::::::::\n {output_dir}\n")

        qr_data = process_images(file_path)  # TODO
        check_code = qr_data.get("check_Code")
        if (check_code != ''):
            check_code_last6 = check_code[-6:]  # 获取后六位
        else:
            check_code_last6 = ''
        print("获取字段")
        print(qr_data.get("invoice_code"))
        print(qr_data.get("invoice_num"))
        print(check_code_last6)
        print(qr_data.get("total_amount"))
        responce = vaild(qr_data.get("invoice_code"), qr_data.get("invoice_num"), qr_data.get(
            "invoice_date"), "elec_normal_invoice", check_code_last6, qr_data.get("total_amount"))
        result = json.loads(responce)

        if result.get("VerifyResult") == "0002":
            return {'error': '发票超过识别次数'}
        # logger.info(f"fields:::::::::::\n {fields}\n")
        words_result = result.get("words_result", {})
        fields = {
            "InvoiceNum": "",  # 发票号
            "InvoiceDate": "",  # 发票日期
            "NoteDrawer": "",  # 开票人
            "TotalAmount": "",  # 总金额
            "TotalTax": "",  # 总税额
            "SellerName": "",  # 销售方名称
            "SellerRegisterNum": "",  # 销售方纳税人识别号
            "PurchaserName": "",  # 购买方名称
            "PurchaserRegisterNum": "",  # 购买方纳税人识别号
            "CommodityDetails": [],  # 商品详情
            "Remarks": "",
        }
        commodity_name_list = words_result.get("CommodityName", [])
        fields["InvoiceNum"] = result.get("InvoiceNum")
        fields["InvoiceDate"] = result.get("InvoiceDate")
        fields["NoteDrawer"] = words_result.get("NoteDrawer")
        fields["TotalAmount"] = words_result.get("TotalAmount")
        fields["TotalTax"] = words_result.get("TotalTax")
        fields["SellerName"] = words_result.get("SellerName")
        fields["SellerRegisterNum"] = words_result.get("SellerRegisterNum")
        fields["PurchaserName"] = words_result.get("PurchaserName")
        fields["PurchaserRegisterNum"] = words_result.get(
            "PurchaserRegisterNum")
        fields["Remarks"] = result.get("Remarks")
        fields["CommodityDetails"] = []
        if commodity_name_list and isinstance(commodity_name_list, list):
            for item in commodity_name_list:
                fields["CommodityDetails"].append(item.get("word", ""))
        else:
            # 如果列表为空或不存在，设置默认值
            fields["CommodityDetails"] = []

        print(fields)

        verify = result.get("VerifyResult")
        if verify == "0001":
            return fields
        else:
            return "发票有误"

    except Exception as e:
        print(e)
        return {"error": str(e)}
