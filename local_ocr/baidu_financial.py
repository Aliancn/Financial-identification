from traceback import print_tb
import requests
import base64
import urllib
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
API_KEY = os.getenv('BAIDU_API_KEY')
SECRET_KEY = os.getenv('BAIDU_SECRET_KEY')

print(API_KEY)
print(SECRET_KEY)
'''
智能财务票据识别
'''

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

def get_file_content_as_base64(path, urlencoded=False):
    """
    获取文件base64编码
    :param path: 文件路径
    :param urlencoded: 是否对结果进行urlencoded 
    :return: base64编码信息
    """
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
    return content

def get_baidu_ocr(image_path):
    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/multiple_invoice?access_token=" + get_access_token()
    
    print("url", url)
    img = get_file_content_as_base64(image_path,True)
    payload=f'image={img}&verify_parameter=false&probability=false&location=false'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    # 处理返回结果
    result = response.json()

    return result

if __name__ == '__main__':
    get_baidu_ocr('../whu/test/3.jpg')
