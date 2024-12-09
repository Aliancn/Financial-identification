
import pandas as pd
import re
import os 

# Load classification data


def load_classification_data():
    now_path = os.path.dirname(__file__)
    file_path = os.path.join(now_path,'classifyItem.xlsx')
    
    excel_data = pd.ExcelFile(file_path)
    return excel_data.parse('Sheet1', usecols=['会计科目名称', '相关对应商品'])

re_class_categories = load_classification_data()


def regex_match( example_text,categories= re_class_categories):
    regex_patterns = {}
    for index, row in categories.iterrows():
        category = row['会计科目名称']
        items = row['相关对应商品']
        # Split items by common delimiters (Chinese comma, comma, and other separators and spaces)
        item_keywords = re.split(r'[,，、\s]', str(items))
        # Create a list of regex patterns for each keyword to allow partial matches
        patterns = [re.escape(keyword.strip())
                    for keyword in item_keywords if keyword.strip()]
        regex_patterns[category] = patterns

    # Check which category regex matches the example text
    matching_categories = []
    for category, patterns in regex_patterns.items():
        for pattern in patterns:
            # Match the keyword exactly as a whole word to avoid partial overmatching
            if re.search(r'\b' + pattern + r'\b', example_text, re.IGNORECASE):
                matching_categories.append(category)
                break  # Stop after the first match in this category

    # If no category matched, return a default message
    return matching_categories if matching_categories else ["未找到匹配类别"]



def get_category(item):
    return regex_match(re_class_categories, item)

# if __name__ == "__main__":
#     example_text = "离心机"
#     # Display the matching categories
#     print(regex_match(re_class_categories, example_text))
