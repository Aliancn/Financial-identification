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
    for barcode in barcodes:
        result = barcode.data.decode("utf-8")
        return result
    return None

def process_images(image_paths):
    '''逐一处理所有电子发票图片文件，识别二维码并输出基本信息'''
    for image_path in image_paths:
        result = extract_qrcode_info(image_path)
        if result:
            results = list(result.split(','))
            print(f"文件: {os.path.basename(image_path)}")
            pprint(results)
            # 包含的字段：发票代码、（发票号码）、开票日期、校验码、金额
            print("-" * 40)
        else:
            print(f"文件: {os.path.basename(image_path)} - 未识别到二维码")
            print("-" * 40)

if __name__ == '__main__':
    base_path = '../whu/image4.jpg'
    # all_images = get_image_paths(base_path)
    all_images = get_image_path(base_path)
    process_images(all_images)