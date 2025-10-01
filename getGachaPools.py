import requests
import json
import os

def fetch_and_process_gacha_pool(url, output_dir):
    """
    从指定 URL 获取 JSON 数据，并处理 gachaPoolClient 中的每一项。

    Args:
        url (str): 请求 JSON 数据的 URL。
        output_dir (str): 保存 JSON 文件的目标目录。
    """
    try:
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 获取 JSON 数据
        response = requests.get(url)
        response.raise_for_status()  # 检查 HTTP 请求是否成功
        data = response.json()

        # 检查是否有 gachaPoolClient
        gacha_pool_client = data.get("gachaPoolClient")
        if not isinstance(gacha_pool_client, list):
            print("Error: gachaPoolClient 数据格式不正确或不存在")
            return

        # 处理 gachaPoolClient 的每一项
        for item in gacha_pool_client:
            gacha_pool_id = item.get("gachaPoolId")
            gacha_pool_detail = item.get("gachaPoolDetail", {})
            detail_info = gacha_pool_detail.get("detailInfo")

            if gacha_pool_id is None or detail_info is None:
                print(f"Skipping item with missing gachaPoolId or detailInfo: {item}")
                continue

            # 构建保存的内容和文件名
            output_data = {"detailInfo": detail_info}
            file_name = f"{gacha_pool_id}.json"
            file_path = os.path.join(output_dir, file_name)

            # 将数据保存到文件
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, ensure_ascii=False, indent=4)

            print(f"Saved detailInfo to {file_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from URL: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# 示例用法
url = "https://weedy.prts.wiki/gacha_table.json"  # 替换为实际的 URL
output_directory = "data/gacha"  # 替换为实际的保存目录
fetch_and_process_gacha_pool(url, output_directory)
