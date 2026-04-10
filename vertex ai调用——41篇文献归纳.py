import os
import time
from google.cloud import storage
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from vertexai.preview import caching

# ==========================================
# [配置区] 个性化边界条件注入
# ==========================================
# 1. 物理网络穿透 (强制 Python 走你的代理)
# 请将 7890 替换为你实际的代理端口
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'

# 2. 数字护照挂载 (指向你刚才下载的 JSON 钥匙的绝对路径)
# Windows 路径示例：C:/Users/Administrator/Desktop/gcp_key.json
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"D:\vertex-article project\gcp_key.json"

# 3. 云端物理坐标
PROJECT_ID = "vertex-ai-491908"
LOCATION = "us-central1"
BUCKET_NAME = "nasicon-ncm"  # 刚才创建的桶名

LOCAL_PDF_DIR = r"D:\vertex-article project\2026.4.8"  # 你放 PDF 的本地文件夹

# ==========================================
# [反应区一]：自动将本地 PDF 推送至云端进料舱 (GCS)
# ==========================================
storage_client = storage.Client(project=PROJECT_ID)
bucket = storage_client.bucket(BUCKET_NAME)
uploaded_uris = []

print(">>> [系统] 开始网络穿透，向 Google Cloud 进料舱推送文献...")
for filename in os.listdir(LOCAL_PDF_DIR):
    if filename.endswith(".pdf"):
        local_path = os.path.join(LOCAL_PDF_DIR, filename)
        blob = bucket.blob(f"cache_input/{filename}")
        blob.upload_from_filename(local_path)

        gcs_uri = f"gs://{BUCKET_NAME}/cache_input/{filename}"
        uploaded_uris.append(gcs_uri)
        print(f"    - 成功上传: {filename} -> {gcs_uri}")

# ==========================================
# [反应区二]：在 Vertex AI 算力集群中活化缓存
# ==========================================
vertexai.init(project=PROJECT_ID, location=LOCATION)
my_cache = None

try:
    print("\n>>> [系统] 正在 GPU 显存中构建百万级 Context Caching...")

    # 将 GCS URI 转化为大模型认识的 Part 对象
    contents = [Part.from_uri(uri, mime_type="application/pdf") for uri in uploaded_uris]

    my_cache = caching.CachedContent.create(
        model_name="gemini-2.5-pro",  # 工业主力模型
        system_instruction=(
            "【全局身份】你是一位拥有极高专业素养的顶尖材料科学与固态电化学数据分析专家。你的核心任务是从海量的高镍正极（NCM）及快离子导体（NASICON）学术文献中，无损且极其严谨地萃取实验数据与物理机理。\n"
            "【绝对红线纪律】\n"
            "1. 零幻觉底线：你的每一次数据提取必须 100% 具备原文物质基础。若原文未提及某参数，强制输出'未找到'，绝对禁止基于物理化学常识进行主观推测或插值。\n"
            "2. 跨尺度剥离：在描述机理时，必须能够穿透表象，直接命中背后的热力学驱动力或动力学限制（如空间电荷层、晶格应力、轨道杂化）。\n"
            "3. 格式绝对刚性：若用户要求 Markdown 表格，你必须保证表格结构完美，且单元格内绝对禁止出现换行符（强制使用分号替代），剥离一切口语化寒暄。"
        ),
        contents=contents,
    )
    print(f">>> [状态] 企业级缓存建立成功！(将按 GCP $300 赠金账单计费)")

    # ==========================================
    # [反应区三]：交叉审问、多级 Token 账本与自动化复查流水线
    # ==========================================
    model = GenerativeModel.from_cached_content(cached_content=my_cache)

    # 建立持续对话通道（拥有上下文记忆）
    chat = model.start_chat()
    # ------------------------------------------
    # 财务模块：初始化全局账本 (Global Ledger)
    # ------------------------------------------
    ledger_cached_in = 0  # 累计命中的缓存 Token (享受极低折扣)
    ledger_new_in = 0  # 累计新增的指令 Token (享受极低折扣)
    ledger_out = 0  # 累计生成的输出 Token (全价计费)


    # 第一轮：自动发送基准 Prompt，生成全局表格
    print("\n>>> [系统] 正在执行首轮全量交叉计算（生成汇总表格），请稍候...")
    prompt_extraction = """
        【任务指令】
        请按文件名排序，遍历并提取缓存中的所有文献数据，建立一个综合性的 Markdown 表格。

        【执行纪律】
        1. 恪守严谨：所有数据必须 100% 源自原文。如果原文无该参数，必须严格填写“未找到”。
        2. 分类阻断：若文献判定为“综述”、“会议”或“非NASICON包覆NCM”，仅提取前三列基本信息，后续字段强制填写“N/A”。
        3. 格式刚性：单元格内部绝对禁止使用回车符/换行符，多项内容强制使用分号 (;) 隔开。

        【表头结构与填写要求（必须严格遵守以下 13 列绝对顺序，绝不可擅自合并或增删列）】
        1. 文献序号：(文件名中带有的：文献x)
        2. 文献名称：(文献标题全称)
        3. 文章类型：(填写：Article / Review / Conference )
        4. 第一作者：(提取第一作者姓名)
        5. 通讯作者：(提取带有星号或明确标注通讯身份的作者姓名，多位用分号隔开)
        6. 通讯单位：(提取通讯作者所属的核心科研机构名称)
        7. 期刊全称：(禁止缩写，提取期刊完整英文名称)
        8. DOI：(提取 DOI 编号)
        9. 主题判定：(填写：是NASICON包覆NCM / 否 / 综述)
        10. 包覆材料化学式
        11. 包覆材料重量占比
        12. 详细包覆工艺：(高度浓缩。格式：环节1(材料用量/设备名称及型号/具体参数和运行条件); 环节2... )
        13. 电池装配配置-正极比例%
        14. 电池装配配置-面容量mAh/cm2
        15. 电池装配配置-面载量mg/cm2)
        16. 电池装配配置-压力Mpa
        17. 电池装配配置-负极物质化学势
        18. 电池装配配置-电解质化学式
        19. 电化学性能-首圈-比容量mAh/g
        20. 电化学性能-首圈-充放电效率%
        21. 电化学性能-倍率：(格式：0.5C=xxxmAh/g；1C=xxxmAh/g；...)
        22. 电化学性能-长循环：(格式：(测试倍率, 圈数, 保持率%))
        23. 核心机制深度解析：(禁止简略泛泛而谈，必须深入具体数据与现象！格式：[测试手段] -> [具体实验现象与数据] -> [推导出的微观机理]。示例：【XRD】充放电过程中(003)峰在高压下往低角度的偏移幅度显著减小 -> 证明包覆层有效抑制了H2到H3的不利相变及c轴塌陷；【XPS/XAS】O 1s谱中晶格氧结合能发生偏移，且观测到P-O-M键的形成 -> 证实包覆层与基体发生界面化学杂化，锚定了表面晶格氧，抑制了高压下的剧烈析氧副反应。)
        """

    response = chat.send_message(prompt_extraction)
    # 将表格写入本地
    with open("Vertex_提取结果_主表.txt", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("\n" + "=" * 50)
    print(">>>[主表生成完毕] 已保存至 'Vertex_提取结果_主表.txt'")

    # [记账] 记录阶段 A 的算力消耗
    usage_A = response.usage_metadata
    ledger_cached_in += usage_A.cached_content_token_count
    ledger_new_in += (usage_A.prompt_token_count - usage_A.cached_content_token_count)
    ledger_out += usage_A.candidates_token_count

    print(f"\n[📊 算力账单 | 阶段 A: 全局成表]")
    print(f" ├─ 命中缓存 (极低折扣): {usage_A.cached_content_token_count} Tokens")
    print(f" ├─ 新增指令 (极低折扣): {usage_A.prompt_token_count - usage_A.cached_content_token_count} Tokens")
    print(f" └─ 模型输出 (全价计费): {usage_A.candidates_token_count} Tokens")
    print("=" * 50)

    # ------------------------------------------
    # 阶段 B：全自动“切片式”溯源复查 (Anti-Hallucination Pass)
    # ------------------------------------------
    print("\n>>> [系统] 启动全量自动化复查流水线 (Data Auditing)...")
    print(">>> 正在为每篇文献单独生成“原文逐字引用”防幻觉报告。")

    # 初始化阶段 B 专属分类账本
    phase_b_cached_in = 0
    phase_b_new_in = 0
    phase_b_out = 0

    # 打开一个新文件，用于追加写入每篇文献的复查报告
    with open("Vertex_防幻觉复查报告.txt", "w", encoding="utf-8") as verify_file:
        verify_file.write("【全量文献交叉验证与原文溯源报告】\n\n")

        # 遍历刚才上传的所有 PDF 文件名，挨个进行极限审问
        for uri in uploaded_uris:
            # 从 GCS 路径中提取纯净的文件名
            doc_name = uri.split("/")[-1]
            print(f"    - 正在复查文献: {doc_name} ...")
            verify_prompt = f"""
                        针对文献 `{doc_name}`，请你在原文中进行强制溯源复查。

                        如果该文献与主题无关或是综述，请回复：“该文献非核心研究，免于复查”。
                        如果是核心研究，请进行【文本与视觉双轨核查】，并严格按以下格式输出：

                        1. 关于【电化学性能】（如循环寿命、首效、倍率等数据）：
                           - 若数据来源于正文文本，请严格摘录“英文原句”。
                           - 若数据来源于图表（Figure）或数据表（Table），请务必明确指出具体的图表编号（如 Figure 3a 充放电曲线），并描述你是如何从图例或坐标轴中视觉读取到该数据的。

                        2. 关于【核心机制深度解析】（测试手段及微观推演）：
                           - 优先摘录原文正文或图注（Caption）中最能支撑该机理的“英文原话”。

                        【防误报纪律】：
                        你拥有阅读图像的能力。不要因为在纯文本中找不到数据就轻易判定为幻觉。只有当“文本中未提及”且“所有图表中也无法读出该数值”时，才允许输出“警告：提取数据可能存在幻觉！”
                        """
            try:
                verify_resp = model.generate_content(verify_prompt)
                # 写入文本文件
                verify_file.write(f"=== 复查对象: {doc_name} ===\n")
                verify_file.write(verify_resp.text + "\n\n" + "-" * 40 + "\n\n")

                # ==========================================
                # [关键修复区]：提取当前文献的 Token 并记入总账
                # ==========================================
                v_usage = verify_resp.usage_metadata

                # 1. 提取本次调用消耗的明细
                current_cached = v_usage.cached_content_token_count
                current_new = v_usage.prompt_token_count - current_cached
                current_out = v_usage.candidates_token_count

                # 2. 物理累加到阶段 B 的总账本中 (这就是你漏掉的步骤)
                phase_b_cached_in += current_cached
                phase_b_new_in += current_new
                phase_b_out += current_out
                # ==========================================

                # 打印单次消耗状态
                print(f"      [复查完成] 消耗 Token -> 输入(含缓存):{v_usage.prompt_token_count} | 输出:{current_out}")

                # 物理延时，防止触发 Vertex AI API 的 RPM 限流墙
                time.sleep(3)

            except Exception as e:
                print(f"    [报错] 复查该文献时发生异常: {e}")
                verify_file.write(f"=== 复查对象: {doc_name} ===\n[系统错误] API 访问异常: {e}\n\n")

    print("\n>>> [系统] 全量自动化复查结束！")
    print(">>> [提示] 溯源证据已保存至 'Vertex_防幻觉复查报告.txt'。")

    # 阶段 B 结束后，将其归入全局总账
    ledger_cached_in += phase_b_cached_in
    ledger_new_in += phase_b_new_in
    ledger_out += phase_b_out

    print(f"\n[📊 算力账单 | 阶段 B: 循环切片复查总计]")
    print(f" ├─ 累计命中缓存 (循环乘数效应折扣): {phase_b_cached_in} Tokens")
    print(f" ├─ 累计新增指令 (常规微量输入折扣): {phase_b_new_in} Tokens")
    print(f" └─ 累计模型输出 (防幻觉提取全价费): {phase_b_out} Tokens")
    print("=" * 50)

    # ------------------------------------------
    # 财务总决算 (Grand Total)
    # ------------------------------------------
    print(f"\n[💰 本次反应釜运行全局总吞吐量 (Grand Total)]")
    print(f" 核心输入总计 (享缓存底价): {ledger_cached_in + ledger_new_in} Tokens")
    print(f" 核心输出总计 (标准全价):   {ledger_out} Tokens")
    print("=" * 50)

    # ------------------------------------------
    # 阶段 C：保留手动交互通道
    # ------------------------------------------
    print("\n" + "=" * 50)
    print(">>>[操作指南] 缓存仍在锁定中。您可以在下方继续手动提问。输入 'exit' 结束并销毁账单。")
    print("=" * 50)

    while True:
        user_query = input("\n[分析师提问] >> ")
        if user_query.strip().lower() in ['exit', 'quit']:
            print(">>> [系统] 收到退出指令，准备释放云端资源...")
            break
        if not user_query.strip():
            continue

        print("[正在查询...]")
        try:
            ans = chat.send_message(user_query)
            print(f"\n[模型回复] -----------------------\n{ans.text}\n----------------------------------")
            print(
                f"[Token 消耗: 输入={ans.usage_metadata.prompt_token_count}(含缓存), 输出={ans.usage_metadata.candidates_token_count}]")
        except Exception as e:
            print(f"\n[报错] 请求失败: {e}")
# ==========================================
# [安全区]：强制物理回收 (防止 $300 赠金被耗干)
# ==========================================
finally:
    print("\n>>> [安全协议] 启动强制垃圾回收...")

    # 1. 销毁缓存 (加入防撞护盾)
    if my_cache:
        try:
            my_cache.delete()
            print("    - [成功] 上下文缓存已主动物理销毁。")
        except Exception as e:
            # 如果报 404，说明已经自动过期，系统静默拦截报错，让程序继续往下走
            print("    - [跳过] 缓存已被云端自动回收 (TTL过期)，无需重复销毁。")

    # 2. 清空 GCS 进料舱 (保证即便缓存销毁失败，这里也必须执行)
    for uri in uploaded_uris:
        try:
            # 提取文件名并删除
            blob_name = uri.split(f"gs://{BUCKET_NAME}/")[1]
            bucket.blob(blob_name).delete()
            print(f"    - [成功] 已从云端彻底删除: {blob_name}")
        except Exception as e:
            print(f"    - [跳过] 云端文件清理异常或已删除: {blob_name}")

    print(">>> [系统结束] 财务止损机制已完美执行完毕，安全退出。")