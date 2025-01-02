import shutil
import struct
from weasyprint import HTML
from jinja2 import Template
import os
from PIL import Image
from pdf2image import convert_from_path
# 模板变量
template_data = {
    "title": "武汉大学软件资产报账单",
    "report_number": "R202411250002",
    "department": "测绘学院",
    "accept_date": "2024-12-05",
    "operator_id": "00007880",
    "operator_name": "黄曦 - 13554449991",
    "acceptor": "夏正伟",
    "project_number": "1505-600460044",
    "project_content": "黄曦购买安全防护平台（本次支付）",
    "project_amount": "183,900.00",
    "booked_amount_upper": "壹拾捌万叁仟玖佰元整",
    "booked_amount_lower": "183,900.00",
    "payment_method": "对公转账",
    "payment_amount": "183,900",
    "payment_note": "测绘安全防护平台",
    "invoice_amount": "182,079.2",
    "invoice_tax": "1,820.8",
    "invoice_total": "183,900",
    "counterparty_name": "武汉珞鸿科技有限公司",
    "counterparty_region": "武汉",
    "counterparty_bank": "中国银行股份有限公司武汉鲁巷广场支行",
    "counterparty_account": "570382525131",
    "electronic_invoice_number": "24422000000170611670",
    "invoice_number": "24422000000170611670",
    "invoice_unit_name": "武汉大学",
    "actual_amount_upper": "拾 万 仟 佰 拾 元 角 分",
    "actual_amount_lower": "",
    "actual_number": ""
}

# template_data = {
#     'InvoiceNum': '99239294',
#     'InvoiceDate': '20211025',
#     'NoteDrawer': '',
#     'TotalAmount': '40631.07',
#     'TotalTax': '1218.93',
#     'SellerName': '武汉大学',
#     'SellerRegisterNum': '12100000707137123P',
#     'PurchaserName': '海军工程大学',
#     'PurchaserRegisterNum': 'Q99420104005655507',
#     'CommodityDetails': ['*研发和技术服务**研发及技术服务费'],
#     'Remarks': None
# }


def draw_html(data=template_data):
    # 读取 HTML 模板文件
    template_path = os.path.join(os.path.dirname(__file__), "template.html")
    with open(template_path, "r", encoding="utf-8") as file:
        template_content = file.read()

    # 渲染 HTML
    template = Template(template_content)
    rendered_html = template.render(data)

    html_path = os.path.join(os.path.dirname(__file__),"tmp_output" ,"output.html")
    # 保存到文件
    with open(html_path, "w", encoding="utf-8") as output_file:
        output_file.write(rendered_html)

    print("HTML 文件已生成！" , html_path)
    return html_path


# html to pdf


def html_to_pdf(html_path):
    # HTML("output.html").write_pdf("output.pdf")
    pdf_path = html_path.replace(".html", ".pdf")
    HTML(html_path).write_pdf(pdf_path)

    # copy  to static
    # file_satic = shutil.copy(pdf_path, os.path.join(
    #     os.path.dirname(__file__), "../static"))

    print("PDF 文件已生成！", pdf_path)

    # 返回文件
    return pdf_path


def pdf_to_single_img(pdf_path):
    images = convert_from_path(pdf_path)
    widths, heights = zip(*(i.size for i in images))

    total_width = max(widths)
    total_height = sum(heights)

    new_img = Image.new('RGB', (total_width, total_height))

    y_offset = 0
    for img in images:
        new_img.paste(img, (0, y_offset))
        y_offset += img.height

    img_path = pdf_path.replace(".pdf", ".png")
    new_img.save(img_path)
    print("PNG 文件已生成！", img_path)
    return img_path


if __name__ == "__main__":
    html_path = draw_html()
    html_to_pdf(html_path)
    pdf_to_single_img(html_path.replace(".html", ".pdf"))
