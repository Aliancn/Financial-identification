import re
from fastapi import FastAPI, UploadFile, File
from validate.app import predict
from pydantic import BaseModel
import os
from fastapi.middleware.cors import CORSMiddleware
from llvm.me_req import req_chat_long
from rag_policy.regular_expression import regex_match
from rag_policy.req import get_policy_prompt
from validate.app import predict
from print.gen_pdf import draw_html, html_to_pdf, pdf_to_single_img
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from log import logger
app = FastAPI()

# 设置静态文件目录
app.mount("/print", StaticFiles(directory="./print/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def extract_dialogues(text):
    """
    解析回答文本，提取对话内容
    :param text: 包含对话的文本
    :return: 对话内容列表
    """
    regex = re.compile(r'<\|assistant\|>(.*?)<\|user\|>', re.DOTALL)
    matches = regex.findall(text)
    dialogues = [match.strip() for match in matches]
    return dialogues


@app.post("/get_invoice_chart")
async def get_invoice_chart(file: UploadFile = File(...)):
    dir_path = os.path.dirname(__file__)
    file_location = f"{dir_path}/tmp/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # 传入本地图片路径，返回字典发票信息
    invoice_info = predict(file_location)

    if invoice_info == {}:
        return {"error": "No invoice info found"}

    prompt = f"请你把发票信息转换成图表\n {invoice_info}"

    response_chart = req_chat_long(prompt=prompt)

    logger.info(f"response_chart: {response_chart}")
    return {"result": invoice_info, "chart": response_chart}


@app.get("/pdf")
def pdf():
    html_path = draw_html()
    pdf_path = html_to_pdf(html_path)
    img_path = pdf_to_single_img(pdf_path)

    return FileResponse(img_path, media_type='image.png', filename=os.path.basename(img_path))


class Items(BaseModel):
    entrys: list[str]
    invoice_info: dict


@app.post("/policy")
async def policy(items: Items):

    # get category
    category = regex_match(items.entrys[0])

    # get policy prompt
    prompt = get_policy_prompt(
        "./rag_policy/policy.pdf", items.invoice_info)
    response = req_chat_long(prompt=prompt)

    return {"category": category, "response": response}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
