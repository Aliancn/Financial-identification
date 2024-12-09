import requests
from dotenv import load_dotenv, find_dotenv
from os import environ

from yaml import Token
load_dotenv(find_dotenv())
API_KEY = environ.get("BAIDU_API_KEY")
SECRET_KEY = environ.get("BAIDU_SECRET_KEY")
TOKEN = None
    

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

def vaild(invoice_code, invoice_num, invoice_date, invoice_type, check_code, total_amount):
    if Token == None:
        Token = get_access_token()
        
    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/vat_invoice_verification?access_token=" + Token
    
    payload=f'invoice_code={invoice_code}&invoice_num={invoice_num}&invoice_date={invoice_date}&invoice_type={invoice_type}&check_code={check_code}&total_amount={total_amount}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    print(response.text)
    
    return response.text
