from paddleocr import PaddleOCR, draw_ocr
from PIL import Image, ImageOps
import cv2


def crop_invoice(image_path, output_path):
    """
    修改图片大小，使得发票的主题占据主要的页面，减小四周的空白部分
    :param image_path: 输入图片路径
    :param output_path: 输出图片路径
    """
    # 打开图像
    img = Image.open(image_path)

    # 将图像转换为灰度图像
    gray_img = ImageOps.grayscale(img)

    # 获取图像的边界框
    bbox = gray_img.getbbox()

    # 裁剪图像
    cropped_img = img.crop(bbox)

    # 保存裁剪后的图像
    cropped_img.save(output_path)


# 初始化OCR模型
ocr = PaddleOCR(use_angle_cls=True, lang='ch')


def crop_invoice_paddle(image_path, output_path):
    # 读取图片
    img = cv2.imread(image_path)
    width = img.shape[1]
    height = img.shape[0]

    # 进行OCR检测
    result = ocr.ocr(img, cls=True)

    # 获取文本区域的所有边界框
    boxes = [line[0] for line in result[0]]

    # 计算最小的外接矩形
    x_min = int(min(box[0][0] for box in boxes))
    y_min = int(min(box[0][1] for box in boxes))
    x_max = int(max(box[2][0] for box in boxes))
    y_max = int(max(box[2][1] for box in boxes))

    # 裁剪图片
    cropped_img = img[max(y_min-20, 0):min(y_max+20, height),
                      max(x_min-20, 0):min(x_max+20, width)]

    # 保存裁剪后的图片
    cv2.imwrite(output_path, cropped_img)
    print(f"裁剪后的图片已保存到 {output_path}")


if __name__ == '__main__':
    input_image_path = 'path_to_your_invoice_image.png'
    output_image_path = 'path_to_your_output_image.png'
    crop_invoice(input_image_path, output_image_path)
    print(f"裁剪后的图像已保存到 {output_image_path}")
