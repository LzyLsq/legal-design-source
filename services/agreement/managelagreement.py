import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "shared").is_dir())))

from flask import jsonify, render_template, request, send_from_directory  # noqa: E402

from shared import config, web  # noqa: E402

app = web.create_flask_app(__name__)

# 配置
app.config['LAWS_DIR'] = str(config.path_from(__file__, 'laws'))
app.config['ALLOWED_EXTENSIONS'] = {'md'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB限制

# 确保目录存在
os.makedirs(app.config['LAWS_DIR'], exist_ok=True)

# 自定义过滤器，用于提取文件名
@app.template_filter('basename')
def basename_filter(path):
    return os.path.basename(path)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def sanitize_filename(filename):
    """
    保留文件名中的特殊符号（如括号和点），同时移除不安全的字符。
    """
    # 允许的字符：字母、数字、中文、.、_、-、（）、空格
    allowed_chars = r"[a-zA-Z0-9\u4e00-\u9fa5\.\_\-\(\)\s]"
    # 使用正则表达式保留允许的字符
    sanitized = re.sub(r"[^{}]+".format(allowed_chars), "", filename)
    return sanitized


def resolve_law_file(filename):
    """把用户输入的文件名解析成 laws 目录内的绝对路径，越界时返回 ``None``。"""
    return config.safe_path(app.config['LAWS_DIR'], filename)


def read_text(file_path):
    """按常见编码依次尝试读取文本文件，全部失败时返回 ``None``。"""
    for encoding in ('utf-8', 'gbk', 'gb18030'):
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return None


@app.route('/')
def index():
    # 获取所有模板文件
    templates = []
    try:
        for root, dirs, files in os.walk(app.config['LAWS_DIR']):
            for file in files:
                if file.endswith('.md'):
                    # 只存储相对于LAWS_DIR的路径
                    rel_path = os.path.relpath(os.path.join(root, file), app.config['LAWS_DIR'])
                    templates.append(rel_path)
    except Exception:
        app.logger.exception("列出模板文件失败")

    return render_template('manage_agreement.html', templates=templates)


@app.route('/add', methods=['POST'])
def add_template():
    # 处理文件上传
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有选择文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'}), 400

    if not (file and allowed_file(file.filename)):
        return jsonify({'success': False, 'message': '只允许上传.md文件'}), 400

    # 保留特殊符号（如括号和点），同时移除不安全的字符
    filename = sanitize_filename(file.filename)
    file_path = resolve_law_file(filename)
    if file_path is None:
        return jsonify({'success': False, 'message': '非法文件路径'}), 403

    # 检查文件是否已存在
    if file_path.exists():
        return jsonify({'success': False, 'message': '文件已存在'}), 400

    try:
        file.save(str(file_path))
        return jsonify({'success': True, 'message': '上传成功', 'filename': filename})
    except Exception:
        app.logger.exception("上传模板失败")
        return jsonify({'success': False, 'message': '上传失败'}), 500


@app.route('/delete/<path:filename>', methods=['POST'])
def delete_template(filename):
    # 处理文件删除
    file_path = resolve_law_file(filename)
    if file_path is None:
        return jsonify({'success': False, 'message': '非法文件路径'}), 403

    try:
        if file_path.exists():
            file_path.unlink()
            return jsonify({'success': True, 'message': '删除成功'})
        return jsonify({'success': False, 'message': '文件不存在'}), 404
    except Exception:
        app.logger.exception("删除模板失败")
        return jsonify({'success': False, 'message': '删除失败'}), 500


@app.route('/view')
def view_template():
    filename = request.args.get('filename')
    if not filename:
        return "缺少文件名参数", 400

    file_path = resolve_law_file(filename)
    if file_path is None:
        return "非法文件路径", 403

    if not file_path.exists():
        return "文件不存在", 404

    content = read_text(file_path)
    if content is None:
        return "无法解码文件内容", 500
    return content


@app.route('/edit/<path:filename>', methods=['GET', 'POST'])
def edit_template(filename):
    file_path = resolve_law_file(filename)
    if file_path is None:
        return jsonify({'success': False, 'message': '非法文件路径'}), 403

    if not file_path.exists():
        return jsonify({'success': False, 'message': '文件不存在'}), 404

    if request.method == 'POST':
        content = request.form.get('content')
        if content is None:
            return jsonify({'success': False, 'message': '内容不能为空'}), 400

        try:
            # 尝试用UTF-8保存，确保中文正常
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return jsonify({'success': True, 'message': '保存成功'})
        except Exception:
            app.logger.exception("保存模板失败")
            return jsonify({'success': False, 'message': '保存失败'}), 500

    # GET请求处理
    content = read_text(file_path)
    if content is None:
        return jsonify({'success': False, 'message': '无法解码文件内容'}), 500
    return jsonify({'success': True, 'content': content})


@app.route('/download/<path:filename>')
def download_template(filename):
    # 构建安全路径
    file_path = resolve_law_file(filename)
    if file_path is None or not file_path.exists():
        return jsonify({'success': False, 'message': '无效文件路径'}), 400

    try:
        return send_from_directory(
            str(file_path.parent),
            file_path.name,
            as_attachment=True,
            download_name=file_path.name
        )
    except Exception:
        app.logger.exception("下载模板失败")
        return jsonify({'success': False, 'message': '下载失败'}), 500


if __name__ == "__main__":
    web.run_flask(app, 5027)
