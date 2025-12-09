# AlphaFold 3 Input Generator

这是一个基于 Web 的工具，用于生成 AlphaFold 3 的 JSON 输入文件 (`af3_input.json`)。它支持从 CIF 模板自动映射结构信息，并提供用户友好的界面来配置蛋白质、配体、RNA 和 DNA 序列及其修饰 (PTM)。

## 功能特点

- **Web 界面**：直观的表单，支持添加多种分子实体（Protein, Ligand, RNA, DNA）。
- **模板自动注入**：上传 CIF 文件，工具会自动解析并根据序列相似度将模板结构注入到对应的蛋白质链中。
- **PTM 支持**：轻松添加翻译后修饰（如 `SEP`, `TPO`, `ALY` 等）。
- **Docker 部署**：提供 Docker 和 Docker Compose 配置，一键部署。
- **默认配置**：自动处理 `modelSeeds` 和格式版本等 AlphaFold 3 特定要求。

## 安装指南

### 方法一：使用 Docker (推荐)

这是最简单的方法，适合在服务器或本地快速运行。

1. **克隆项目**

    ```bash
    git clone https://github.com/ChrisLou-bioinfo/Alphafold3_InputJson_Generater.git
    cd Alphafold3_InputJson_Generater
    ```

2. **启动服务**
    确保已安装 Docker 和 Docker Compose。

    ```bash
    docker-compose up --build -d
    ```

    服务启动后，可以通过浏览器访问：
    `http://localhost:19999` (或者服务器 IP:19999)

3. **停止服务**

    ```bash
    docker-compose down
    ```

### 方法二：本地 Python 运行

如果你想在本地开发环境运行：

1. **环境准备**
    需要 Python 3.8+。

    ```bash
    cd flask_tool
    pip install -r requirements.txt
    ```

2. **运行应用**

    ```bash
    python app.py
    ```

    # AF3 Input JSON Generator — Flask & Docker Setup

    本文档介绍如何在本地或 Docker 环境中部署 `flask_tool`，用于生成 AlphaFold3 的输入 JSON 文件。

    ## 1. 功能概览

    - 通过 Web 表单定义蛋白质、RNA、DNA 以及配体序列，支持修饰信息。
    - 可上传 MMCIF 模板结构，自动将模板嵌入到生成的输入 JSON 中。
    - 支持直接运行 Flask 开发服务器或以 Docker/Gunicorn 方式生产部署。

    ## 2. 仓库结构（必要文件）

    ```text
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

        ```text
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
