import json
import re

# 计算页面宽度


def calculate_page_width(dt_polys):
    all_x_coords = []
    for poly in dt_polys:
        x_coords = [point[0] for point in poly]  # 提取每个点的 x 坐标
        all_x_coords.extend(x_coords)

    page_width = max(all_x_coords) - min(all_x_coords)
    return page_width


def calculate_page_height(dt_polys):
    all_y_coords = []
    for poly in dt_polys:
        y_coords = [point[1] for point in poly]  # 提取每个点的 y 坐标
        all_y_coords.extend(y_coords)

    page_height = max(all_y_coords) - min(all_y_coords)
    return page_height


def extract_invoice_date(texts):

    for text in texts:
        if "开票日期" in text:
            try:
                # 尝试使用正则提取日期
                match = re.search(r"开票日期[:：]?\s*(\d{4}年\d{2}月\d{2}日)", text)
                if match:
                    return match.group(1).strip()
                # 如果正则未匹配，使用分割逻辑
                parts = text.split(":") if ":" in text else text.split("：")
                if len(parts) > 1:
                    return parts[1].strip()
            except Exception as e:
                print(f"Error parsing '开票日期' in text: '{text}', error: {e}")
    return ""


def extract_invoice_number(texts):
    """
    提取发票号码字段，增强健壮性
    :param texts: OCR 识别的文本列表
    :return: 发票号码（如果未找到则返回空字符串）
    """
    for text in texts:
        if "发票号码" in text:
            try:
                # 尝试使用正则提取发票号码
                match = re.search(r"发票号码[:：]?\s*([0-9]+)", text)
                if match:
                    return match.group(1).strip()
                # 如果正则未匹配，使用分割逻辑
                parts = text.split(":") if ":" in text else text.split("：")
                if len(parts) > 1:
                    candidate = parts[1].strip()
                    # 验证是否为纯数字
                    if candidate.isdigit():
                        return candidate
            except Exception as e:
                print(f"Error parsing '发票号码' in text: '{text}', error: {e}")
    return ""

# def clean_and_normalize_text(text):
#     # 构建全角到半角字符的映射表
#     full_to_half = {ord(c): ord(c) - 0xFEE0 for c in "１２３４５６７８９０"}
#     full_to_half[ord('　')] = ord(' ')  # 全角空格 -> 普通空格
#
#     # 替换全角字符，移除不可见字符
#     text = text.translate(full_to_half).replace('\u200B', '').replace('\u200C', '').replace('\u200D', '').replace('\uFEFF', '')
#     return text.strip()


def clean_and_normalize_text(text):
    # 构建全角到半角字符的映射表（包括数字、空格和英文字母）
    full_to_half = {ord(c): ord(
        c) - 0xFEE0 for c in "１２３４５６７８９０ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ"}
    full_to_half[ord('　')] = ord(' ')  # 全角空格 -> 普通空格

    # 替换全角字符，移除不可见字符
    text = text.translate(full_to_half).replace('\u200B', '').replace(
        '\u200C', '').replace('\u200D', '').replace('\uFEFF', '')
    return text.strip()


def is_valid_name(name):
    """
    校验是否为有效的人名：
    - 必须为 2 到 4 个连续汉字。
    """
    return bool(re.match(r"^[\u4e00-\u9fa5]{2,4}$", name))


def extract_note_drawer(texts, dt_polys, page_height):
    """
    提取开票人字段，增强健壮性：
    - 优先在“开票人”本字段中查找人名。
    - 如果未找到有效人名，则在字段坐标范围内查找。
    - 如果范围内未找到，再检查下一个字段是否包含有效人名。

    :param texts: OCR 识别的文本列表。
    :param dt_polys: 每个字段的坐标列表 [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]。
    :param page_height: 页面总高度。
    :return: 开票人名称（如果未找到则返回空字符串）。
    """
    try:
        for i, text in enumerate(texts):
            # 检查字段是否在页面的下半部分
            y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
            x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
            y_center = sum(y_coords) / 2
            x_center = sum(x_coords) / 2
            field_height = abs(y_coords[1] - y_coords[0])
            field_width = abs(x_coords[1] - x_coords[0])

            if y_center <= page_height / 2:
                continue  # 跳过上半部分字段

            # 标准化文本
            normalized_text = text.replace(":", "：").strip()

            # 检查是否包含“开票人”或类似字段
            if any(keyword in normalized_text for keyword in ["开票人", "开票", "票人", "开人"]):
                # # print(f"找到开票人字段: {text}")

                # 优先在当前字段中直接提取人名
                match = re.search(
                    r"(开票人|开票|票人|开人)[：:]?\s*(\S+)", normalized_text)
                if match:
                    candidate = match.group(2).strip()
                    if is_valid_name(candidate):  # 校验人名格式
                        # # print(f"直接从开票人字段提取到名称: {candidate}")
                        return candidate
                    else:
                        print(f"开票人字段中找到无效名称: {candidate}")

                # 如果当前字段未找到有效人名，则在坐标范围内查找
                extended_y_range = (y_center - field_height,
                                    y_center + field_height)
                extended_x_range = (
                    x_center - 1.5 * field_width, x_center + 1.5 * field_width)
                # # print(f"限定范围：y 坐标 {extended_y_range}, x 坐标 {extended_x_range}")

                for j, nearby_text in enumerate(texts):
                    nearby_y_coords = [dt_polys[j][0][1], dt_polys[j][2][1]]
                    nearby_x_coords = [dt_polys[j][0][0], dt_polys[j][1][0]]
                    nearby_y_center = sum(nearby_y_coords) / 2
                    nearby_x_center = sum(nearby_x_coords) / 2

                    # 检查是否在限定范围内
                    if (extended_y_range[0] <= nearby_y_center <= extended_y_range[1] and
                            extended_x_range[0] <= nearby_x_center <= extended_x_range[1]):
                        # 尝试提取范围内字段中的人名
                        nearby_match = re.search(r"^\S+$", nearby_text.strip())
                        if nearby_match:
                            candidate = nearby_match.group(0).strip()
                            if is_valid_name(candidate):
                                # # print(f"从范围内提取到开票人名称: {candidate}")
                                return candidate
                            else:
                                print(f"范围内找到无效名称: {candidate}")

                # 如果范围内未找到，再检查下一个字段
                if i + 1 < len(texts):
                    next_text = texts[i + 1].strip()
                    next_y_coords = [dt_polys[i + 1]
                                     [0][1], dt_polys[i + 1][2][1]]
                    next_y_center = sum(next_y_coords) / 2

                    # 确保下一个字段在页面下半部分
                    if next_y_center > page_height / 2:
                        next_match = re.search(r"^\S+$", next_text)
                        if next_match:
                            candidate = next_match.group(0).strip()
                            if is_valid_name(candidate):
                                # # print(f"从下一个字段提取到开票人名称: {candidate}")
                                return candidate
                            else:
                                print(f"下一个字段找到无效名称: {candidate}")

        # print("未找到符合条件的开票人字段")
        return ""

    except Exception as e:
        # print(f"提取开票人字段时出错: {e}")
        return ""


def is_valid_name(name):
    """
    校验提取的名称是否符合人名格式：
    - 通常为两个或三个汉字。
    - 排除含有明显无关内容（如数字、银行等关键词）。
    :return: 是否为有效名称（布尔值）。
    """
    # 校验是否为 2-3 个汉字
    if not re.match(r"^[\u4e00-\u9fa5]{2,8}$", name):
        return False

    # 排除无关内容
    exclude_keywords = ["银行", "账号", "下载", "次数"]
    for keyword in exclude_keywords:
        if keyword in name:
            return False

    return True


def fullwidth_to_halfwidth(text):

    return "".join(
        chr(ord(char) - 0xFEE0) if 0xFF01 <= ord(char) <= 0xFF5E else char
        for char in text
    ).replace("（", "(").replace("）", ")").replace("：", ":")


# def chinese_price_to_number(chinese_price):
#     """
#     将中文大写总价格转换为数字，先筛选出包含金额单位的字段并清洗。
#     :param chinese_price: str，中文大写金额，如 "壹拾贰圆叁角伍分" 或 "壹拾贰圆整"
#     :return: float，转换后的数字金额
#     """
#     # 定义中文数字与阿拉伯数字的映射
#     chinese_to_arabic = {
#         "零": 0, "壹": 1, "贰": 2, "叁": 3, "肆": 4,
#         "伍": 5, "陆": 6, "柒": 7, "捌": 8, "玖": 9
#     }
#
#     # 定义权值
#     unit_mapping = {"圆": 1, "元": 1, "角": 0.1, "分": 0.01}
#
#     # 筛选出包含金额单位的字段
#     if not re.search(r"[元圆角分整]", chinese_price):
#         raise ValueError(f"未找到金额单位，无法处理: {chinese_price}")
#
#     # 清洗字段：保留中文大写数字和金额单位
#     cleaned_price = re.sub(r"[^\u4e00-\u9fa5元圆角分整]", "", chinese_price)
#     cleaned_price = cleaned_price.replace("元", "圆")  # 统一将“元”替换为“圆”
#
#     # 初始化结果和临时变量
#     total = 0
#     current_unit_value = 1  # 默认是“圆”的值
#     temp_value = 0
#
#     for char in cleaned_price:
#         if char in chinese_to_arabic:
#             # 如果是数字，则更新临时值
#             temp_value = chinese_to_arabic[char]
#         elif char in unit_mapping:
#             # 如果是单位，则将临时值乘以单位权值，并累加到总金额
#             total += temp_value * unit_mapping[char]
#             temp_value = 0  # 重置临时值
#         else:
#             # 如果是无关字符，跳过
#             continue
#
#     return round(total, 2)  # 保留两位小数

# def contains_chinese_price(texts):
#     """
#     检查文本列表中是否包含中文价格字段，包括大写金额格式。
#     :param texts: list of str，包含待检查的字符串
#     :return: bool，是否包含中文价格字段
#     """
#     # 定义中文大写数字和金额单位的正则表达式
#     price_pattern = re.compile(
#         r"[零壹贰叁肆伍陆柒捌玖拾佰仟万亿]*[圆元](整|[零壹贰叁肆伍陆柒捌玖拾佰仟万亿]*[角分])?"
#     )
#
#     # 遍历每个文本，检查是否包含符合中文价格格式的内容
#     for text in texts:
#         if price_pattern.search(text):
#             return True  # 如果找到匹配，立即返回 True
#
#     return False  # 遍历完所有文本，未找到匹配，返回 False


def extract_total_price(texts, dt_polys):
    # if(contains_chinese_price(texts)):
    #     price=chinese_price_to_number(texts)
    #     return price
    # else:
    try:
        total_price = ""
        price_y_coord = None  # 保存 "价税合计（大写）" 的纵坐标范围
        price_height = None  # 保存 "价税合计（大写）" 的字段高度
        texts = [fullwidth_to_halfwidth(text) for text in texts]
        # 遍历文本，找到 "价税合计（大写）" 的纵坐标
        for i, text in enumerate(texts):
            normalized_text = text.replace(":", "：").strip()  # 预处理文本
            if "价税合计" in normalized_text:
                # 获取纵坐标范围 [y1, y3]
                y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
                price_y_coord = (min(y_coords), max(y_coords))
                price_height = price_y_coord[1] - price_y_coord[0]  # 字段高度
                break

        # 如果找到了 "价税合计（大写）"，尝试匹配同一纵坐标范围的价格
        if price_y_coord and price_height:
            extended_y_range = (
                price_y_coord[0] - 0.6 * price_height,
                price_y_coord[1] + 0.6 * price_height,
            )
            # # print(f"扩展后的 y 坐标范围: {extended_y_range}")

            for i, text in enumerate(texts):
                y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
                y_center = sum(y_coords) / 2  # 计算文本中心纵坐标
                if extended_y_range[0] <= y_center <= extended_y_range[1]:
                    # 匹配形如 ￥XX.XX 或 ¥XX.XX 的价格，允许前面没有 ¥ 或 ￥
                    match = re.search(r"([¥￥]?\s*[0-9]+(\.[0-9]{1,2})?)", text)
                    if match:
                        total_price = match.group(1).strip().replace(
                            "¥", "").replace("￥", "")
                        # # print(f"提取到总价格: {total_price}")
                        return total_price

        # 如果位置特征没有找到价格，再尝试直接从 "(小写)" 字段提取
        if not total_price:
            for i, text in enumerate(texts):
                normalized_text = text.replace(":", "：").strip()  # 预处理文本
                if "小写" in normalized_text:
                    # 检查当前字段
                    match = re.search(
                        r"([¥￥]?\s*[0-9]+(\.[0-9]{1,2})?)", normalized_text)
                    if match:
                        total_price = match.group(1).strip().replace(
                            "¥", "").replace("￥", "")
                        # # print(f"提取到总价格（基于小写字段）: {total_price}")
                        return total_price

                    # 如果当前字段无价格，检查下一字段
                    if i + 1 < len(texts):
                        next_text = texts[i + 1].replace(":", "：").strip()
                        match = re.search(
                            r"([¥￥]?\s*[0-9]+(\.[0-9]{1,2})?)", next_text)
                        if match:
                            total_price = match.group(1).strip().replace(
                                "¥", "").replace("￥", "")
                            # # print(f"提取到总价格（基于小写字段的下一字段）: {total_price}")
                            return total_price

        # 如果 "(小写)" 与金额字段分开，还可以检查同一纵坐标下的其他字段
        if not total_price and price_y_coord:
            # # print("未找到符合条件的总价格，尝试匹配 (小写) 邻近字段")
            for i, text in enumerate(texts):
                y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
                y_center = sum(y_coords) / 2  # 计算文本中心纵坐标
                if price_y_coord[0] <= y_center <= price_y_coord[1]:
                    match = re.search(r"([¥￥]?\s*[0-9]+(\.[0-9]{1,2})?)", text)
                    if match:
                        total_price = match.group(1).strip().replace(
                            "¥", "").replace("￥", "")
                        # print(f"提取到总价格（基于邻近字段）: {total_price}")
                        return total_price

        # 未找到总价格
        # print("未找到符合条件的总价格")
        return ""

    except Exception as e:
        # print(f"提取总价格时出错: {e}")
        return ""

# 中英文冒号


def normalize_text(text):
    return text.replace(":", "：").strip()

# def extract_purchaser_name(texts, dt_polys, page_width, page_height):
#     """
#     提取购买方名称：
#     - 字段必须在页面左上半边。
#     - 字段的纵坐标与“购买方”字段的纵坐标差距不大于0.5个“购买方”字段的高度。
#     - 名称字段可能包含“名称：”、“名 称：”或“称：”。
#     - 兼容中英文冒号以及字段中可能出现的空格。
#     """
#     try:
#         # 定位“购买方”字段的纵坐标范围
#         buyer_y_center = None
#         buyer_height = None
#         for i, text in enumerate(texts):
#             # 检查“购买方”三个字是否有至少两个字被识别到
#             if sum([1 for char in "购买方" if char in text]) >= 2:
#                 y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
#                 buyer_y_center = sum(y_coords) / 2
#                 buyer_height = abs(y_coords[1] - y_coords[0])  # 获取“购买方”字段的高度
#                 # print(f"找到“购买方”字段，y 坐标中心: {buyer_y_center}, 高度: {buyer_height}")
#                 break
#
#         # 如果找到“购买方”字段，限制名称字段的纵坐标范围
#         extended_y_range = None
#         if buyer_y_center is not None and buyer_height is not None:
#             extended_y_range = (
#                 buyer_y_center -1.3 * buyer_height,
#                 buyer_y_center + 1.3 * buyer_height
#             )
#             # print(f"扩展后的 y 坐标范围: {extended_y_range}")
#
#         # 遍历文本寻找符合条件的字段
#         for i, text in enumerate(texts):
#             x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
#             y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
#             y_center = sum(y_coords) / 2
#
#             # 限制字段必须在页面左半边
#             if max(x_coords) > page_width *2/ 3:
#                 continue
#
#             # 限制字段必须在页面上半区
#             if y_center > page_height / 2:
#                 continue
#
#             # 如果找到“购买方”，限制名称字段的纵坐标范围
#             if extended_y_range is not None:
#                 if y_center < extended_y_range[0] or y_center > extended_y_range[1]:
#                     continue
#
#             # 使用正则提取名称字段，兼容各种情况
#             normalized_text = text.replace(":", "：").strip()
#             name_match = re.search(r"(名称|名\s*称|称)[：:]?\s*(.+)", normalized_text)
#             if name_match:
#                 purchaser_name = name_match.group(2).strip()
#                 # print(f"提取到购买方名称: {purchaser_name}")
#                 return purchaser_name
#
#         # 如果未找到符合条件的字段，尝试直接寻找包含“名称”、“名 称”或“称”的字段
#         # print("未找到“购买方”字段，尝试直接寻找包含“名称”、“名 称”或“称”的字段")
#         for i, text in enumerate(texts):
#             x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
#             y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
#             y_center = sum(y_coords) / 2
#
#             # 限制字段必须在页面左半边
#             if max(x_coords) > page_width *2/ 3:
#                 continue
#
#             # 限制字段必须在页面上半区
#             if y_center > page_height / 2:
#                 continue
#
#             # 使用正则提取名称字段
#             normalized_text = text.replace(":", "：").strip()
#             name_match = re.search(r"(名称|名\s*称|称)[：:]?\s*(.+)", normalized_text)
#             if name_match:
#                 purchaser_name = name_match.group(2).strip()
#                 # print(f"提取到购买方名称（兜底逻辑）: {purchaser_name}")
#                 return purchaser_name
#
#         # 如果未找到任何字段
#         # print("未找到符合条件的购买方名称")
#         return ""
#
#     except Exception as e:
#         # print(f"提取购买方名称时出错: {e}")
#         return ""


def extract_purchaser_name(texts, dt_polys, page_width, page_height):
    """
    提取购买方名称，增强健壮性：
    - 放宽对“统一社会信用代码/纳税人识别号”的匹配，支持字段中只要包含“社会信用代码”或“纳税人识别号”的至少5个字即可。
    - 改进正则表达式，兼容字段中的空格、全角字符、大小写、中文和英文冒号等。
    """
    try:
        # 定位“购买方”字段的纵坐标范围
        buyer_y_center = None
        buyer_height = None
        for i, text in enumerate(texts):
            # 检查“购买方”三个字是否有至少两个字被识别到
            if sum([1 for char in "购买方" if char in text]) >= 2:
                y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
                buyer_y_center = sum(y_coords) / 2
                buyer_height = abs(y_coords[1] - y_coords[0])  # 获取“购买方”字段的高度
                # # print(f"找到“购买方”字段，y 坐标中心: {buyer_y_center}, 高度: {buyer_height}")
                break

        # 如果找到“购买方”字段，限制名称字段的纵坐标范围
        extended_y_range = None
        if buyer_y_center is not None and buyer_height is not None:
            extended_y_range = (
                buyer_y_center - 1.3 * buyer_height,  # 扩大范围
                buyer_y_center + 1.3 * buyer_height
            )
            # # print(f"扩展后的 y 坐标范围: {extended_y_range}")

        # 遍历文本寻找符合条件的字段
        for i, text in enumerate(texts):
            x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
            y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
            y_center = sum(y_coords) / 2

            # 限制字段必须在页面左半边
            if max(x_coords) > page_width * 2 / 3:
                continue

            # 限制字段必须在页面上半区
            if y_center > page_height / 2:
                continue

            # 如果找到“购买方”，限制名称字段的纵坐标范围
            if extended_y_range is not None:
                if y_center < extended_y_range[0] or y_center > extended_y_range[1]:
                    continue

            # 放宽匹配逻辑：支持“统一社会信用代码/纳税人识别号”超过5个字即可
            normalized_text = text.replace(":", "：").strip()
            if (
                sum([1 for char in "社会信用代码" if char in normalized_text]) >= 5
                or sum([1 for char in "纳税人识别号" if char in normalized_text]) >= 5
            ):
                # # print(f"提取到匹配的字段: {normalized_text}")
                return normalized_text

            # 改进正则提取名称字段，兼容空格、全角字符等
            name_match = re.search(
                r"(名称|名\s*称|称)[：:]?\s*(.+)", normalized_text)
            if name_match:
                purchaser_name = name_match.group(2).strip()
                # print(f"提取到购买方名称: {purchaser_name}")
                return purchaser_name

        # 如果未找到符合条件的字段，打印调试信息
        # print("未找到符合条件的购买方名称，调试字段过滤过程：")
        for i, text in enumerate(texts):
            x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
            y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
            y_center = sum(y_coords) / 2
            # print(f"字段: {text}, x: {x_coords}, y: {y_coords}")

        # print("未找到符合条件的购买方名称")
        return ""

    except Exception as e:
        # print(f"提取购买方名称时出错: {e}")
        return ""


def extract_purchaser_register_num(texts, dt_polys, page_width, page_height):
    """
    提取购买方统一社会信用代码或纳税人识别号：
    - 字段必须在页面左上半边。
    - 字段的纵坐标与“购买方”字段的纵坐标差距不大于0.5个“购买方”字段的高度。
    - 字段可能包含“纳税人识别号：”或“统一社会信用代码/纳税人识别号：”。
    """
    try:
        # 定位“购买方”字段的纵坐标范围
        buyer_y_center = None
        buyer_height = None
        for i, text in enumerate(texts):
            # 检查“购买方”三个字是否有至少两个字被识别到
            if sum([1 for char in "购买方" if char in text]) >= 2:
                y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
                buyer_y_center = sum(y_coords) / 2
                buyer_height = abs(y_coords[1] - y_coords[0])  # 获取“购买方”字段的高度
                # print(f"找到“购买方”字段，y 坐标中心: {buyer_y_center}, 高度: {buyer_height}")
                break

        # 如果找到“购买方”字段，限制识别号字段的纵坐标范围
        extended_y_range = None
        if buyer_y_center is not None and buyer_height is not None:
            extended_y_range = (
                buyer_y_center - 1.3 * buyer_height,
                buyer_y_center + 1.3 * buyer_height
            )
            # print(f"扩展后的 y 坐标范围: {extended_y_range}")

        # 遍历文本寻找符合条件的字段
        for i, text in enumerate(texts):
            x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
            y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
            y_center = sum(y_coords) / 2

            # 限制字段必须在页面左半边
            if max(x_coords) > page_width * 2 / 3:
                continue

            # 限制字段必须在页面上半区
            if y_center > page_height / 2:
                continue

            # 如果找到“购买方”，限制识别号字段的纵坐标范围
            if extended_y_range is not None:
                if y_center < extended_y_range[0] or y_center > extended_y_range[1]:
                    continue

            # 使用正则提取纳税人识别号或统一社会信用代码，兼容各种情况
            normalized_text = text.replace(":", "：").strip()
            num_match = re.search(
                r"(统一社会信用代码|纳税人识别号)[/／]?(纳税人识别号)?[：:]?\s*(.+)", normalized_text)
            if num_match:
                purchaser_register_num = num_match.group(3).strip()
                cleaned_register_num = purchaser_register_num.replace(
                    " ", "")  # 去掉字段中所有空格
                # print(f"提取到购买方纳税人识别号: {cleaned_register_num}")
                return clean_and_normalize_text(cleaned_register_num)

        # 如果未找到符合条件的字段，尝试直接寻找包含“纳税人识别号”或“统一社会信用代码”的字段
        # print("未找到“购买方”字段，尝试直接寻找包含“纳税人识别号”或“统一社会信用代码”的字段")
        for i, text in enumerate(texts):
            x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
            y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
            y_center = sum(y_coords) / 2

            # 限制字段必须在页面左半边
            if max(x_coords) > page_width * 2 / 3:
                continue

            # 限制字段必须在页面上半区
            if y_center > page_height / 2:
                continue

            # 使用正则提取纳税人识别号或统一社会信用代码
            normalized_text = text.replace(":", "：").strip()
            num_match = re.search(
                r"(统一社会信用代码|纳税人识别号)[/／]?(纳税人识别号)?[：:]?\s*(.+)", normalized_text)
            if num_match:
                purchaser_register_num = num_match.group(3).strip()
                cleaned_register_num = purchaser_register_num.replace(
                    " ", "")  # 去掉字段中所有空格
                # print(f"提取到购买方纳税人识别号（兜底逻辑）: {cleaned_register_num}")
                return clean_and_normalize_text(cleaned_register_num)

        # 如果未找到任何字段
        # print("未找到符合条件的购买方纳税人识别号")
        return ""

    except Exception as e:
        # print(f"提取购买方纳税人识别号时出错: {e}")
        return ""


def extract_seller_name(texts, dt_polys, page_width, page_height):
    """
    提取销售方名称：
      - 横坐标 > 1/3 * page_width 且纵坐标 < 1/2 * page_height，或者
      - 横坐标 < 2/3 * page_width 且纵坐标 > 1/2 * page_height。
    - 字段的纵坐标必须与“销售方”字段相近（差距不超过0.5倍字段高度）。
    - 支持“名称：”、“名 称：”或“称：”的字段。
    - 兼容中英文冒号以及字段中可能出现的空格。
    """
    try:
        # 定位“销售方”字段的纵坐标范围
        seller_y_center = None
        seller_height = None
        for i, text in enumerate(texts):
            # 检查“销售方”三个字是否有至少两个字被识别到
            if sum([1 for char in "销售方" if char in text]) >= 2:
                y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
                seller_y_center = sum(y_coords) / 2
                seller_height = abs(y_coords[1] - y_coords[0])  # 获取“销售方”字段的高度
                # print(f"找到“销售方”字段，y 坐标中心: {seller_y_center}, 高度: {seller_height}")
                break

        # 如果找到“销售方”字段，限制目标字段的纵坐标范围
        extended_y_range = None
        if seller_y_center is not None and seller_height is not None:
            extended_y_range = (
                seller_y_center - 1.3 * seller_height,
                seller_y_center + 1.3 * seller_height
            )
            # print(f"扩展后的 y 坐标范围: {extended_y_range}")

        # 遍历文本寻找符合条件的字段
        for i, text in enumerate(texts):
            x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
            y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
            x_center = sum(x_coords) / 2
            y_center = sum(y_coords) / 2

            # 限制字段的位置
            if not (
                (x_center > page_width / 3 and y_center < page_height / 2) or
                (x_center < page_width * 2 / 3 and y_center > page_height / 2)
            ):
                continue

            # 限制字段的纵坐标必须与“销售方”字段相近
            if extended_y_range is not None:
                if y_center < extended_y_range[0] or y_center > extended_y_range[1]:
                    continue

            # 使用正则提取名称字段，兼容各种情况
            normalized_text = text.replace(":", "：").strip()
            name_match = re.search(
                r"(名称|名\s*称|称)[：:]?\s*(.+)", normalized_text)
            if name_match:
                seller_name = name_match.group(2).strip()
                # print(f"提取到销售方名称: {seller_name}")
                return seller_name

        # 如果未找到符合条件的字段，尝试直接寻找包含“名称”、“名 称”或“称”的字段
        # print("未找到符合条件的销售方字段，尝试直接寻找包含“名称”、“名 称”或“称”的字段")
        for i, text in enumerate(texts):
            x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
            y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
            x_center = sum(x_coords) / 2
            y_center = sum(y_coords) / 2

            # 限制字段的位置
            if not (
                (x_center > page_width / 3 and y_center < page_height / 2) or
                (x_center < page_width * 2 / 3 and y_center > page_height / 2)
            ):
                continue

            # 使用正则提取名称字段
            normalized_text = text.replace(":", "：").strip()
            name_match = re.search(
                r"(名称|名\s*称|称)[：:]?\s*(.+)", normalized_text)
            if name_match:
                seller_name = name_match.group(2).strip()
                # print(f"提取到销售方名称（兜底逻辑）: {seller_name}")
                return seller_name

        # 如果未找到任何字段
        # print("未找到符合条件的销售方名称")
        return ""

    except Exception as e:
        # print(f"提取销售方名称时出错: {e}")
        return ""


def extract_seller_register_num(texts, dt_polys, page_width, page_height):
    """
    提取销售方统一社会信用代码或纳税人识别号：
    - 字段必须在页面右上或左下：
      - 横坐标 > 1/3 * page_width 且纵坐标 < 1/2 * page_height，或者
      - 横坐标 < 2/3 * page_width 且纵坐标 > 1/2 * page_height。
    - 字段的纵坐标必须与“销售方”字段相近（差距不超过0.5倍字段高度）。
    - 支持“纳税人识别号：”或“统一社会信用代码/纳税人识别号：”。
    - 兼容中英文冒号以及字段中可能出现的空格。
    """
    try:
        # 定位“销售方”字段的纵坐标范围
        seller_y_center = None
        seller_height = None
        for i, text in enumerate(texts):
            # 检查“销售方”三个字是否有至少两个字被识别到
            if sum([1 for char in "销售方" if char in text]) >= 2:
                y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
                seller_y_center = sum(y_coords) / 2
                seller_height = abs(y_coords[1] - y_coords[0])  # 获取“销售方”字段的高度
                # print(f"找到“销售方”字段，y 坐标中心: {seller_y_center}, 高度: {seller_height}")
                break

        # 如果找到“销售方”字段，限制目标字段的纵坐标范围
        extended_y_range = None
        if seller_y_center is not None and seller_height is not None:
            extended_y_range = (
                seller_y_center - 1.3 * seller_height,
                seller_y_center + 1.3 * seller_height
            )
            # print(f"扩展后的 y 坐标范围: {extended_y_range}")

        # 遍历文本寻找符合条件的字段
        for i, text in enumerate(texts):
            x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
            y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
            x_center = sum(x_coords) / 2
            y_center = sum(y_coords) / 2

            # 限制字段的位置
            if not (
                (x_center > page_width / 2 and y_center < page_height / 2) or
                (x_center < page_width * 2 / 3 and y_center > page_height / 2)
            ):
                continue

            # 限制字段的纵坐标必须与“销售方”字段相近
            if extended_y_range is not None:
                if y_center < extended_y_range[0] or y_center > extended_y_range[1]:
                    continue

            # 使用正则提取纳税人识别号或统一社会信用代码，兼容各种情况
            normalized_text = text.replace(":", "：").strip()
            num_match = re.search(
                r"(统一社会信用代码|纳税人识别号)[/／]?(纳税人识别号)?[：:]?\s*(.+)", normalized_text)
            if num_match:
                seller_register_num = num_match.group(3).strip()
                cleaned_register_num = seller_register_num.replace(
                    " ", "")  # 去掉字段中所有空格
                # print(f"提取到销售方纳税人识别号: {cleaned_register_num}")
                return clean_and_normalize_text(cleaned_register_num)

        # 如果未找到符合条件的字段，尝试直接寻找包含“纳税人识别号”或“统一社会信用代码”的字段
        # print("未找到符合条件的销售方字段，尝试直接寻找包含“纳税人识别号”或“统一社会信用代码”的字段")
        for i, text in enumerate(texts):
            x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
            y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
            x_center = sum(x_coords) / 2
            y_center = sum(y_coords) / 2

            # 限制字段的位置
            if not (
                (x_center > page_width / 3 and y_center < page_height / 2) or
                (x_center < page_width * 2 / 3 and y_center > page_height / 2)
            ):
                continue

            # 使用正则提取纳税人识别号或统一社会信用代码
            normalized_text = text.replace(":", "：").strip()
            num_match = re.search(
                r"(统一社会信用代码|纳税人识别号)[/／]?(纳税人识别号)?[：:]?\s*(.+)", normalized_text)
            if num_match:
                seller_register_num = num_match.group(3).strip()
                cleaned_register_num = seller_register_num.replace(
                    " ", "")  # 去掉字段中所有空格
                # print(f"提取到销售方纳税人识别号（兜底逻辑）: {cleaned_register_num}")
                return clean_and_normalize_text(cleaned_register_num)

        # 如果未找到任何字段
        # print("未找到符合条件的销售方纳税人识别号")
        return ""

    except Exception as e:
        # print(f"提取销售方纳税人识别号时出错: {e}")
        return ""

# def extract_total_amount_without_tax(texts, dt_polys, page_height):
#     """
#     提取合计金额的内容，增强健壮性：
#     - 横坐标范围放宽到“金额”字段的范围 ±2 倍金额宽度。
#     - 纵坐标范围放宽到与“合计”字段的纵坐标中心 ±1.5 合计字段的高度。
#     - 处理“金”“额”可能被分开识别的情况。
#     - 如果找不到“金额”字段，用与“合计”字段同一行的下一个以 ¥ 或 ￥ 开头的字段作为总金额。
#     """
#     try:
#         # 找到“金额”列的 x 坐标范围
#         amount_column_x = None
#         amount_width = None
#         for i, text in enumerate(texts):
#             if "金额" in text:
#                 x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
#                 amount_column_x = (min(x_coords), max(x_coords))
#                 amount_width = abs(x_coords[1] - x_coords[0])  # 计算金额列宽度
#                 # print(f"找到金额列，x 坐标范围: {amount_column_x}, 列宽: {amount_width}")
#                 break
#
#         # 如果没有找到完整的“金额”，检查分开的“金”和“额”
#         if not amount_column_x:
#             for i, text in enumerate(texts):
#                 if "金" in text:
#                     for j, next_text in enumerate(texts):
#                         if "额" in next_text:
#                             # 检查“金”和“额”是否在同一水平线
#                             y_coords_1 = [dt_polys[i][0][1], dt_polys[i][2][1]]
#                             y_coords_2 = [dt_polys[j][0][1], dt_polys[j][2][1]]
#                             y_center_1 = sum(y_coords_1) / 2
#                             y_center_2 = sum(y_coords_2) / 2
#                             if abs(y_center_1 - y_center_2) < 20:  # 容差范围
#                                 x_coords = [dt_polys[i][0][0], dt_polys[j][1][0]]
#                                 amount_column_x = (min(x_coords), max(x_coords))
#                                 amount_width = abs(amount_column_x[1] - amount_column_x[0])  # 计算列宽度
#                                 # print(f"找到分开的“金”“额”字段，x 坐标范围: {amount_column_x}, 列宽: {amount_width}")
#                                 break
#                 if amount_column_x:
#                     break
#
#         # 如果仍未找到“金额”字段，则退出
#         if not amount_column_x:
#             # print("未找到金额列，尝试使用合计字段的逻辑定位")
#             extended_x_range = None  # 如果没有金额列，暂时不设置 x 范围
#         else:
#             # 横坐标范围放宽 ±2 倍金额列宽
#             extended_x_range = (amount_column_x[0] - 2 * amount_width, amount_column_x[1] + 2 * amount_width)
#             # print(f"扩展后的 x 坐标范围: {extended_x_range}")
#
#         # 尝试找到“合计”或“合”“计”分开识别的字段的 y 坐标
#         total_y = None
#         total_height = None
#         total_x_end = None
#         for i, text in enumerate(texts):
#             normalized_text = text.replace(":", "：").strip()
#             # 确保在页面的下半区
#             y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
#             y_center = sum(y_coords) / 2
#             height = abs(y_coords[1] - y_coords[0])  # 合计字段的高度
#             if y_center <= page_height / 2:  # 判断是否在页面下半区
#                 continue
#
#             if "合计" in normalized_text:
#                 total_y = y_center
#                 total_height = height
#                 total_x_end = max([dt_polys[i][1][0], dt_polys[i][2][0]])  # 合计字段的右边 x 坐标
#                 # print(f"找到合计字段，y 坐标: {total_y}, 高度: {total_height}, x 坐标结束: {total_x_end}")
#                 break
#             elif "合" in normalized_text:
#                 # 检查是否存在“计”且与“合”在同一水平线上
#                 for j, next_text in enumerate(texts):
#                     next_y_coords = [dt_polys[j][0][1], dt_polys[j][2][1]]
#                     next_y_center = sum(next_y_coords) / 2
#                     if "计" in next_text and abs(next_y_center - y_center) < 20:
#                         total_y = y_center
#                         total_height = height
#                         total_x_end = max([dt_polys[j][1][0], dt_polys[j][2][0]])  # 合计字段的右边 x 坐标
#                         # print(f"找到分开的“合计”字段，y 坐标: {total_y}, 高度: {total_height}, x 坐标结束: {total_x_end}")
#                         break
#             if total_y:
#                 break
#
#         if total_y is None or total_height is None:
#             # print("未找到合计字段，无法提取合计金额")
#             return ""
#
#         # 纵坐标范围放宽 ±1.5 倍合计字段高度
#         tolerance_factor = 1.5
#         extended_y_range = (total_y - total_height * tolerance_factor, total_y + total_height * tolerance_factor)
#         # print(f"扩展后的 y 坐标范围: {extended_y_range}")
#
#         # 遍历所有文本，寻找金额内容
#         for i, text in enumerate(texts):
#             x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
#             y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
#             y_center = sum(y_coords) / 2
#
#             # 如果有金额列，检查是否在金额列范围内
#             if extended_x_range:
#                 if x_coords[0] < extended_x_range[0] or x_coords[1] > extended_x_range[1]:
#                     continue
#
#             # 检查 y 坐标是否在扩展的纵坐标范围内
#             if y_center < extended_y_range[0] or y_center > extended_y_range[1]:
#                 continue
#
#             # 使用正则表达式提取金额
#             amount_match = re.search(r"[¥￥]\s*(\d+\.\d+)", text)
#             if amount_match:
#                 total_amount = amount_match.group(1).strip()
#                 # print(f"提取到合计金额: {total_amount}")
#                 return total_amount
#
#         # 如果找不到金额，寻找“合计”字段右侧的第一个金额字段
#         # print("未找到符合条件的合计金额，尝试寻找“合计”字段右侧的金额")
#         if total_x_end:
#             for i, text in enumerate(texts):
#                 x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
#                 y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
#                 y_center = sum(y_coords) / 2
#
#                 # 检查 y 坐标是否在扩展的纵坐标范围内
#                 if y_center < extended_y_range[0] or y_center > extended_y_range[1]:
#                     continue
#
#                 # 检查是否在合计字段右侧
#                 if x_coords[0] > total_x_end:
#                     # 使用正则表达式提取金额
#                     amount_match = re.search(r"[¥￥]\s*(\d+\.\d+)", text)
#                     if amount_match:
#                         total_amount = amount_match.group(1).strip()
#                         # print(f"从“合计”字段右侧提取到金额: {total_amount}")
#                         return total_amount
#
#         # print("未找到任何金额字段")
#         return ""
#
#     except Exception as e:
#         # print(f"提取合计金额时出错: {e}")
#         return ""


def extract_total_amount_without_tax(texts, dt_polys, page_height):
    """
    提取合计金额的内容，增强健壮性：
    - 横坐标范围放宽到“金额”字段的范围 ±2 倍金额宽度。
    - 纵坐标范围放宽到与“合计”字段的纵坐标中心 ±1.5 合计字段的高度。
    - 处理“金”“额”可能被分开识别的情况。
    - 如果找不到“金额”字段，用与“合计”字段同一行的下一个以 ¥ 或 ￥ 开头的字段作为总金额。
    - 如果找不到“合计”字段，则定位“价税合计”字段，找到其纵坐标后向上扩展2倍行距，再放宽1倍行距范围查找。
    - 避免“价税合计”字段被误识别为“合计”。
    """
    try:
        # 找到“金额”列的 x 坐标范围
        amount_column_x = None
        amount_width = None
        for i, text in enumerate(texts):
            if "金额" in text:
                x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
                amount_column_x = (min(x_coords), max(x_coords))
                amount_width = abs(x_coords[1] - x_coords[0])  # 计算金额列宽度
                # print(f"找到金额列，x 坐标范围: {amount_column_x}, 列宽: {amount_width}")
                break

        # 如果没有找到完整的“金额”，检查分开的“金”和“额”
        if not amount_column_x:
            for i, text in enumerate(texts):
                if "金" in text:
                    for j, next_text in enumerate(texts):
                        if "额" in next_text:
                            # 检查“金”和“额”是否在同一水平线
                            y_coords_1 = [dt_polys[i][0][1], dt_polys[i][2][1]]
                            y_coords_2 = [dt_polys[j][0][1], dt_polys[j][2][1]]
                            y_center_1 = sum(y_coords_1) / 2
                            y_center_2 = sum(y_coords_2) / 2
                            if abs(y_center_1 - y_center_2) < 20:  # 容差范围
                                x_coords = [dt_polys[i][0]
                                            [0], dt_polys[j][1][0]]
                                amount_column_x = (
                                    min(x_coords), max(x_coords))
                                amount_width = abs(
                                    amount_column_x[1] - amount_column_x[0])  # 计算列宽度
                                # print(f"找到分开的“金”“额”字段，x 坐标范围: {amount_column_x}, 列宽: {amount_width}")
                                break
                if amount_column_x:
                    break

        # 如果仍未找到“金额”字段，则退出
        if not amount_column_x:
            # print("未找到金额列，尝试使用合计字段的逻辑定位")
            extended_x_range = None  # 如果没有金额列，暂时不设置 x 范围
        else:
            # 横坐标范围放宽 ±2 倍金额列宽
            extended_x_range = (
                amount_column_x[0] - 2 * amount_width, amount_column_x[1] + 2 * amount_width)
            # print(f"扩展后的 x 坐标范围: {extended_x_range}")

        # 尝试找到“合计”或“合”“计”分开识别的字段的 y 坐标
        total_y = None
        total_height = None
        total_x_end = None
        for i, text in enumerate(texts):
            normalized_text = text.replace(":", "：").strip()
            # 确保在页面的下半区
            y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
            y_center = sum(y_coords) / 2
            height = abs(y_coords[1] - y_coords[0])  # 合计字段的高度
            if y_center <= page_height / 2:  # 判断是否在页面下半区
                continue

            # 确保合计字段不被误识别为“价税合计”
            if "合计" == normalized_text and "价税合计" not in text:
                total_y = y_center
                total_height = height
                total_x_end = max(
                    [dt_polys[i][1][0], dt_polys[i][2][0]])  # 合计字段的右边 x 坐标
                # print(f"找到合计字段，y 坐标: {total_y}, 高度: {total_height}, x 坐标结束: {total_x_end}")
                break
            elif "合" == normalized_text:
                # 检查是否存在“计”且与“合”在同一水平线上
                for j, next_text in enumerate(texts):
                    next_y_coords = [dt_polys[j][0][1], dt_polys[j][2][1]]
                    next_y_center = sum(next_y_coords) / 2
                    if "计" == next_text.strip() and abs(next_y_center - y_center) < 30:
                        total_y = y_center
                        total_height = height
                        total_x_end = max(
                            [dt_polys[j][1][0], dt_polys[j][2][0]])  # 合计字段的右边 x 坐标
                        # print(f"找到分开的“合计”字段，y 坐标: {total_y}, 高度: {total_height}, x 坐标结束: {total_x_end}")
                        break
            if total_y:
                break

        # 如果未找到“合计”，尝试寻找“价税合计”字段
        if total_y is None or total_height is None:
            # print("未找到合计字段，尝试定位“价税合计”字段")
            for i, text in enumerate(texts):
                if len([ch for ch in "价税合计" if ch in text]) >= 3:  # 匹配至少3个字
                    y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
                    total_y = sum(y_coords) / 2
                    total_height = abs(y_coords[1] - y_coords[0])
                    # print(f"找到“价税合计”字段，y 坐标: {total_y}, 高度: {total_height}")
                    total_y -= 2 * total_height  # 减去2倍行距
                    break

        if total_y is None or total_height is None:
            # print("未找到合计字段或价税合计字段，无法提取合计金额")
            return ""

        # 纵坐标范围放宽 ±1.5 倍合计字段高度
        tolerance_factor = 1.5
        extended_y_range = (total_y - total_height * tolerance_factor,
                            total_y + total_height * tolerance_factor)
        # print(f"扩展后的 y 坐标范围: {extended_y_range}")

        # 遍历所有文本，寻找金额内容
        for i, text in enumerate(texts):
            x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
            y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
            y_center = sum(y_coords) / 2

            # 如果有金额列，检查是否在金额列范围内
            if extended_x_range:
                if x_coords[0] < extended_x_range[0] or x_coords[1] > extended_x_range[1]:
                    continue

            # 检查 y 坐标是否在扩展的纵坐标范围内
            if y_center < extended_y_range[0] or y_center > extended_y_range[1]:
                continue

            # 使用正则表达式提取金额
            amount_match = re.search(r"[¥￥]\s*(\d+\.\d+)", text)
            if amount_match:
                total_amount = amount_match.group(1).strip()
                # print(f"提取到合计金额: {total_amount}")
                return total_amount

        # 如果找不到金额，寻找“合计”字段右侧的第一个金额字段
        # print("未找到符合条件的合计金额，尝试寻找“合计”字段右侧的金额")
        if total_x_end:
            for i, text in enumerate(texts):
                x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
                y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
                y_center = sum(y_coords) / 2

                # 检查 y 坐标是否在扩展的纵坐标范围内
                if y_center < extended_y_range[0] or y_center > extended_y_range[1]:
                    continue

                # 检查是否在合计字段右侧
                if x_coords[0] > total_x_end:
                    # 使用正则表达式提取金额
                    amount_match = re.search(r"[¥￥]\s*(\d+\.\d+)", text)
                    if amount_match:
                        total_amount = amount_match.group(1).strip()
                        # print(f"从“合计”字段右侧提取到金额: {total_amount}")
                        return total_amount

        # print("未找到任何金额字段")
        return ""

    except Exception as e:
        # print(f"提取合计金额时出错: {e}")
        return ""

# def extract_total_tax(texts, dt_polys, page_width, page_height):
#     """
#     提取总税额字段，增强健壮性：
#     - 仅在页面的下半区寻找税额。
#     - 最终提取到的字段，其横坐标必须大于 4/5 * page_width。
#     - 纵坐标范围与合计字段相同或 ±1.5 倍合计字段高度。
#     - 税额字段可能被分开识别为“税”和“额”。
#     - 如果找不到税额字段，尝试寻找与“合计”字段同一行的后后一个带 ¥ 或 ￥ 的字段。
#     - 距离限制：分开的“税”和“额”字段水平距离不能超过 100。
#     """
#     try:
#         # 初始化变量
#         tax_column_x = None
#         tax_width = None
#         total_tax = ""
#
#         # 找到“税额”列的 x 坐标范围
#         for i, text in enumerate(texts):
#             if "税额" in text:
#                 x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
#                 tax_column_x = (min(x_coords), max(x_coords))
#                 tax_width = abs(x_coords[1] - x_coords[0])  # 计算税额列宽度
#                 # print(f"找到税额列，x 坐标范围: {tax_column_x}, 列宽: {tax_width}")
#                 break
#
#         # 如果没有找到完整的“税额”，检查“税”和“额”是否被分开识别
#         if not tax_column_x:
#             for i, text in enumerate(texts):
#                 if "税" in text:
#                     for j, next_text in enumerate(texts):
#                         if "额" in next_text:
#                             # 检查“税”和“额”是否在同一水平线上
#                             y_coords_1 = [dt_polys[i][0][1], dt_polys[i][2][1]]
#                             y_coords_2 = [dt_polys[j][0][1], dt_polys[j][2][1]]
#                             y_center_1 = sum(y_coords_1) / 2
#                             y_center_2 = sum(y_coords_2) / 2
#                             x_coords_1 = [dt_polys[i][0][0], dt_polys[i][1][0]]
#                             x_coords_2 = [dt_polys[j][0][0], dt_polys[j][1][0]]
#                             x_distance = abs(min(x_coords_2) - max(x_coords_1))  # 计算“税”和“额”的水平距离
#
#                             if (
#                                 abs(y_center_1 - y_center_2) < 20
#                                 and x_distance <= 100
#                             ):  # 容差范围和距离限制
#                                 x_coords = [min(x_coords_1), max(x_coords_2)]
#                                 tax_column_x = (min(x_coords), max(x_coords))
#                                 tax_width = abs(tax_column_x[1] - tax_column_x[0])  # 计算列宽度
#                                 # print(f"找到分开的“税”“额”字段，x 坐标范围: {tax_column_x}, 列宽: {tax_width}, 距离: {x_distance}")
#                                 break
#                 if tax_column_x:
#                     break
#
#         # 如果找到“税额”列，放宽横坐标范围
#         if tax_column_x:
#             extended_x_range = (tax_column_x[0] - tax_width, tax_column_x[1] + tax_width)
#             # print(f"扩展后的 x 坐标范围: {extended_x_range}")
#         else:
#             extended_x_range = None
#
#         # 尝试找到“合计”字段或分开的“合”和“计”的 y 坐标范围
#         total_y = None
#         total_height = None
#         total_x_end = None
#         for i, text in enumerate(texts):
#             normalized_text = text.replace(":", "：").strip()
#             y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
#             y_center = sum(y_coords) / 2
#             height = abs(y_coords[1] - y_coords[0])  # 合计字段的高度
#
#             if "合计" in normalized_text:
#                 total_y = y_center
#                 total_height = height
#                 total_x_end = max([dt_polys[i][1][0], dt_polys[i][2][0]])  # 合计字段的右边 x 坐标
#                 # print(f"找到合计字段，y 坐标: {total_y}, 高度: {total_height}, x 坐标结束: {total_x_end}")
#                 break
#             elif "合" in normalized_text:
#                 for j, next_text in enumerate(texts):
#                     next_y_coords = [dt_polys[j][0][1], dt_polys[j][2][1]]
#                     next_y_center = sum(next_y_coords) / 2
#                     if "计" in next_text and abs(next_y_center - y_center) < 20:
#                         total_y = y_center
#                         total_height = height
#                         total_x_end = max([dt_polys[j][1][0], dt_polys[j][2][0]])  # 合计字段的右边 x 坐标
#                         # print(f"找到分开的“合计”字段，y 坐标: {total_y}, 高度: {total_height}")
#                         break
#             if total_y:
#                 break
#
#         if total_y is None or total_height is None:
#             # print("未找到合计字段，无法提取总税额")
#             return ""
#
#         # 纵坐标范围放宽 ±1.5 倍合计字段高度
#         tolerance_factor = 1.5
#         extended_y_range = (total_y - total_height * tolerance_factor, total_y + total_height * tolerance_factor)
#         # print(f"扩展后的 y 坐标范围: {extended_y_range}")
#
#         # 遍历所有文本，寻找税额内容
#         for i, text in enumerate(texts):
#             x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
#             y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
#             y_center = sum(y_coords) / 2
#
#             # 检查 x 和 y 坐标是否在范围内
#             if extended_x_range:
#                 if x_coords[0] < extended_x_range[0] or x_coords[1] > extended_x_range[1]:
#                     continue
#             if y_center < extended_y_range[0] or y_center > extended_y_range[1]:
#                 continue
#
#             # 使用正则表达式提取税额
#             tax_match = re.search(r"[¥￥]\s*(\d+\.\d+)", text)
#             if tax_match and min(x_coords) > 4 / 5 * page_width:  # 确保最终结果横坐标 > 4/5 page_width
#                 total_tax = tax_match.group(1).strip()
#                 # print(f"提取到总税额: {total_tax}")
#                 return total_tax
#
#         # 如果找不到税额，寻找“合计”字段右侧的后后一个金额字段
#         # print("未找到符合条件的税额，尝试寻找“合计”字段右侧的后后一个金额字段")
#         if total_x_end:
#             count = 0
#             for i, text in enumerate(texts):
#                 x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
#                 y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
#                 y_center = sum(y_coords) / 2
#
#                 if y_center < extended_y_range[0] or y_center > extended_y_range[1]:
#                     continue
#                 if x_coords[0] > total_x_end:
#                     count += 1
#                     if count == 2:  # 找到后后一个字段
#                         tax_match = re.search(r"[¥￥]\s*(\d+\.\d+)", text)
#                         if tax_match and min(x_coords) > 4 / 5 * page_width:
#                             total_tax = tax_match.group(1).strip()
#                             # print(f"从“合计”字段后后一个字段提取到税额: {total_tax}")
#                             return total_tax
#
#         # print("未找到任何税额字段")
#         return ""
#
#     except Exception as e:
#         # print(f"提取总税额时出错: {e}")
#         return ""


def extract_total_tax(texts, dt_polys, page_width, page_height):
    """
    提取总税额字段，增强健壮性：
    - 仅在页面的下半区寻找税额。
    - 最终提取到的字段，其横坐标必须大于 4/5 * page_width。
    - 纵坐标范围与合计字段相同或 ±1.5 倍合计字段高度。
    - 税额字段可能被分开识别为“税”和“额”。
    - 如果找不到税额字段，尝试寻找与“合计”字段同一行的后后一个带 ¥ 或 ￥ 的字段。
    - 如果未找到“合计”字段，尝试定位“价税合计”。
    - “价税合计”定位要求找到其中3个字以上，并扩展纵坐标范围进行查找。
    - 距离限制：分开的“税”和“额”字段水平距离不能超过 100。
    """
    try:
        # 初始化变量
        tax_column_x = None
        tax_width = None
        total_tax = ""

        # 找到“税额”列的 x 坐标范围
        for i, text in enumerate(texts):
            if "税额" in text:
                x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
                tax_column_x = (min(x_coords), max(x_coords))
                tax_width = abs(x_coords[1] - x_coords[0])  # 计算税额列宽度
                # print(f"找到税额列，x 坐标范围: {tax_column_x}, 列宽: {tax_width}")
                break

        # 如果没有找到完整的“税额”，检查“税”和“额”是否被分开识别
        if not tax_column_x:
            for i, text in enumerate(texts):
                if "税" in text:
                    for j, next_text in enumerate(texts):
                        if "额" in next_text:
                            # 检查“税”和“额”是否在同一水平线上
                            y_coords_1 = [dt_polys[i][0][1], dt_polys[i][2][1]]
                            y_coords_2 = [dt_polys[j][0][1], dt_polys[j][2][1]]
                            y_center_1 = sum(y_coords_1) / 2
                            y_center_2 = sum(y_coords_2) / 2
                            x_coords_1 = [dt_polys[i][0][0], dt_polys[i][1][0]]
                            x_coords_2 = [dt_polys[j][0][0], dt_polys[j][1][0]]
                            # 计算“税”和“额”的水平距离
                            x_distance = abs(min(x_coords_2) - max(x_coords_1))

                            if (
                                abs(y_center_1 - y_center_2) < 20
                                and x_distance <= 100
                            ):  # 容差范围和距离限制
                                x_coords = [min(x_coords_1), max(x_coords_2)]
                                tax_column_x = (min(x_coords), max(x_coords))
                                tax_width = abs(
                                    tax_column_x[1] - tax_column_x[0])  # 计算列宽度
                                # print(f"找到分开的“税”“额”字段，x 坐标范围: {tax_column_x}, 列宽: {tax_width}, 距离: {x_distance}")
                                break
                if tax_column_x:
                    break

        # 如果找到“税额”列，放宽横坐标范围
        if tax_column_x:
            extended_x_range = (
                tax_column_x[0] - tax_width, tax_column_x[1] + tax_width)
            # print(f"扩展后的 x 坐标范围: {extended_x_range}")
        else:
            extended_x_range = None

        # 尝试找到“合计”字段或分开的“合”和“计”的 y 坐标范围
        total_y = None
        total_height = None
        total_x_end = None
        for i, text in enumerate(texts):
            normalized_text = text.replace(":", "：").strip()
            y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
            y_center = sum(y_coords) / 2
            height = abs(y_coords[1] - y_coords[0])  # 合计字段的高度

            # 精确匹配“合计”，避免误识别其他字段
            if normalized_text == "合计" and "价" not in text and "税" not in text:
                total_y = y_center
                total_height = height
                total_x_end = max(
                    [dt_polys[i][1][0], dt_polys[i][2][0]])  # 合计字段的右边 x 坐标
                # print(f"找到合计字段，y 坐标: {total_y}, 高度: {total_height}, x 坐标结束: {total_x_end}")
                break
            elif normalized_text == "合":
                for j, next_text in enumerate(texts):
                    next_y_coords = [dt_polys[j][0][1], dt_polys[j][2][1]]
                    next_y_center = sum(next_y_coords) / 2
                    if next_text.strip() == "计" and abs(next_y_center - y_center) < 30:
                        total_y = y_center
                        total_height = height
                        total_x_end = max(
                            [dt_polys[j][1][0], dt_polys[j][2][0]])  # 合计字段的右边 x 坐标
                        # print(f"找到分开的“合计”字段，y 坐标: {total_y}, 高度: {total_height}")
                        break
            if total_y:
                break

        # 如果未找到“合计”，尝试寻找“价税合计”字段
        if total_y is None or total_height is None:
            # print("未找到合计字段，尝试定位“价税合计”字段")
            for i, text in enumerate(texts):
                if len([ch for ch in "价税合计" if ch in text]) >= 3:  # 匹配至少3个字
                    y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
                    total_y = sum(y_coords) / 2
                    total_height = abs(y_coords[1] - y_coords[0])
                    # print(f"找到“价税合计”字段，y 坐标: {total_y}, 高度: {total_height}")
                    total_y -= 2 * total_height  # 减去2倍行距
                    break

        if total_y is None or total_height is None:
            # print("未找到合计字段或价税合计字段，无法提取总税额")
            return ""

        # 纵坐标范围放宽 ±1.5 倍合计字段高度
        tolerance_factor = 1.5
        extended_y_range = (total_y - total_height * tolerance_factor,
                            total_y + total_height * tolerance_factor)
        # print(f"扩展后的 y 坐标范围: {extended_y_range}")

        # 遍历所有文本，寻找税额内容
        for i, text in enumerate(texts):
            x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
            y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
            y_center = sum(y_coords) / 2

            # 检查 x 和 y 坐标是否在范围内
            if extended_x_range:
                if x_coords[0] < extended_x_range[0] or x_coords[1] > extended_x_range[1]:
                    continue
            if y_center < extended_y_range[0] or y_center > extended_y_range[1]:
                continue

            # 使用正则表达式提取税额
            tax_match = re.search(r"[¥￥]\s*(\d+\.\d+)", text)
            # 确保最终结果横坐标 > 4/5 page_width
            if tax_match and min(x_coords) > 4 / 5 * page_width:
                total_tax = tax_match.group(1).strip()
                # print(f"提取到总税额: {total_tax}")
                return total_tax

        # 如果找不到税额，寻找“合计”字段右侧的后后一个金额字段
        # print("未找到符合条件的税额，尝试寻找“合计”字段右侧的后后一个金额字段")
        if total_x_end:
            count = 0
            for i, text in enumerate(texts):
                x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
                y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
                y_center = sum(y_coords) / 2

                if y_center < extended_y_range[0] or y_center > extended_y_range[1]:
                    continue
                if x_coords[0] > total_x_end:
                    count += 1
                    if count == 2:  # 找到后后一个字段
                        tax_match = re.search(r"[¥￥]\s*(\d+\.\d+)", text)
                        if tax_match and min(x_coords) > 4 / 5 * page_width:
                            total_tax = tax_match.group(1).strip()
                            # print(f"从“合计”字段后后一个字段提取到税额: {total_tax}")
                            return total_tax

        # print("未找到任何税额字段")
        return ""

    except Exception as e:
        # print(f"提取总税额时出错: {e}")
        return ""
# 项目名称提取


def extract_project_name(texts, dt_polys, page_height):
    """
    提取项目名称字段：
    - 如果是“项目名称”，水平查找范围为中心 ±1.5 个字段宽度。
    - 如果是“服务名称”，水平查找范围为中心 ±0.8 个字段宽度。
    - 高度范围限定为项目/服务名称字段下方的 0.5 个字段高度到“合计”字段上方，或者页面高度的 2/3。
    - 处理重复字段提取问题。
    """
    try:
        # 定位“项目名称”或“服务名称”字段的横坐标范围
        project_column_x = None
        project_width = None
        project_y = None
        project_height = None
        horizontal_tolerance_factor = None  # 水平查找范围扩展因子

        for i, text in enumerate(texts):
            if "项目名称" in text or "服务名称" in text:
                x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
                y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
                project_column_x = (min(x_coords), max(x_coords))
                project_width = abs(x_coords[1] - x_coords[0])  # 计算字段宽度
                project_y = max(y_coords)  # 获取字段的下边缘 y 坐标
                project_height = abs(y_coords[1] - y_coords[0])  # 计算字段高度

                # 根据字段类型设置水平查找范围扩展因子
                if "项目名称" in text:
                    horizontal_tolerance_factor = 1.5
                elif "服务名称" in text:
                    horizontal_tolerance_factor = 0.8

                # print(f"找到“项目名称”或“服务名称”字段，x 坐标范围: {project_column_x}, 宽度: {project_width}, y 坐标下边缘: {project_y}, 高度: {project_height}, 水平扩展因子: {horizontal_tolerance_factor}")
                break

        if not project_column_x or horizontal_tolerance_factor is None:
            # print("未找到“项目名称”或“服务名称”字段，无法提取项目名称")
            return []

        # 水平查找范围扩展
        center_x = sum(project_column_x) / 2
        extended_x_range = (
            center_x - horizontal_tolerance_factor * project_width,
            center_x + horizontal_tolerance_factor * project_width,
        )
        # print(f"扩展后的 x 坐标范围: {extended_x_range}")

        # 定位“合计”或分开的“合”和“计”字段的上边界
        total_y = None
        for i, text in enumerate(texts):
            normalized_text = text.replace(":", "：").strip()
            y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
            y_center = sum(y_coords) / 2

            if "合计" in normalized_text:
                total_y = min(y_coords)  # 获取“合计”字段的上边缘 y 坐标
                # print(f"找到“合计”字段，y 坐标上边缘: {total_y}")
                break
            elif "合" in normalized_text:
                # 检查是否存在“计”且与“合”在同一水平线上
                for j, next_text in enumerate(texts):
                    next_y_coords = [dt_polys[j][0][1], dt_polys[j][2][1]]
                    next_y_center = sum(next_y_coords) / 2
                    if "计" in next_text and abs(next_y_center - y_center) < 20:
                        total_y = min(y_coords)  # 获取“合计”字段的上边缘 y 坐标
                        # print(f"找到分开的“合计”字段，y 坐标上边缘: {total_y}")
                        break
            if total_y:
                break

        # 未找到“合计”字段，将上边界设置为页面高度的 2/3
        if total_y is None:
            total_y = page_height * 2 / 3
            # print(f"未找到“合计”字段，默认上边界 y 坐标为页面高度的 2/3: {total_y}")

        # 设置项目名称字段的高度范围
        extended_y_range = (project_y - 0.3 * project_height, total_y)
        # print(f"扩展后的 y 坐标范围: {extended_y_range}")

        # 遍历所有文本，寻找符合条件的项目名称字段
        project_names = []
        for i, text in enumerate(texts):
            x_coords = [dt_polys[i][0][0], dt_polys[i][1][0]]
            y_coords = [dt_polys[i][0][1], dt_polys[i][2][1]]
            y_center = sum(y_coords) / 2

            # 检查是否在扩展的横坐标范围内
            if x_coords[0] < extended_x_range[0] or x_coords[1] > extended_x_range[1]:
                continue

            # 检查是否在扩展的高度范围内
            if y_center < extended_y_range[0] or y_center > extended_y_range[1]:
                continue

            # 如果通过条件，认为是项目名称
            project_names.append(text.strip())
            # print(f"提取到项目名称: {text.strip()}")

        if not project_names:
            # print("未找到任何符合条件的项目名称")
            return []

        return project_names

    except Exception as e:
        # print(f"提取项目名称时出错: {e}")
        return []


def extract_invoice_fields(json_data, qr_data):
    # 初始化字段字典
    fields = {
        "InvoiceNum": "",  # 发票号
        "InvoiceDate": "",  # 发票日期
        "NoteDrawer": "",  # 开票人
        "TotalAmount": "",  # 总金额
        "TotalTax": "",  # 总税额
        "SellerName": "",  # 销售方名称
        "SellerRegisterNum": "",  # 销售方纳税人识别号
        "PurchaserName": "",  # 购买方名称
        "PurchaserRegisterNum": "",  # 购买方纳税人识别号
        "CommodityDetails": ""  # 商品详情
    }
    texts = json_data.get("ocr_result", {}).get("rec_text", [])
    dt_polys = json_data.get("ocr_result", {}).get("dt_polys", [])
    page_width = calculate_page_width(dt_polys)
    page_height = calculate_page_height(dt_polys)
    # print(texts)

    def safe_split(text, delimiter, index):
        """安全分割字符串，避免索引错误"""
        parts = text.split(delimiter)
        return parts[index] if len(parts) > index else ""

    # 提取字段值
    fields["InvoiceNum"] = extract_invoice_number(texts)
    fields["InvoiceDate"] = extract_invoice_date(texts)
    fields["NoteDrawer"] = extract_note_drawer(texts, dt_polys, page_height)
    fields["TotalAmount"] = extract_total_amount_without_tax(
        texts, dt_polys, page_height)
    fields["TotalTax"] = extract_total_tax(
        texts, dt_polys, page_width, page_height)
    fields["SellerName"] = extract_seller_name(
        texts, dt_polys, page_width, page_height)
    fields["SellerRegisterNum"] = extract_seller_register_num(
        texts, dt_polys, page_width, page_height)
    fields["PurchaserName"] = extract_purchaser_name(
        texts, dt_polys, page_width, page_height)
    fields["PurchaserRegisterNum"] = extract_purchaser_register_num(
        texts, dt_polys, page_width, page_height)
    fields["totalPay"] = extract_total_price(texts, dt_polys)
    fields["CommodityDetails"] = extract_project_name(
        texts, dt_polys, page_height)

    if qr_data and isinstance(qr_data, list):
        try:

            if len(qr_data) > 5:
                if qr_data[2] == "":
                    if len(qr_data) > 4 and '.' in qr_data[4]:
                        fields["totalPay"] = qr_data[4]  # 含税金额
                else:  # 第三个字段不为空
                    if len(qr_data) > 4 and '.' in qr_data[4]:
                        fields["TotalAmount"] = qr_data[4]  # 不含税金额

        except Exception as e:
            print(f"处理 QR 数据时出错: {e}")

    return fields


def find_with_json(json_path, qr_data):

    with open(json_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    # 提取字段
    extracted_fields = extract_invoice_fields(json_data, qr_data)

    # 输出提取结果
    # return (json.dumps(extracted_fields, ensure_ascii=False, indent=4))
    return extracted_fields
