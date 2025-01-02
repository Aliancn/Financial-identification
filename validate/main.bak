import os
import fitz
from pyzbar.pyzbar import decode
from PIL import Image

def get_filepath(base_path):
    '''获取当前路径下所有的电子发票pdf文件路径'''
    file_paths = []
    file_names = os.listdir(base_path)
    for file_name in file_names:
        if file_name.endswith('.pdf'):
            file_paths.append(os.path.join(base_path, file_name))
    return file_paths

def rename_pdf(file_paths):
    '''逐一对所有电子发票文件左上角的二维码识别并重命名文件'''
    for file_path in file_paths:
        result = get_qrcode(file_path)
        results = list(result.split(','))
        new_name = results[2] + "_" + results[3] + ".pdf"
        new_file_path = os.path.dirname(file_path) + '\\' + new_name       
        os.rename(file_path, new_file_path)

def get_qrcode(file_path):
    '''提取pdf文件中左上角的二维码并识别'''
    pdfDoc = fitz.open(file_path)
    page = pdfDoc[0]    #只对第一页的二维码进行识别
    rotate = int(0)
    zoom_x = 3.0
    zoom_y = 3.0
    mat = fitz.Matrix(zoom_x, zoom_y).prerotate(rotate)
    rect = page.rect
    mp = rect.tl + (rect.br - rect.tl) * 1 / 5
    clip = fitz.Rect(rect.tl, mp)
    pix = page.getPixmap(matrix=mat, alpha=False, clip=clip)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)  
    barcodes = decode(img)
    for barcode in barcodes:
        result = barcode.data.decode("utf-8")
        return result

if __name__ == '__main__':
    base_path = os.getcwd()
    all_files = get_filepath(base_path)
    rename_pdf(all_files)

