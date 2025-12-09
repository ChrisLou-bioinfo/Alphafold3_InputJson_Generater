# AF3 Input JSON Generator — Flask & Docker Setup

本文档介绍如何在本地或 Docker 环境中部署 `flask_tool`，用于生成 AlphaFold3 的输入 JSON 文件。

## 1. 功能概览
- 通过 Web 表单定义蛋白质、RNA、DNA 以及配体序列，支持修饰信息。
- 可上传 MMCIF 模板结构，自动将模板嵌入到生成的输入 JSON 中。
- 支持直接运行 Flask 开发服务器或以 Docker/Gunicorn 方式生产部署。

## 2. 仓库结构（必要文件）
```
├── docker-compose.yml            # 将 Flask 应用以 Gunicorn 方式运行（19999 端口）
├── start.sh                      # 本地直接运行 Flask 的快捷脚本
├── DOCKER_AND_FLASK_SETUP.md     # 本文档
└── flask_tool/
    ├── app.py                    # Flask 入口与路由
    ├── util.py                   # 模板链解析与注入逻辑
    ├── requirements.txt          # Python 依赖
    ├── Dockerfile                # 构建镜像所需指令
    └── templates/
        └── index.html            # 前端页面
```

## 3. 运行前准备
- 已安装 **Python 3.9+**（本地运行）或 **Docker 20.10+**（Docker 部署）。
- 推荐使用 macOS/Linux 终端或 WSL2。

---

## 4. 本地直接运行（开发模式）
1. 创建虚拟环境并安装依赖：
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r flask_tool/requirements.txt
   ```
2. 启动应用：
   ```bash
   ./start.sh
   ```
3. 打开浏览器访问 [http://127.0.0.1:19999](http://127.0.0.1:19999)。

> 默认使用 Flask 自带服务器，适合开发调试。若需重新选择端口，可编辑 `flask_tool/app.py` 中的 `app.run(... port=19999)`。

---

## 5. Docker 部署（推荐生产方式）
1. 构建并启动服务：
   ```bash
   docker-compose up -d --build
   ```
2. 浏览器访问 [http://localhost:19999](http://localhost:19999)。
3. 停止服务：
   ```bash
   docker-compose down
   ```

Docker 镜像基于官方 `python:3.9-slim`，使用 Gunicorn 以 4 个 worker 模式运行，适合中等负载。

---

## 6. 更新部署
若已在 Docker 中运行，更新代码后执行：
```bash
./update_docker.sh
```
脚本会依次停止容器、重新构建镜像并在后台启动新容器。

---

## 7. Web 界面使用说明
1. 填写 **Job Name** 与随机种子（可输入逗号分隔的多个整数）。
2. 根据需要添加 `Protein / RNA / DNA / Ligand` 条目：
   - 蛋白/核酸：需要指定链 ID 与序列，可添加修饰信息。
   - 配体：可输入 CCD 代码列表或 SMILES。
3. （可选）上传 MMCIF 模板文件，多文件将逐一尝试匹配链并注入模板。
4. 点击 **Generate JSON** 按钮，浏览器将下载 `JobName.json`。

---

## 8. 常见问题
| 问题 | 解决方案 |
| --- | --- |
| 端口被占用 | 修改 `docker-compose.yml` 或 `app.py` 中的端口配置。 |
| Docker 构建缓慢 | 首次构建需要下载基础镜像，可提前 `docker pull python:3.9-slim`。 |
| 模板未成功注入 | 确认链 ID 或序列匹配是否正确，可查看服务器终端输出日志。 |

---

## 9. 贡献与支持
- 提交 Issue / PR 前，请确保在 `add-flask-and-docker` 分支或其他 feature 分支上工作。
- 欢迎补充更多模板匹配策略或前端功能。

如需进一步帮助，请联系仓库维护者。
