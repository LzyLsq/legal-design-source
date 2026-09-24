import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "shared").is_dir())))

from shared import config, web  # noqa: E402

import os
from flask import request, render_template, send_file, jsonify, redirect, url_for
import markdown
from docx import Document
import pathlib

app = web.create_flask_app(__name__)

# 配置
app.config['DOCS_ROOT'] = str(config.path_from(__file__, 'mymodel'))
app.config['ALLOWED_EXTENSIONS'] = {'md', 'docx'}

# 确保目录存在
os.makedirs(app.config['DOCS_ROOT'], exist_ok=True)

def secure_filename(filename):
    """安全处理文件名"""
    return os.path.basename(filename)

def allowed_file(filename):
    """检查文件扩展名"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# 动态获取文件列表
def get_files():
    files = []
    for root, dirs, filenames in os.walk(app.config['DOCS_ROOT']):
        for filename in filenames:
            if filename.endswith(('.md', '.docx')):
                files.append(os.path.join(root, filename))
    return files

@app.route('/')
def index():
    all_files = get_files()
    return render_template('myindex.html', all_files=all_files)

@app.route('/show_md', methods=['GET'])
def show_md():
    filename = request.args.get('filename')
    if not filename or not allowed_file(filename):
        return "Invalid file or file type not supported", 400

    secure_file = secure_filename(filename)
    file_path = os.path.join(app.config['DOCS_ROOT'], secure_file)

    if not os.path.exists(file_path):
        return "File not found", 404

    file_ext = pathlib.Path(file_path).suffix.lower()
    if file_ext == '.md':
        with open(file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        # 将 Markdown 转换为 HTML
        content = markdown.markdown(md_content)
        return render_template('myshow.html', content=content, filename=secure_file, file_type='md')
    elif file_ext == '.docx':
        doc = Document(file_path)
        content = ""
        for para in doc.paragraphs:
            content += para.text + "\n"
        # 保留 Word 文件的原始排版，将段落分隔符替换为 HTML 标签
        content = content.replace("\n", "<br>")
        return render_template('myshow.html', content=content, filename=secure_file, file_type='docx')
    else:
        return "This file type is not supported for viewing", 400

@app.route('/download', methods=['GET'])
def download():
    filename = request.args.get('filename')
    if not filename:
        return "Filename not provided", 400

    secure_file = secure_filename(filename)
    file_path = os.path.join(app.config['DOCS_ROOT'], secure_file)

    if not os.path.exists(file_path):
        return "File not found", 404

    return send_file(file_path, as_attachment=True)

@app.route('/save_md', methods=['POST'])
def save_md():
    data = request.form
    filename = data.get('filename')
    content = data.get('content')

    if not filename or not content:
        return jsonify({'status': 'error', 'message': 'Missing filename or content'}), 400

    secure_file = secure_filename(filename)
    file_path = os.path.join(app.config['DOCS_ROOT'], secure_file)

    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({'status': 'success', 'message': 'File saved successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/create', methods=['GET'])
def create():
    filename = request.args.get('filename')
    if not filename or not allowed_file(filename):
        return "Invalid file or file type not supported", 400

    secure_file = secure_filename(filename)
    file_path = os.path.join(app.config['DOCS_ROOT'], secure_file)

    if os.path.exists(file_path):
        return "File already exists", 400

    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # 创建文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('')
        return redirect(url_for('show_md', filename=secure_file))
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/rename_file', methods=['POST'])
def rename_file():
    data = request.form
    old_filename = data.get('old_filename')
    new_filename = data.get('new_filename')

    if not old_filename or not new_filename:
        return jsonify({'status': 'error', 'message': 'Missing filenames'}), 400

    secure_old = secure_filename(old_filename)
    secure_new = secure_filename(new_filename)

    old_path = os.path.join(app.config['DOCS_ROOT'], secure_old)
    new_path = os.path.join(app.config['DOCS_ROOT'], secure_new)

    if not os.path.exists(old_path):
        return jsonify({'status': 'error', 'message': 'Old file not found'}), 404

    if os.path.exists(new_path):
        return jsonify({'status': 'error', 'message': 'New file already exists'}), 400

    try:
        os.rename(old_path, new_path)
        return jsonify({'status': 'success', 'message': 'File renamed successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/delete_file', methods=['POST'])
def delete_file():
    data = request.form
    filename = data.get('filename')

    if not filename:
        return jsonify({'status': 'error', 'message': 'Missing filename'}), 400

    secure_file = secure_filename(filename)
    file_path = os.path.join(app.config['DOCS_ROOT'], secure_file)

    if not os.path.exists(file_path):
        return jsonify({'status': 'error', 'message': 'File not found'}), 404

    try:
        os.remove(file_path)
        return jsonify({'status': 'success', 'message': 'File deleted successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    web.run_flask(app, 5030)