import pandas as pd
import os

# 获取当前目录下的所有Excel文件
excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') or f.endswith('.xls')]

print(f"找到 {len(excel_files)} 个Excel文件：")
for i, file in enumerate(excel_files):
    print(f"{i+1}. {file}")

# 分析第一个Excel文件
if excel_files:
    first_file = excel_files[0]
    print(f"\n分析文件：{first_file}")
    
    # 读取Excel文件
    try:
        df = pd.read_excel(first_file)
        print(f"\n工作表名称：{first_file.split('.')[0]}")
        print(f"数据行数：{len(df)}")
        print(f"数据列数：{len(df.columns)}")
        print(f"\n列名：")
        for i, col in enumerate(df.columns):
            print(f"  {i+1}. {col}")
        
        print(f"\n前5行数据：")
        print(df.head())
        
        # 保存列名到文件
        with open('excel_columns.txt', 'w', encoding='utf-8') as f:
            f.write(f"文件：{first_file}\n")
            f.write(f"列数：{len(df.columns)}\n")
            for col in df.columns:
                f.write(f"{col}\n")
        
    except Exception as e:
        print(f"读取文件时出错：{e}")