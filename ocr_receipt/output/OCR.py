import os
from paddlex import create_pipeline
from ocr_receipt.parse_with_json import find_with_json


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
    res.save_to_img(img_path)


    res.save_to_json(json_path)

    # 返回存储的绝对路径
    return {"image_path": os.path.abspath(img_path), "json_path": os.path.abspath(json_path)}


pipeline = create_pipeline(pipeline="table_recognition")
output = pipeline.predict("/Users/crickzhou/Desktop/10.png")

# 输出目录
output_dir = "./output/"
result_paths = []

# 存储预测结果
for idx, res in enumerate(output):
    file_prefix = f"result_{idx}"
    paths = save_and_return_path(res, output_dir, file_prefix)
    result_paths.append(paths)

# 打印所有结果路径
for idx, paths in enumerate(result_paths):
    print(f"Result {idx}:")
    print(f"  Image Path: {paths['image_path']}")
    print(f"  JSON Path: {paths['json_path']}")

find_with_json(result_paths[0]['json_path'])


