from pprint import pprint
from rag_policy.byhand import getTextPdf


def get_prompt_for_as_rag(invoice_info, uer_info, policy_info):
    """
    根据输入的发票信息、用户信息和报销政策信息，生成对应的prompt。

    参数:
    invoice_info (str): 发票信息。
    uer_info (str): 用户信息。
    policy_info (str): 报销政策信息。

    返回:
    str: 生成的任务描述。
    """
    prompt = f"""
    **输入**：  
    1. 发票信息：
    {invoice_info}  
    2. 用户信息：
    {uer_info}
    3. 报销政策：
    {policy_info}

    **任务**：  
    - 判断发票内容是否符合报销政策要求。  
    - 计算实际可报销金额，并指出超限额或特殊审批需求。  
    - 提供政策适用的具体条款依据及注意事项。  

    **输出**：  
    - 报销判断结果（可报销/不可报销）及理由。  
    - 适用的政策条款及依据。  
    - 可报销金额及相关限制说明。  
    - 必要的操作建议或提交材料清单（如需额外审批）。  

    **要求**：  
    确保推理结果准确且易于理解，支持多样化政策和复杂报销场景。
    """

    return prompt


invoice_info_example = """
{
    "InvoiceNum": "24952000000110579895",
    "InvoiceDate": "2024年07月17日",
    "NoteDrawer": "吴启山",
    "TotalAmount": "121.81",
    "TotalTax": "15.83",
    "SellerName": "深圳市浩凌科技有限公司",
    "SellerRegisterNum": "91440300587908164C",
    "PurchaserName": "武汉大学",
    "PurchaserRegisterNum": "12100000707137123P",
    "CommodityDetails": [
        "*计算机配套产品*键盘"
    ],
    "totalPay": "137.64"
}
"""

user_info_example = """
{
    "UserName": "张三",
    "Department": "信息管理中心",
    "post" : "副教授",
    "Balance": "1000.00",
}
"""


# policy_info_example = getTextPdf("./rag_policy/policy.pdf")
# pr = get_prompt_for_as_rag(
#     invoice_info_example, user_info_example, policy_info_example)
# pprint(pr)


def get_policy_prompt(policy_file_path, invoice_info, user_info= user_info_example):
    policy_info = getTextPdf(policy_file_path)
    pr = get_prompt_for_as_rag(invoice_info, user_info, policy_info)
    return pr
