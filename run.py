"""
FastAPIサーバーの起動スクリプト
環境変数を確実に読み込み、サーバーを起動します
"""
from dotenv import load_dotenv
import uvicorn
import os


def main():
    # 環境変数を読み込む
    load_dotenv()

    # 重要な環境変数が設定されているか確認
    print("\n=== 環境変数の確認 ===")
    server_host = os.getenv('SERVER_HOST')
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')

    print(f"SERVER_HOST: {server_host or '未設定'}")
    print(f"YOUTUBE_API_KEY: {'設定済み' if youtube_api_key else '未設定'}")
    print("==================\n")

    # サーバーを起動
    print("FastAPIサーバーを起動します...")
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
