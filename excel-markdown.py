import pandas as pd
import os

# ==========================================
# [物理坐标配置]
# ==========================================
WORK_DIR = r"D:\vertex-article project"
# 请确保你的 Excel 文件名与下方一致，或自行修改
INPUT_EXCEL = os.path.join(WORK_DIR, "汇总数据.xlsx")
OUTPUT_MD = os.path.join(WORK_DIR, "高维特征矩阵.md")

print(">>> [系统] 启动 Excel 到 Markdown 降维转化引擎...")

try:
    # 1. 强制绝对字符串读取：防止浮点数精度丢失或整数被篡改 (如 1.0 变 1)
    df = pd.read_excel(INPUT_EXCEL, dtype=str)

    # 2. 物理格式清洗：清洗可能导致 Markdown 矩阵崩溃的“剧毒字符”
    # 将所有的 NaN (空白单元格) 强制填充为 "未找到"
    df = df.fillna("未找到")

    # 遍历全表，清洗换行符 (\n) 与管道符 (|)
    for col in df.columns:
        df[col] = df[col].apply(
            lambda x: str(x).replace('\n', ' ; ').replace('|', '\|')
        )

    # 3. 渲染为标准 Markdown 表格结构
    print(f"    - 成功读取矩阵: 共 {df.shape[0]} 行, {df.shape[1]} 列。正在渲染...")
    md_content = df.to_markdown(index=False)

    # 4. 写入本地固态存储
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write("# 固态电化学 NASICON/NCM 全局特征矩阵\n\n")
        f.write(md_content)

    print(f">>> [成功] 转化完成！无损 Markdown 已生成: {OUTPUT_MD}")

except FileNotFoundError:
    print(f"\n[致命错误] 未能在 {WORK_DIR} 找到 Excel 文件，请核对文件名是否为 '汇总数据.xlsx'！")
except Exception as e:
    print(f"\n[系统崩溃] 转化过程中发生未知异常: {e}")