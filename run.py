"""
FastAPIサーバーの起動スクリプト
環境変数を確実に読み込み、サーバーを起動します
"""
from dotenv import load_dotenv
import uvicorn
import os
import logging

# ロガーの設定
logger = logging.getLogger(__name__)


def main():
    # 環境変数を読み込む
    load_dotenv()

    # 重要な環境変数が設定されているか確認
    logger.info("=== 環境変数の確認 ===")
    server_host = os.getenv('SERVER_HOST')
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')

    logger.info(f"SERVER_HOST: {server_host or '未設定'}")
    logger.info(f"YOUTUBE_API_KEY: {'設定済み' if youtube_api_key else '未設定'}")
    if youtube_api_key:
        logger.info(f"YOUTUBE_API_KEY: ***{youtube_api_key[-5:]}")
    logger.info("==================")

    # サーバーを起動
    logger.info("FastAPIサーバーを起動します...")
    logger.info("=== アクセスURL ===")
    logger.info("管理画面: http://localhost:8000/admin")
    logger.info("オーバーレイ: http://localhost:8000/")
    logger.info("==================")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
