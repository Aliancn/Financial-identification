def normalize_bbox(ocr_results):
    """
    将OCR结果的四个顶点坐标归一化为左上和右下角的bbox形式。
    :param ocr_results: OCR结果 [([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], "文本内容")]
    :return: 格式化后的列表 [{"bbox": [x1, y1, x2, y2], "text": "文本内容"}]
    """
    normalized_results = []
    for coords, text in ocr_results:
        x_coords = [point[0] for point in coords]
        y_coords = [point[1] for point in coords]
        bbox = [min(x_coords), min(y_coords), max(x_coords),
                max(y_coords)]  # [左上x, 左上y, 右下x, 右下y]
        normalized_results.append({"bbox": bbox, "text": text})
    return normalized_results


def remove_noise(normalized_results, keywords=None):
    """
    根据内容过滤噪声字段。
    :param normalized_results: 已归一化的OCR结果 [{"bbox": [...], "text": "文本内容"}]
    :param keywords: 噪声关键词列表，如 ["水印", "背景"]
    :return: 去噪后的字段列表
    """
    if keywords is None:
        keywords = ["水印", "测试", "背景"]

    return [
        item for item in normalized_results
        if item["text"].strip() and all(kw not in item["text"] for kw in keywords)
    ]


def sort_results(normalized_results):
    """
    按坐标排序，先纵向再横向。
    :param normalized_results: 去噪后的OCR结果 [{"bbox": [...], "text": "文本内容"}]
    :return: 排序后的结果
    """
    return sorted(normalized_results, key=lambda x: (x["bbox"][1], x["bbox"][0]))


def merge_fields(sorted_results, x_threshold=20, y_threshold=10):
    """
    合并相邻字段（同一行或同一逻辑字段）。
    :param sorted_results: 排序后的OCR结果 [{"bbox": [...], "text": "文本内容"}]
    :param x_threshold: 同行字段横向间距阈值
    :param y_threshold: 同行纵向间距阈值
    :return: 合并后的字段列表
    """
    merged_results = []
    current_line = []
    prev_bbox = None

    for item in sorted_results:
        if not current_line:
            current_line.append(item)
            prev_bbox = item["bbox"]
            continue

        # 检查是否属于同一行
        if abs(item["bbox"][1] - prev_bbox[1]) <= y_threshold:
            # 检查是否属于同一字段
            if abs(item["bbox"][0] - prev_bbox[2]) <= x_threshold:
                current_line.append(item)
            else:
                # 当前行结束，合并内容
                merged_text = " ".join([i["text"] for i in current_line])
                merged_bbox = [
                    current_line[0]["bbox"][0],  # 左上角x
                    current_line[0]["bbox"][1],  # 左上角y
                    current_line[-1]["bbox"][2],  # 右下角x
                    current_line[-1]["bbox"][3]  # 右下角y
                ]
                merged_results.append(
                    {"bbox": merged_bbox, "text": merged_text})
                current_line = [item]
        else:
            # 不在同一行，合并当前行内容
            merged_text = " ".join([i["text"] for i in current_line])
            merged_bbox = [
                current_line[0]["bbox"][0],
                current_line[0]["bbox"][1],
                current_line[-1]["bbox"][2],
                current_line[-1]["bbox"][3]
            ]
            merged_results.append({"bbox": merged_bbox, "text": merged_text})
            current_line = [item]
        prev_bbox = item["bbox"]

    # 最后一行处理
    if current_line:
        merged_text = " ".join([i["text"] for i in current_line])
        merged_bbox = [
            current_line[0]["bbox"][0],
            current_line[0]["bbox"][1],
            current_line[-1]["bbox"][2],
            current_line[-1]["bbox"][3]
        ]
        merged_results.append({"bbox": merged_bbox, "text": merged_text})

    return merged_results


def group_fields(merged_results):
    """
    按字段逻辑分组。
    :param merged_results: 合并后的OCR结果 [{"bbox": [...], "text": "文本内容"}]
    :return: 按逻辑分组的字段字典
    """
    grouped_data = {
        "基本信息": {},
        "购方信息": {},
        "销方信息": {},
        "商品明细": [],
        "金额信息": {}
    }

    for item in merged_results:
        text = item["text"]
        if "发票代码" in text:
            grouped_data["基本信息"]["发票代码"] = text.split("发票代码")[-1].strip()
        elif "发票号码" in text:
            grouped_data["基本信息"]["发票号码"] = text.split("发票号码")[-1].strip()
        elif "购方" in text:
            grouped_data["购方信息"]["名称"] = text
        elif "销方" in text:
            grouped_data["销方信息"]["名称"] = text
        elif any(keyword in text for keyword in ["金额", "税额", "价税合计"]):
            grouped_data["金额信息"].update({"金额信息": text})
        else:
            grouped_data["商品明细"].append(text)

    return grouped_data


def process(ocr_content):
    normalized = normalize_bbox(ocr_content)
    filtered = remove_noise(normalized)
    sorted_results = sort_results(filtered)
    merged_results = merge_fields(sorted_results)
    grouped_data = group_fields(merged_results)

    print(grouped_data)
