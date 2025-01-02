import os
from pyzbar.pyzbar import decode
from PIL import Image
from pprint import pprint


def get_image_paths(base_path):
    '''获取当前路径下所有的电子发票图片文件路径'''
    image_paths = []
    file_names = os.listdir(base_path)
    for file_name in file_names:
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_paths.append(os.path.join(base_path, file_name))
    return image_paths


def get_image_path(img_path):
    '''获取当前路径的电子发票图片文件路径'''
    return [img_path]


def extract_qrcode_info(image_path):
    '''提取图片文件中的二维码并识别'''
    img = Image.open(image_path)
    barcodes = decode(img)
    print(barcodes)
    for barcode in barcodes:
        result = barcode.data.decode("utf-8")
        return result
    return None


def process_images(base_path):
    '''处理目录或单张图片路径，识别二维码并输出基本信息'''
    if os.path.isdir(base_path):  # 如果是目录
        image_paths = get_image_paths(base_path)
    elif os.path.isfile(base_path):  # 如果是单个图片文件
        image_paths = get_image_path(base_path)
    else:
        print(f"路径无效: {base_path}")
        return

    for image_path in image_paths:
        result = extract_qrcode_info(image_path)

        if result:
            results = list(result.split(','))
            if len(results) >= 7:  # 确保字段数量足够
                parsed_data = {
                    "invoice_code": results[2],      # 第三字段：发票代码
                    "invoice_num": results[3],   # 第四字段：发票号码
                    "total_amount": results[4],          # 第五字段：金额
                    "invoice_date": results[5],            # 第六字段：时间
                    "check_Code": results[6]        # 第七字段：发票校验码
                }
                print(f"文件: {os.path.basename(image_path)}")
                pprint(parsed_data)
                print("-" * 40)
                return parsed_data
            else:
                print(f"文件: {os.path.basename(image_path)} - 二维码信息不完整")
                print("-" * 40)
        else:
            print(f"文件: {os.path.basename(image_path)} - 未识别到二维码")
