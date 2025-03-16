import os
import asyncio
import time
from dotenv import load_dotenv
from googleapiclient.discovery import build
from youtube_utils import YouTubeAPI
import json


# 環境変数の読み込み
load_dotenv()


async def test_youtube_integration():
    """YouTubeAPI統合テスト"""
    print("=== YouTube API統合テスト開始 ===")

    # APIキーの取得
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("エラー: YOUTUBE_API_KEYが設定されていません")
        return
    print("APIキー: 設定済み")

    # テスト用の動画ID
    video_id = os.getenv("YOUTUBE_VIDEO_ID")
    if not video_id:
        print("エラー: YOUTUBE_VIDEO_IDが設定されていません")
        return
    print(f"テスト対象の動画ID: {video_id}")
    print()

    # 1. YouTubeAPI初期化テスト
    print("1. YouTubeAPI初期化テスト")
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        api = YouTubeAPI(youtube)
        print("✓ APIの初期化に成功しました")
        print()

        # ライブチャットID取得
        print("\n2. ライブチャットID取得テスト")
        chat_id = api.get_live_chat_id(video_id=video_id)
        if chat_id:
            print(f"✓ ライブチャットIDの取得に成功しました: {chat_id}")

            # ライブチャットID設定
            print("\n3. ライブチャットID設定テスト")
            api.set_live_chat_id(chat_id)
            print("✓ ライブチャットIDの設定に成功しました")

            # コメント取得（5回試行）
            print("\n4. ライブチャットメッセージ取得テスト")
            for i in range(5):
                print(f"\n試行 {i+1}/5:")
                messages = api.get_live_chat_messages()
                print(f"取得したメッセージ数: {len(messages)}")
                if messages:
                    print("最新のメッセージ:")
                    print(json.dumps(messages[0], indent=2, ensure_ascii=False))
                else:
                    print("現在メッセージはありません")
                time.sleep(3)  # 3秒待機
        else:
            print("! ライブチャットIDの取得に失敗しました")

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    asyncio.run(test_youtube_integration())
