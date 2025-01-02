from pyzbar import pyzbar
from PIL import Image


def parse_invoice_info(picture):
    """
    发票二维码解析，获取关键信息
    :param picture: 发票图片
    :return: dict
    """
    invoice_info = {}
    img = Image.open(picture)
    # 解析二维码的数据
    results = pyzbar.decode(img)

    for result in results:
        text_list = result.data.decode('utf-8').split(',')
        # invoice_info['发票代码'] = text_list[2]
        # invoice_info['发票号码'] = text_list[3]
        # invoice_info['不含税金额'] = text_list[4]
        # invoice_info['开票日期'] = text_list[5]
        # invoice_info['校验码'] = text_list[6]
        invoice_info["result"] = text_list
    return invoice_info


if __name__ == '__main__':
    picture = '../whu/image.png'
    invoice_info = parse_invoice_info(picture)
    print(invoice_info)