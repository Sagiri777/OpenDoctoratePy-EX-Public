import subprocess
import os
import shutil
import stat
from datetime import datetime
import sys
from pathlib import Path

# 确保脚本在正确的目录下运行
SCRIPT_DIR = Path(__file__).resolve().parent
os.chdir(SCRIPT_DIR)

# 定义存储库信息 - 使用绝对路径
repositories = [
    ["https://github.com/Kengxxiao/ArknightsGameData.git", "zh_CN", str(SCRIPT_DIR / "data")],
    ["https://github.com/yuanyan3060/ArknightsGameResource.git", "", str(SCRIPT_DIR / "data")],
    #["https://github.com/ArknightsAssets/ArknightsGamedata.git", "cn", str(SCRIPT_DIR / "data")],
    ["https://github.com/FlandiaYingman/ArknightsGameDataComposite.git", "zh_CN", str(SCRIPT_DIR / "data")],
    ["https://github.com/fexli/ArknightsResource.git", "", str(SCRIPT_DIR / "data")],
]

def safety_check():
    """检查工作目录和关键文件夹"""
    # 确保我们在正确的目录
    if not (SCRIPT_DIR / "config").exists():
        print("错误：未在正确的工作目录中！")
        print(f"当前目录: {os.getcwd()}")
        print(f"期望目录: {SCRIPT_DIR}")
        sys.exit(1)
    
    # 检查是否有重要文件夹
    important_dirs = ["server", "config"]
    for dir_name in important_dirs:
        if (SCRIPT_DIR / dir_name).exists():
            print(f"检测到重要文件夹: {dir_name}")

def backup_directory(path):
    """创建目录的备份"""
    if os.path.exists(path):
        backup_name = f"{path}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copytree(path, backup_name)
        return backup_name
    return None

def create_tmp_directory():
    """创建临时目录"""
    if os.path.exists("tmp"):
        shutil.rmtree("tmp", onerror=lambda func, path, exc_info: (os.chmod(path, stat.S_IWUSR), func(path)))
    os.makedirs("tmp", exist_ok=True)

# 运行安全检查
print("正在进行安全检查...")
safety_check()

# 显示选项并获取用户输入
print("\n请选择要下载的仓库：")
for i, repo in enumerate(repositories):
    print(f"{i}. {repo[0]}")
print("q. 退出程序")

user_input = input("请输入选项编号：").strip().lower()
if user_input == 'q':
    sys.exit(0)

try:
    user_choice = int(user_input)
    if user_choice < 0 or user_choice >= len(repositories):
        raise ValueError
except ValueError:
    print("无效的选择，请重新运行程序并输入正确的选项。")
    sys.exit(1)

# 获取仓库信息
repo_url, sub_path, target_dir = repositories[user_choice]

# 设置代理环境
env = os.environ.copy()
env["http_proxy"] = "http://127.0.0.1:20122"
env["https_proxy"] = "http://127.0.0.1:20122"

# 准备路径
git_path = f"{sub_path}/gamedata/excel/" if sub_path else "gamedata/excel/"
target_excel_path = os.path.join(target_dir, "excel")

try:
    # 初始化备份路径
    backup_path = None
    # 创建临时目录
    create_tmp_directory()
    
    print("正在克隆仓库...")
    result = subprocess.run(
        [
            "git", "clone",
            "-n", "--depth=1", "--filter=tree:0",
            repo_url, "tmp"
        ],
        env=env,
        check=True,
        capture_output=True,
        text=True
    )

    print("设置稀疏检出...")
    # 初始化临时仓库的 sparse-checkout
    result = subprocess.run(
        [
            "git", "config", "core.sparseCheckout", "true"
        ],
        cwd="tmp",
        env=env,
        check=True,
        capture_output=True,
        text=True
    )
    
    # 写入 sparse-checkout 配置文件
    sparse_checkout_file = os.path.join("tmp", ".git", "info", "sparse-checkout")
    with open(sparse_checkout_file, "w") as f:
        f.write(git_path)

    print("检出文件...")
    result = subprocess.run(
        [
            "git", "checkout"
        ],
        cwd="tmp",
        env=env,
        check=True,
        capture_output=True,
        text=True
    )

    # 检查文件是否下载成功
    excel_source = os.path.join("tmp", sub_path, "gamedata", "excel") if sub_path else os.path.join("tmp", "gamedata", "excel")
    if not os.path.isdir(excel_source):
        raise Exception(f"下载的文件夹 {excel_source} 不存在")

    # 创建目标目录（如果不存在）
    os.makedirs(target_dir, exist_ok=True)

    # 备份现有的excel文件夹
    backup_path = None
    if os.path.exists(target_excel_path):
        print("正在创建备份...")
        backup_path = backup_directory(target_excel_path)
        print(f"备份已创建在：{backup_path}")

    # 删除现有的excel文件夹并移动新文件
    print("正在更新文件...")
    if os.path.exists(target_excel_path):
        shutil.rmtree(target_excel_path, onerror=lambda func, path, exc_info: (os.chmod(path, stat.S_IWUSR), func(path)))
    shutil.move(excel_source, target_excel_path)

    print("清理临时文件...")
    shutil.rmtree("tmp", onerror=lambda func, path, exc_info: (os.chmod(path, stat.S_IWUSR), func(path)))

    print("更新完成！")
    if backup_path:
        print(f"如果需要恢复备份，请使用：{backup_path}")

except Exception as e:
    print(f"发生错误：{str(e)}")
    if 'backup_path' in locals() and backup_path:
        print(f"正在恢复备份...")
        if os.path.exists(target_excel_path):
            shutil.rmtree(target_excel_path)
        shutil.move(backup_path, target_excel_path)
        print("备份已恢复")
    if os.path.exists("tmp"):
        shutil.rmtree("tmp", onerror=lambda func, path, exc_info: (os.chmod(path, stat.S_IWUSR), func(path)))
    sys.exit(1)