import requests
import json
from log import logger 

def req_chat_long(prompt,  history=[], api_url='http://127.0.0.1:7860/chat'):
    # 用于向glm-long 发送对话请求
    # 日志写在llvm_log.txt
    pay_load = {
        "message": prompt,
        "history": history,
        "temperature": 0.5,
        "max_new_tokens": 4096
    }

    # 请求
    try:
        logger.info(f"Requesting chat-long with payload: {pay_load}")
        response = requests.post(api_url, json=pay_load)
        response.raise_for_status()  # 检查是否有 HTTP 错误
        # 解析返回数据
        response_data = response.json()
        return response_data

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
    
if __name__ == "__main__":
    prompt = "请问这是什么发票？"
    response = req_chat_long(prompt)
    print(response)
