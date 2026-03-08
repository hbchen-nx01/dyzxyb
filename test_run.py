import sys
import os
import traceback

# 添加当前目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

try:
    print("正在导入应用...")
    from app import app
    print("应用导入成功")
    
    # 尝试运行应用
    print("正在启动应用...")
    app.run(debug=True, host='127.0.0.1', port=5001)
except Exception as e:
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {e}")
    print("详细堆栈信息:")
    traceback.print_exc()
