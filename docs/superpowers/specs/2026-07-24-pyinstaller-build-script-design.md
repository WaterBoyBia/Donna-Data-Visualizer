# PyInstaller 文件夹版打包脚本设计

## 目标

新增一个 Windows PowerShell 打包脚本，使用现有 `Donna.spec` 和固定的 `donna` Conda 环境，将 Donna 打包为可在 Windows 10/11 64 位电脑上运行的文件夹版程序。目标电脑不需要安装 Python、Conda 或项目依赖。

## 输入与环境

- 项目根目录为脚本所在目录。
- Python 固定使用 `D:\miniconda\envs\donna\python.exe`。
- PyInstaller 使用该环境中已安装的版本。
- 打包配置继续使用现有 `Donna.spec`，不修改其中的固定 Conda 路径。

## 脚本行为

新增根目录脚本 `build.ps1`，依次执行：

1. 切换到脚本所在的项目根目录，避免从其他目录启动时出现相对路径错误。
2. 检查固定 Python、`main.py`、`Donna.spec`、`version.txt` 和 `icon/111.ico` 是否存在。
3. 检查 `PyInstaller`、`matplotlib`、`numpy` 和 `xlrd` 能否由固定 Python 导入。
4. 调用 `python -m PyInstaller --clean --noconfirm Donna.spec`。
5. 检查 `dist/Donna/Donna.exe` 和 `dist/Donna/_internal/` 是否生成。
6. 输出成功位置；任一步骤失败时以非零状态退出并显示明确错误。

## 输出与覆盖规则

- 输出目录：`dist/Donna/`。
- 主程序：`dist/Donna/Donna.exe`。
- 运行依赖：`dist/Donna/_internal/`。
- `--clean --noconfirm` 会清理 PyInstaller 缓存并覆盖旧的 `build/Donna` 和 `dist/Donna` 构建产物。

## 明确排除

- 不创建、删除或修改 ZIP 文件。
- 不修改 `version/` 中的历史发布包。
- 不修改 `Donna.spec` 的 Conda 路径。
- 不执行 Git 暂存、提交、分支或推送操作。
- 不支持 Windows 10/11 64 位以外的目标平台。

## 验证标准

- 使用固定的 `donna` Python 运行环境检查。
- 实际执行脚本后，PyInstaller 返回成功状态。
- `dist/Donna/Donna.exe` 与 `dist/Donna/_internal/` 均存在。
- 打包日志中没有导致构建中止的错误。
