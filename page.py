from random import choices
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import gradio as gr
import shutil
import os
import pathlib
import logging
from main import process_invoice
from sklearn import base
from sympy import false
from log import SimpleLogger
import time
app = FastAPI()
logger = SimpleLogger(log_file='app.log', log_level=logging.DEBUG)
time_now = time.time()
logger.info("App started: " + f"{time_now}")

# 模拟分类函数


def classify_invoice(file_path):
    # 这里可以添加实际的分类逻辑
    # 例如，使用 OCR 提取文本，然后进行分类
    # 这里我们假设返回两个可能的分类
    logger.info(f"file_path: {file_path}")
    result = process_invoice(file_path)
    logger.info(result["category"]["科目名称"])
    return result["category"]["科目名称"]

# 定义处理上传文件的函数


def handle_upload(file, target_dir='tmp'):
    try:
        file = file.name
        target_dir = os.path.join(os.getcwd(),target_dir) ; 
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
    def classify_and_select(file):
        file_path = handle_upload(file=file)
        classifications = classify_invoice(file_path)
        # os.remove(file_path)
        return gr.Dropdown(choices=classifications, value=classifications[0])

    def final_classification(file, selected_classification):
        # file_path = handle_upload(file)
        # 这里可以添加保存最终分类结果的逻辑
        # os.remove(file_path)
        return f"最终分类: {selected_classification}"

    with gr.Blocks() as demo:
        with gr.Row():
            file_input = gr.File(label="上传发票文件", file_count="single", file_types=[
                                 '.pdf', '.jpg', '.png'])
            classify_button = gr.Button("分类")
            classification_output = gr.Dropdown(
                label="选择分类", choices=[], allow_custom_value=True)

        classify_button.click(classify_and_select, inputs=[
                              file_input], outputs=[classification_output])

        with gr.Row():
            final_classification_button = gr.Button("确认最终分类")
            final_classification_output = gr.Textbox(label="最终分类结果")

        final_classification_button.click(final_classification, inputs=[
                                          file_input, classification_output], outputs=[final_classification_output])

    return demo


# 启动 Gradio 界面
gradio_app = gradio_interface()


@app.get("/")
async def read_root():
    return {"message": "Hello World"}


@app.get("/gradio")
async def get_gradio():
    return gradio_app.launch(share=True)

if __name__ == "__main__":
    # import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    gradio_app.launch(share=False)
