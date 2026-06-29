# app.py
import sys
import io
# 强制标准输出为 UTF-8，避免中文编码错误 (Windows 环境)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from flask import Flask, request, jsonify
from flask_cors import CORS
from cihai.core import Cihai

app = Flask(__name__)
CORS(app)

# --- 初始化 cihai ---
print("⏳ 正在初始化 cihai...")
c = Cihai()
if not c.unihan.is_bootstrapped:
    print("⏳ 首次使用，正在下载 Unihan 数据库 (约 50MB)，请耐心等待...")
    c.unihan.bootstrap()
    print("✅ 数据库下载完成！")
print("✅ cihai 初始化完成！")

# --- 核心查询函数 ---
def get_cangjie_code(char):
    """从本地 Unihan 数据库查询仓颉码"""
    try:
        results = c.unihan.lookup_char(char)
        for glyph in results:
            if hasattr(glyph, 'kCangjie') and glyph.kCangjie:
                return glyph.kCangjie
        return None
    except Exception as e:
        print(f"查询出错: {e}")
        return None

# --- Flask 路由 ---
@app.route('/cangjie', methods=['GET'])
def get_cangjie():
    char = request.args.get('char', '')
    if not char or len(char) != 1:
        return jsonify({'error': '请提供单个中文字'}), 400

    code = get_cangjie_code(char)
    if code:
        return jsonify({'char': char, 'code': code})
    else:
        # 如果查不到，返回 '未收录'
        return jsonify({'char': char, 'code': '未收录'})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)