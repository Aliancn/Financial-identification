import gradio as gr

# 模拟对话逻辑函数
def chat_respond(user_message, chat_history):
    # chat_history是一个[(user_msg, bot_msg), ...]的列表。
    # 根据用户输入生成下一个回复。
    # 这里仅为示例，实际可接入您的对话逻辑或模型。
    if "预约" in user_message:
        bot_reply = "您可以登录后进入设备预约界面，选择设备信息，进行预约，如：高通离心机，2024-03-12 10:00-10:30"
    elif "反馈" in user_message:
        bot_reply = "您可以拨打我们的反馈电话400-888-8888或立即转人工反馈组进行处理。"
    else:
        bot_reply = "您好，这里是公共科科询智能实验室助手，请问有什么可以帮助您的？"
        
    chat_history.append((user_message, bot_reply))
    return "", chat_history


# 当点击预约按钮时触发的回调函数
def on_reservation_click():
    # 实际逻辑可能是跳转到某个预约链接或者改变界面等
    # 这里暂做示例性的提示语输出，可以根据需求定制
    return "即将跳转至预约界面..."

# 当点击反馈按钮时触发的回调函数
def on_feedback_click():
    # 同理，这里也可以进行页面跳转或输出其他信息
    return "正在转接至人工反馈组...请稍候"


with gr.Blocks() as demo:
    gr.Markdown("# 类似于智能客服的对话页面示例")
    
    chatbot = gr.Chatbot(label="对话框", elem_id="chatbot",type="messages")
    user_input = gr.Textbox(label="输入您的问题：", placeholder="请在此输入...")
    submit_btn = gr.Button("发送")
    
    with gr.Row():
        reservation_button = gr.Button("设备预约")
        feedback_button = gr.Button("意见反馈")
    
    # 用于显示按钮点击的结果提示
    output_text = gr.Textbox(label="系统通知", interactive=False)
    
    # 每当用户点击“发送”时调用 chat_respond 进行对话
    submit_btn.click(fn=chat_respond, inputs=[user_input, chatbot], outputs=[user_input, chatbot])
    
    # 点击按钮时的回调
    reservation_button.click(fn=on_reservation_click, outputs=output_text)
    feedback_button.click(fn=on_feedback_click, outputs=output_text)

demo.launch()
