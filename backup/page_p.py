from random import choices
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import gradio as gr
import shutil
import os

from matplotlib.pyplot import cla

from main_p import process_invoice, func_ocr, func_classify
from log import logger
import time
import pandas as pd
app = FastAPI()
time_now = time.time()
logger.info("App started: " + f"{time_now}")

# 定义处理上传文件的函数


def handle_upload(file, target_dir='tmp'):
    try:
        file = file.name
        target_dir = os.path.join(os.getcwd(), target_dir)
        logger.info(f"target_dir: {target_dir}")
        os.makedirs(target_dir, exist_ok=True)
        file_path = os.path.join(target_dir, os.path.basename(file))

        if not os.path.isfile(file):
            logger.error(f"Source file does not exist: {file}")
            return None

        shutil.copy(file, file_path)

        if os.path.isfile(file_path):
            # logger.info(f"File successfully saved to {file_path}")
            # pdf 2 image
            # if file_path.endswith('.pdf'):
            #     logger.info(f"Converting PDF to image: {file_path}")
            #     from pdf2image import convert_from_path
            #     images = convert_from_path(file_path)
            #     if images:
            #         image_path = file_path.replace('.pdf', '.jpg')
            #         images[0].save(image_path, 'JPEG')
            #         logger.info(f"PDF successfully converted to image: {image_path}")
            #         return image_path
            #     else:
            #         logger.error(f"Failed to convert PDF to image: {file_path}")
            #         return None
            return file_path
        else:
            logger.error(f"Failed to save file to {file_path}")
            return None
    except Exception as e:
        logger.error(f"An error occurred while handling the upload: {e}")
        return None


# 定义 Gradio 界面


def gradio_interface():
    # def classify(file):
    #     file_path = handle_upload(file=file)
    #     classifications, df_fields = classify_invoice(file_path)
    #     return classifications, df_fields

    def handle_ocr(file):
        file_path = handle_upload(file=file)
        fields = func_ocr(file_path)
        df_fields = pd.DataFrame([fields]).drop(columns=["CommodityDetails"])
        return df_fields, fields

    def handle_classify(fields):
        res = func_classify(fields)
        classification = res['科目名称']
        if type(classification) == str:
            classification = [classification]
        classification = pd.DataFrame(classification, columns=["分类"])

        itemNum = res['商品详细信息']
        if type(itemNum) == str:
            itemNum = [itemNum]
        itemNum = pd.DataFrame(itemNum, columns=["商品详细信息"])
        clas = classification.join(itemNum)
        return clas

    with gr.Blocks() as demo:
        with gr.Row():
            file_input = gr.File(label="上传发票文件", file_count="single", file_types=[
                                 '.pdf', '.jpg', '.png'])
            classify_button = gr.Button("分类")
            # classification_output = gr.Dropdown(
            #     label="选择分类", choices=[], allow_custom_value=True)

        # 添加表格展示字段信息
        with gr.Row():
            fields_table = gr.DataFrame(label="发票信息展示")

        with gr.Row():
            classification_output = gr.DataFrame(label="分类信息展示")

        # def update_info(file):
        #     classification, df_fields = classify(file)
        #     return classification, df_fields

        # 使用 State 组件保存 OCR 结果
        ocr_result = gr.State()

        # 先更新 fields_table，再更新 classification_output
        classify_button.click(handle_ocr, inputs=[file_input], outputs=[fields_table, ocr_result]).then(
            handle_classify, inputs=[ocr_result], outputs=classification_output
        )

    return demo


# 启动 Gradio 界面
gradio_app = gradio_interface()


@app.get("/")
async def read_root():
    return {"message": "Hello World"}


@app.get("/gradio")
async def get_gradio():
    return gradio_app.launch(share=True)


def save_uploaded_file(uploaded_file: UploadFile, target_dir: str = '/tmp') -> str:
    try:
        target_dir = os.path.join(os.getcwd(), target_dir)
        os.makedirs(target_dir, exist_ok=True)
        file_path = os.path.join(target_dir, uploaded_file.filename)

        with open(file_path, "wb") as file:
            file.write(uploaded_file.file.read())

        return file_path
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save file: {e}")


@app.post("/classify")
async def classify(file: UploadFile = File(...)):
    file_path = save_uploaded_file(file)
    # 保存文件
    if file_path is None:
        raise HTTPException(status_code=500, detail="Failed to save file")
    result = process_invoice(file_path)
    return JSONResponse(content={"result": result})

if __name__ == "__main__":
    # import uvicorn
    # uvicorn.run(app, host="127.0.0.1", port=8001)
    gradio_app.launch(share=False)
