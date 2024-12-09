from PIL import Image, ImageOps, ExifTags
import cv2
import numpy as np
import os


def rotation_exif(image_path, output_path):
    """
    旋转图片，使其变正
    :param image_path: 输入图片路径
    :param output_path: 输出图片路径
    """
    # 打开图像
    img = Image.open(image_path)

    try:
        # 获取图像的 EXIF 信息
        exif = img._getexif()
        if exif is not None:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break

            # 根据 EXIF 信息中的 Orientation 标签旋转图像
            if exif[orientation] == 3:
                img = img.rotate(180, expand=True)
            elif exif[orientation] == 6:
                img = img.rotate(270, expand=True)
            elif exif[orientation] == 8:
                img = img.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # 如果没有 EXIF 信息或无法获取 Orientation 标签，则不进行旋转
        pass

    # 保存旋转后的图像
    rotated_path = os.path.splitext(output_path)[0] + '_rotated.jpg'
    img.save(rotated_path)


def rotation_deg(img_path, output_path, rotate=False, degrees=0):
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
        rotated_path = os.path.splitext(output_path)[0] + '_rotated.jpg'
        cv2.imwrite(rotated_path, rotated)
    else:
        print("未进行旋转")

from paddleocr import PaddleOCR
import cv2
import numpy as np

# 初始化 PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch')  # 启用角度分类

def rotate_invoice_to_correct_orientation(image_path, output_path):
    # 读取图片
    img = cv2.imread(image_path)
    
    # 进行 OCR 检测
    result = ocr.ocr(img, cls=True)

    # 检查方向
    angles = [line[1][1] for line in result[0]]  # 获取所有文本行的角度
    avg_angle = np.mean(angles)  # 计算平均角度

    print(f"检测到平均旋转角度：{avg_angle}°")

    # 判断是否需要旋转
    if abs(avg_angle) > 1:  # 如果角度大于 1 度，进行旋转
        # 计算旋转矩阵
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, -avg_angle, 1.0)
        
        # 旋转图片
        rotated_img = cv2.warpAffine(img, rotation_matrix, (w, h))
        cv2.imwrite(output_path, rotated_img)
        print(f"图片已旋转到正确方向，并保存到：{output_path}")
    else:
        cv2.imwrite(output_path, img)
        print("图片方向已正确，无需旋转，保存原图。")



if __name__ == '__main__':
    input_image_path = 'path_to_your_invoice_image.jpg'
    output_image_path = 'path_to_your_output_image.jpg'
    
    print(f"旋转后的图像已保存到 {output_image_path}")
