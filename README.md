# 🧪 固态电化学文献萃取项目 - 核心控制流备忘录

## 1. 常用终端操作 (Terminal Commands)
*注意：在 PyCharm 底部 Terminal 运行*

- **安装基础运行环境 (拿到新电脑后第一步)**
  `pip install google-cloud-aiplatform google-cloud-storage`
- **导出当前环境图纸 (更新了新库后执行)**
  `pip freeze > requirements.txt`
- **根据图纸一键还原环境 (在新电脑上执行)**
  `pip install -r requirements.txt`

## 2. Git 云端同步核指令 (解决冲突专用)
*注意：日常使用右上角绿色勾和蓝色箭头，仅在报错时使用以下指令*

- **强行用本地宇宙覆盖云端 (Force Push)**
  `git push origin master -f`
- **强行解除 Git 全局网络代理**
  `git config --global --unset http.proxy`
  `git config --global --unset https.proxy`

## 3. 本地网络穿透核对表 (VPN 代理)
- Clash 默认端口: `7890`
- v2ray 默认端口: `10808` 或 `10809`
- **Python 代码硬编码代理写法:**
  `os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'`

## 4. Google Cloud 物理坐标字典
- **存储桶 (Bucket) 区域限定:** `us-central1` (绝对不可选多区域)
- **主力工业模型名称:** `gemini-2.5-pro` (支持百万缓存)
- **最新图谱解析预览版:** `gemini-3.1-pro-preview` 

## 5. 灾难急救协议 (SOS)
- **现象：** Python 报错 `FileNotFoundError` (WinError 3)
  **解法：** 检查路径是否包含中文字符，路径字符串前面是否加了字母 `r`，例如 `r"D:\pdfs"`。
- **现象：** 运行一半强行中断，担心扣费。
  **解法：** 登录 GCP 网页控制台 -> Cloud Storage -> 手动删空桶内的 PDF。缓存会在 60 分钟后自动物理销毁，无需恐慌。