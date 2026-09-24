import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "shared").is_dir())))

from shared import config, web  # noqa: E402

import os
from flask import request, render_template, send_file, make_response, jsonify
from markupsafe import Markup
import markdown
from docx import Document
from docx.oxml.ns import qn
from bs4 import BeautifulSoup

app = web.create_flask_app(__name__)

# 自定义过滤器，用于提取文件名
@app.template_filter('basename')
def basename_filter(path):
    return os.path.basename(path)

# 用于存储所有md文件路径
all_files = []
# 文件的根目录
docs_root = str(config.path_from(__file__, "laws"))
for root, dirs, files in os.walk(docs_root):
    for file in files:
        if file.endswith('.md'):
            all_files.append(os.path.join(root, file))

@app.route('/')
def index():
    return render_template('index.html', all_files=all_files)

@app.route('/show_md', methods=['GET'])
def show_md():
    filename = request.args.get('filename')
    content = md2html(filename)
    md_content = open(filename, 'r', encoding='utf-8').read()
    return render_template('show_md.html', content=content, md_content=md_content, filename=filename)

@app.route('/download_word', methods=['GET'])
def download_word():
    filename = request.args.get('filename')
    # 确保路径正确
    if not os.path.exists(filename):
        return "File not found", 404
    return send_file(filename, as_attachment=True)

@app.route('/save_md', methods=['POST'])
def save_md():
    data = request.form
    custom_filename = data.get('custom_filename')  # 获取用户自定义的文件名
    content = data.get('content')

    # 确保文件名合法
    if not custom_filename:
        return jsonify({'status': 'error', 'message': 'Invalid filename'}), 400
    # 移除路径部分，防止路径穿越攻击
    custom_filename = os.path.basename(custom_filename)
    # 添加 .md 扩展名，如果用户没有提供
    if not custom_filename.endswith('.md'):
        custom_filename += '.md'

    # 保存到 tem 文件夹
    tem_dir = str(config.path_from(__file__, 'mymodel'))
    os.makedirs(tem_dir, exist_ok=True)  # 确保 tem 文件夹存在
    tem_path = os.path.join(tem_dir, custom_filename)

    try:
        with open(tem_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({'status': 'success', 'message': 'File saved successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/delete_temp_file', methods=['POST'])
def delete_temp_file():
    data = request.form
    filename = data.get('filename')
    try:
        if os.path.exists(filename):
            os.remove(filename)
        return 'File deleted successfully'
    except Exception as e:
        return str(e)

@app.route('/convert_to_word', methods=['GET'])
def convert_to_word():
    md_filename = request.args.get('filename')
    docx_filename = os.path.splitext(md_filename)[0] + '.docx'

    # 读取 Markdown 文件内容
    with open(md_filename, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 转换为 HTML
    html_content = markdown.markdown(md_content)

    # 创建 Word 文档
    doc = Document()

    # 设置文档样式
    doc.styles['Normal'].font.name = 'Arial'
    doc.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')

    # 将 HTML 内容添加到 Word 文档
    soup = BeautifulSoup(html_content, 'html.parser')
    elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li', 'strong', 'em'])

    for element in elements:
        if element.name.startswith('h'):
            level = int(element.name[1])
            heading = doc.add_heading(level=level)
            heading.add_run(element.get_text()).bold = True
        elif element.name == 'p':
            para = doc.add_paragraph(element.get_text())
        elif element.name in ['ul', 'ol']:
            for li in element.find_all('li'):
                para = doc.add_paragraph()
                run = para.add_run(li.get_text())
                if element.name == 'ul':
                    para.style = 'List Bullet'
                else:
                    para.style = 'List Number'
        elif element.name == 'strong':
            para = doc.add_paragraph()
            run = para.add_run(element.get_text())
            run.bold = True
        elif element.name == 'em':
            para = doc.add_paragraph()
            run = para.add_run(element.get_text())
            run.italic = True

    # 将 Word 文档保存到内存中
    from io import BytesIO
    docx_io = BytesIO()
    doc.save(docx_io)
    docx_io.seek(0)

    # 设置响应头，提示浏览器下载文件
    response = make_response(docx_io.getvalue())
    response.headers.set('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response.headers.set('Content-Disposition', 'attachment', filename=docx_filename)

    return response

@app.route('/save_as_word', methods=['POST'])
def save_as_word():
    data = request.form
    custom_filename = data.get('custom_filename')  # 获取用户自定义的文件名
    content = data.get('content')

    # 创建 Word 文档
    doc = Document()

    # 设置文档样式
    doc.styles['Normal'].font.name = 'Arial'
    doc.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')

    # 转换 Markdown 内容为 HTML
    html_content = markdown.markdown(content)

    # 解析 HTML 并添加到 Word 文档
    soup = BeautifulSoup(html_content, 'html.parser')
    elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li', 'strong', 'em'])

    for element in elements:
        if element.name.startswith('h'):
            level = int(element.name[1])
            heading = doc.add_heading(level=level)
            heading.add_run(element.get_text()).bold = True
        elif element.name == 'p':
            para = doc.add_paragraph(element.get_text())
        elif element.name in ['ul', 'ol']:
            for li in element.find_all('li'):
                para = doc.add_paragraph()
                run = para.add_run(li.get_text())
                if element.name == 'ul':
                    para.style = 'List Bullet'
                else:
                    para.style = 'List Number'
        elif element.name == 'strong':
            para = doc.add_paragraph()
            run = para.add_run(element.get_text())
            run.bold = True
        elif element.name == 'em':
            para = doc.add_paragraph()
            run = para.add_run(element.get_text())
            run.italic = True

    # 保存到 tem 文件夹
    tem_dir = str(config.path_from(__file__, 'mymodel'))
    os.makedirs(tem_dir, exist_ok=True)  # 确保 tem 文件夹存在
    tem_path = os.path.join(tem_dir, f'{custom_filename}.docx')

    try:
        doc.save(tem_path)  # 直接保存到文件
        return jsonify({'status': 'success', 'message': 'File saved successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def md2html(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    html = markdown.markdown(text)
    return Markup(html)

if __name__ == '__main__':
    web.run_flask(app, 5028)