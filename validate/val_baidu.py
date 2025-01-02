import json
from log import logger
import requests
from dotenv import load_dotenv, find_dotenv
from os import environ

load_dotenv(find_dotenv())
load_dotenv(find_dotenv())
API_KEY = environ.get("BAIDU_API_KEY")
SECRET_KEY = environ.get("BAIDU_SECRET_KEY")
# API_KEY="7IIOpbt5UykdriEcvW11Pz8n"
# SECRET_KEY="A31sxhyyGTPzWJJbsTU3ythzTRIxqPhJ"
# Token = None


def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials",
              "client_id": API_KEY, "client_secret": SECRET_KEY}
    s = str(requests.post(url, params=params).json().get("access_token"))
    print(s)
    return s


def vaild(invoice_code, invoice_num, invoice_date, invoice_type, check_code, total_amount):
    # if Token == None:
        # Token = get_access_token()

    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/vat_invoice_verification?access_token=" + Token

    payload = f'invoice_code={invoice_code}&invoice_num={invoice_num}&invoice_date={invoice_date}&invoice_type={invoice_type}&check_code={check_code}&total_amount={total_amount}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.content)

    if response.status_code == 200:
        # 返回解析后的 JSON 数据
        
        logger.info(f"API 请求成功: {response.text}")
        return response.text
    else:
        # 如果状态码不为 200，抛出异常并打印错误信息
        print(f"API 请求失败: {response.text}")
        raise ValueError(f"API 请求失败: {response.text}")
    # return response.text


# if __name__ == '__main__':
    # 旧发票
    # data=vaild('014002200311','00143812','20230619','elec_normal_invoice','462072','5940.59')
    # 新发票
    # data = vaild('', '24117000000295693830', '20240617',
    #              'elec_normal_invoice', '', '75.00')
    # print(data)
    # extracted_fields = extract_from_response(data)
# get_access_token()

Token = get_access_token()
