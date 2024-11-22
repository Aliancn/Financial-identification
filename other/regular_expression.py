# # coding=gb2312

import pandas as pd
import re


# Extract relevant columns for creating regex patterns
def load_classification_data():
    file_path = 'classification_standard.xlsx'
    excel_data = pd.ExcelFile(file_path)
    sheet_1 = excel_data.parse('商品对照')
    return sheet_1[['科目名称', '相关对应商品（达不到资产验收条件的商品，且不满足设备附件验收条件）']]


categories = load_classification_data()


# Example text to match against the regex patterns
example_text = "111"


def regex_match(categories, example_text):
    # Generate regex patterns based on the '相关对应商品' field for each category
    regex_patterns = {}
    for index, row in categories.iterrows():
        category = row['科目名称']
        items = row['相关对应商品（达不到资产验收条件的商品，且不满足设备附件验收条件）']
        # Split items by common delimiters (Chinese comma, comma, and other separators)
        item_keywords = re.split(r'[，、,]', str(items))
        # Create a regex pattern by joining keywords with '|'
        pattern = '|'.join([re.escape(keyword.strip())
                           for keyword in item_keywords if keyword.strip()])
        regex_patterns[category] = pattern

    # Check which category regex matches the example text
    matching_categories = [category for category, pattern in regex_patterns.items(
    ) if re.search(pattern, example_text)]

    # If no category matched, return a default message
    return matching_categories if matching_categories else ["未找到匹配类别"]


# Display the matching categories
print(regex_match(categories, example_text))
