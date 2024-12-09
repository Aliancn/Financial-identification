import pdfplumber
# from langchain_community.document_loaders import PDFPlumberLoader as pdfplumber
import pandas as pd


def getTextPdf(path: str):
    with pdfplumber.open(path) as pdf:
        print('页数：', len(pdf.pages))
        content = ''
        for i in range(len(pdf.pages)):
            # 读取PDF文档第i+1页
            page = pdf.pages[i]

            # page.extract_text()函数即读取文本内容，下面这步是去掉文档最下面的页码
            page_content = '\n'.join(page.extract_text().split('\n')[:-1])
            content = content + page_content
        return content


# 提取以上解析结果中，“地方法规”和“2.其他有关资料”之间的内容
# result = content.split('地方法规列举如下：')[1].split('2.其他有关资料')[0]

def getTablePdf(path):
    with pdfplumber.open(path) as pdf:
        first_page = pdf.pages[0]
        tables = first_page.extract_tables()
        content = []
        for table in tables:
            df = pd.DataFrame(table)
            # 第一列当成表头：
            df = pd.DataFrame(table[1:], columns=table[0])
            content.append(df)


if __name__ == '__main__':
    path = 'policy.pdf'
    content = getTextPdf(path)
    print(content)
    # table = getTable(path)
    # print(table)
