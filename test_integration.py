import os
import asyncio
from dotenv import load_dotenv
from googleapiclient.discovery import build
from youtube_utils import YouTubeAPI
import json
import logging

# ロガーの設定
logger = logging.getLogger(__name__)

# 環境変数の読み込み
load_dotenv()


async def test_youtube_integration():
    """YouTubeAPI統合テスト"""
    logger.info("=== YouTube API統合テスト開始 ===")

    # APIキーの取得
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        logger.error("エラー: YOUTUBE_API_KEYが設定されていません")
        return
    logger.info("APIキー: 設定済み")

    # テスト用の動画ID
    video_id = os.getenv("YOUTUBE_VIDEO_ID")
    if not video_id:
        logger.error("エラー: YOUTUBE_VIDEO_IDが設定されていません")
        return
    logger.info(f"テスト対象の動画ID: {video_id}")

    # 1. YouTubeAPI初期化テスト
    logger.info("1. YouTubeAPI初期化テスト")
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        api = YouTubeAPI(youtube)
        logger.info("✓ APIの初期化に成功しました")

        # ライブチャットID取得
        logger.info("2. ライブチャットID取得テスト")
        chat_id = api.get_live_chat_id(video_id=video_id)
        if chat_id:
            logger.info(f"✓ ライブチャットIDの取得に成功しました: {chat_id}")

            # ライブチャットID設定
            logger.info("3. ライブチャットID設定テスト")
            api.set_live_chat_id(chat_id)
            logger.info("✓ ライブチャットIDの設定に成功しました")

            # コメント取得（5回試行）
            logger.info("4. ライブチャットメッセージ取得テスト")
            for i in range(5):
                logger.info(f"試行 {i+1}/5:")
                messages = api.get_live_chat_messages()
                logger.info(f"取得したメッセージ数: {len(messages)}")
                if messages:
                    logger.info("最新のメッセージ:")
                    logger.info(json.dumps(messages[0], indent=2, ensure_ascii=False))
                else:
                    logger.info("現在メッセージはありません")
                await asyncio.sleep(3)  # 3秒待機
        else:
            logger.warning("! ライブチャットIDの取得に失敗しました")

    except Exception as e:
        logger.error(f"エラーが発生しました: {str(e)}")

    logger.info("=== テスト完了 ===")

if __name__ == "__main__":
    asyncio.run(test_youtube_integration())
