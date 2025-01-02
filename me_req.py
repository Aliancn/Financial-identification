import requests
import json


def req_chat(prompt, content,  history=None, api_url='http://127.0.0.1:6006/api/chat'):
    # 用于向glm-4-chat 发送对话请求
    # 请求数据
    data = {
        "prompt": prompt,
        "content": content,
        "history": [],  # 如果需要，可以传递历史对话记录
    }

    # 设置请求头
    headers = {
        "Content-Type": "application/json"
    }

    # 发送 POST 请求
    try:
        # log
        open('llvm_log.txt', 'a').write(
            f'prompt: {prompt}, content: "{content}"\n')
        response = requests.post(
            api_url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # 检查是否有 HTTP 错误

        # 解析返回数据
        response_data = response.json()['response']
        return response_data

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


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
        open('llvm_log.txt', 'a').write(
            f'prompt: {prompt}')
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
