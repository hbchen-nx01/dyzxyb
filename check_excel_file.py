import pandas as pd
import os

def check_excel_file():
    """检查Excel文件的完整性和格式"""
    file_path = 'test_equipment.xlsx'
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return False
    
    print(f"文件存在: {file_path}")
    print(f"文件大小: {os.path.getsize(file_path)} bytes")
    
    try:
        # 尝试用openpyxl打开.xlsx文件
        print("尝试用openpyxl打开文件...")
        df = pd.read_excel(file_path, engine='openpyxl')
        print("文件可以正常打开")
        print(f"表格行数: {df.shape[0]}")
        print(f"表格列数: {df.shape[1]}")
        print("列名:")
        for col in df.columns:
            print(f"  - {col}")
        
        print("\n前5行数据:")
        print(df.head())
        
        return True
    except Exception as e:
        print(f"打开文件失败: {e}")
        return False

if __name__ == "__main__":
    check_excel_file()