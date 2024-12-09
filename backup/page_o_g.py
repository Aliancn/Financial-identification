from random import choices
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import gradio as gr
import shutil
import os

from main_o_g import process_invoice
from log import logger
import time
import pandas as pd
app = FastAPI()
time_now = time.time()
logger.info("App started: " + f"{time_now}")

# 模拟分类函

def classify_invoice(file_path):
    # 这里可以添加实际的分类逻辑
    logger.info(f"file_path: {file_path}")
    result = process_invoice(file_path)

    fields = result["extracted_fields"]
    df_fields = pd.DataFrame([fields]).drop(columns=["CommodityDetails"])
    classification = result["category"]["科目名称"]
    if type(classification) == str:
        classification = [classification]
    classification = pd.DataFrame(classification, columns=["分类"])
    logger.info(f"classification: {classification}")
    logger.info(f"df_fields: {df_fields}")

    return classification, df_fields

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

        logger.info(f"file src: {file}")
        logger.info(f"file tar: {file_path}")

        shutil.copy(file, file_path)

        if os.path.isfile(file_path):
            logger.info(f"File successfully saved to {file_path}")
            return file_path
        else:
            logger.error(f"Failed to save file to {file_path}")
            return None
    except Exception as e:
        logger.error(f"An error occurred while handling the upload: {e}")
        return None


# 定义 Gradio 界面


def gradio_interface():
    def classify(file):
        file_path = handle_upload(file=file)
        classifications, df_fields = classify_invoice(file_path)
        # logger.info(f"classifications: {classifications}")
        # logger.info(f"type(classifications): {type(classifications)}")
        # logger.info(f"df_fields: {df_fields}")
        # if len(classifications) == 0:
        #     logger.error("No classifications found")
        # elif type(classifications) == str:
        #     classifications = [classifications]

        # return gr.Dropdown(choices=classifications, value=classifications[0]), df_fields
        return classifications, df_fields

    with gr.Blocks() as demo:
        with gr.Row():
            file_input = gr.File(label="上传发票文件", file_count="single", file_types=[
                                 '.pdf', '.jpg', '.png'])
            classify_button = gr.Button("分类")
            # classification_output = gr.Dropdown(
            #     label="选择分类", choices=[], allow_custom_value=True)

        with gr.Row():
            classification_output = gr.DataFrame(label="分类信息展示")
        # 添加表格展示字段信息
        with gr.Row():
            fields_table = gr.DataFrame(label="发票信息展示")

        def update_info(file):
            classification, df_fields = classify(file)
            return classification, df_fields

        classify_button.click(update_info, inputs=[
                              file_input], outputs=[classification_output, fields_table])

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
