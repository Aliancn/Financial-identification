import mimetypes
import os
import fitz  # PyMuPDF
from PIL import Image


def is_pdf(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type == "application/pdf"


def convert_pdf_to_images(pdf_path, output_dir):
    """
    将 PDF 转换为图片，每一页保存为一张图片。
    :param pdf_path: PDF 文件路径。
    :param output_dir: 输出图片的目录。
    :return: 转换后的图片文件路径列表。
    """
    try:
        pdf_document = fitz.open(pdf_path)
        image_paths = []

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            pix = page.get_pixmap()
            output_file = os.path.join(output_dir, f"page_{page_num + 1}.png")
            pix.save(output_file)
            image_paths.append(output_file)
            # print(f"保存图片: {output_file}")

        pdf_document.close()
        return image_paths
    except Exception as e:
        print(f"PDF 转图片失败: {e}")
        return []


def handle_uploaded_file(file_path):
    """
    处理用户上传的文件。如果是 PDF，自动转换成图片。
    :param file_path: 用户上传的文件路径。
    :return: 如果是 PDF 返回图片路径列表，否则返回原始文件路径。
    """
    if is_pdf(file_path):
        print(f"检测到 PDF 文件: {file_path}")
        output_dir = os.path.join(os.path.dirname(file_path), "output_images")
        image_paths = convert_pdf_to_images(file_path, output_dir)
        return image_paths
    else:
        print(f"非 PDF 文件: {file_path}")
        return file_path


def save_and_return_path(res, output_dir, file_prefix):
    """
    保存结果为图片和 JSON，并返回存储的绝对路径。
    :param res: 预测结果对象。
    :param output_dir: 输出目录。
    :param file_prefix: 文件名前缀。
    :return: 一个字典，包含图片和 JSON 文件的绝对路径。
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 构造存储路径
    img_path = os.path.join(output_dir, f"{file_prefix}.jpg")
    json_path = os.path.join(output_dir, f"{file_prefix}.json")
    # 保存文件
    # print(f"保存图片: {img_path}")
    # print(f"保存 JSON: {json_path}")
    # res.save_to_img(img_path)
    res.save_to_json(json_path)

    # 返回存储的绝对路径
    return {"image_path": os.path.abspath(img_path), "json_path": os.path.abspath(json_path)}


