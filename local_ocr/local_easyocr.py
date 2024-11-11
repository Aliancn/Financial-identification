import easyocr
# this needs to run only once to load the model into memory
reader = easyocr.Reader(['ch_sim', 'en'])


def get_local_ocr(img_path, detail=0):
    result = reader.readtext(img_path, detail=detail)
    return result


if __name__ == '__main__':
    img_path = '../whu/test/3.jpg'
    result = get_local_ocr(img_path)
    print(result)
