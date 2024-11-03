from flask import Flask, jsonify
import boto3
import os
import zipfile
import subprocess

app = Flask(__name__)

# S3 設置
BUCKET_NAME = 'demo-bucket-20240930'
DOWNLOAD_PATH = '/home/Demo/App'  # 下載並解壓的目標路徑

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# 初始化 S3 客戶端
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def get_sorted_files():
    # 列出 S3 中所有物件
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
    
    if 'Contents' not in response:
        print("Bucket is empty.")
        return []

    # 根據最後修改時間排序，最近的在前
    return sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)

def stop_running_app():
    try:
        # 使用 ps 查找進程 ID，並關閉應用
        ps_command = "ps aux | grep '[d]otnet .*MyWebApp.dll' | awk '{print $2}'"
        pid = subprocess.check_output(ps_command, shell=True).decode().strip()

        if pid:
            kill_command = f"sudo kill {pid}"
            subprocess.run(kill_command, shell=True)
            print("Application stopped successfully.")
        else:
            print("No running application found.")
    except subprocess.CalledProcessError as e:
        print("Failed to stop application:", e)

def download_and_install(file_key):
    try:
        # 1. 停止正在運行的應用
        stop_running_app()

        # 定義本地下載的路徑
        artifact_local_path = os.path.join(DOWNLOAD_PATH, 'artifact.zip')

        # 2. 從 S3 下載指定的 Artifact
        s3_client.download_file(BUCKET_NAME, file_key, artifact_local_path)

        # 3. 解壓縮文件
        with zipfile.ZipFile(artifact_local_path, 'r') as zip_ref:
            zip_ref.extractall(DOWNLOAD_PATH)

        # 4. 執行 .NET 程式 (假設主程式為 MyWebApp.dll)
        start_command = f"$HOME/dotnet/dotnet {os.path.join(DOWNLOAD_PATH, 'MyWebApp.dll')}"
        result = subprocess.run(start_command, shell=True, capture_output=True, text=True)

        return {
            "message": "Artifact downloaded, extracted, and application executed successfully.",
            "output": result.stdout
        }

    except Exception as e:
        return {"error": str(e)}

@app.route('/install-latest', methods=['POST'])
def install_latest():
    sorted_files = get_sorted_files()
    if not sorted_files:
        return jsonify({"error": "No files found in S3 bucket"}), 404

    latest_file = sorted_files[0]
    response = download_and_install(latest_file['Key'])
    return jsonify(response)

@app.route('/install-second-latest', methods=['POST'])
def install_second_latest():
    sorted_files = get_sorted_files()
    if len(sorted_files) < 2:
        return jsonify({"error": "Less than two files found in S3 bucket"}), 404

    second_latest_file = sorted_files[1]
    response = download_and_install(second_latest_file['Key'])
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)