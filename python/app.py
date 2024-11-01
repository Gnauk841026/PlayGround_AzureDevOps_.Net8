from fastapi import FastAPI
import boto3
import subprocess
import zipfile
import os

# 初始化 FastAPI 應用
app = FastAPI()

# AWS S3 客戶端配置 (使用環境變數)
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

# 設置一些常量
BUCKET_NAME = "demo-bucket-20240930"  # 替換為你的 S3 bucket 名稱
DOWNLOAD_PATH = "/home/Demo"  # 本地下載的文件路徑
EXTRACT_PATH = "/home/Demo/app"  # 文件解壓縮到的目標路徑
SERVICE_NAME = "your_web_service"    # .Net 8 網頁的服務名
DLL_PATH = "/home/Demo/app/MyWebApp.dll"  # 需要運行的 .NET DLL 文件的路徑


def get_latest_file_key():
    # 獲取 S3 bucket 中最新的文件
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    all_files = sorted(response.get('Contents', []), key=lambda x: x['LastModified'], reverse=True)
    if len(all_files) > 0:
        return all_files[0]['Key']
    return None


def get_second_latest_file_key():
    # 獲取 S3 bucket 中第二新的文件
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    all_files = sorted(response.get('Contents', []), key=lambda x: x['LastModified'], reverse=True)
    if len(all_files) > 1:
        return all_files[1]['Key']
    return None


@app.post("/first")
def deploy_latest():
    try:
        # Step 1: 從 S3 下載最新檔案
        latest_file_key = get_latest_file_key()
        if not latest_file_key:
            return {"error": "未找到最新的檔案"}
        s3.download_file(BUCKET_NAME, latest_file_key, DOWNLOAD_PATH)
        print(f"檔案已下載到 {DOWNLOAD_PATH}")

        # Step 2: 停止 .Net 8 網頁服務
        subprocess.run(['systemctl', 'stop', SERVICE_NAME], check=True)
        print(f"服務 {SERVICE_NAME} 已停止")

        # Step 3: 解壓縮下載的檔案到目標路徑
        with zipfile.ZipFile(DOWNLOAD_PATH, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_PATH)
        print(f"檔案已解壓縮到 {EXTRACT_PATH}")

        # Step 4: 執行 .NET DLL 文件
        subprocess.run(['dotnet', DLL_PATH], check=True)
        print(f".NET DLL {DLL_PATH} 已成功執行")

        return {"message": "最新版本部署流程已成功完成"}
    except subprocess.CalledProcessError as e:
        print(f"命令執行失敗: {e}")
        return {"error": f"命令執行失敗: {e}"}
    except Exception as e:
        print(f"發生錯誤: {e}")
        return {"error": f"發生錯誤: {e}"}


@app.post("/rollback")
def rollback_to_second_latest():
    try:
        # Step 1: 從 S3 下載第二新檔案
        second_latest_file_key = get_second_latest_file_key()
        if not second_latest_file_key:
            return {"error": "未找到第二新的檔案"}
        s3.download_file(BUCKET_NAME, second_latest_file_key, DOWNLOAD_PATH)
        print(f"檔案已下載到 {DOWNLOAD_PATH}")

        # Step 2: 停止 .Net 8 網頁服務
        subprocess.run(['systemctl', 'stop', SERVICE_NAME], check=True)
        print(f"服務 {SERVICE_NAME} 已停止")

        # Step 3: 解壓縮下載的檔案到目標路徑
        with zipfile.ZipFile(DOWNLOAD_PATH, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_PATH)
        print(f"檔案已解壓縮到 {EXTRACT_PATH}")

        # Step 4: 執行 .NET DLL 文件
        subprocess.run(['dotnet', DLL_PATH], check=True)
        print(f".NET DLL {DLL_PATH} 已成功執行")

        return {"message": "回滾到第二新版本流程已成功完成"}
    except subprocess.CalledProcessError as e:
        print(f"命令執行失敗: {e}")
        return {"error": f"命令執行失敗: {e}"}
    except Exception as e:
        print(f"發生錯誤: {e}")
        return {"error": f"發生錯誤: {e}"}