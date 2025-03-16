"""
YouTubeAPIの設定ファイル
"""
from dataclasses import dataclass
from os import getenv
from dotenv import load_dotenv


# 環境変数の読み込み
load_dotenv()


# 環境変数から取得する設定
class EnvConfig:
    """環境変数から取得する設定"""
    API_KEY: str = getenv('YOUTUBE_API_KEY', '')
    CHANNEL_ID: str = getenv('YOUTUBE_CHANNEL_ID', '')
    SERVER_HOST: str = getenv('SERVER_HOST', 'localhost')


@dataclass
class AppConfig:
    """アプリケーション固有の設定"""
    # メッセージ取得の間隔（秒）
    MESSAGE_FETCH_INTERVAL: int = 3

    # 処理済みメッセージの最大保持数
    MAX_PROCESSED_MESSAGES: int = 1000

    # デフォルトのプロフィール画像URL
    DEFAULT_PROFILE_IMAGE: str = 'https://yt3.ggpht.com/ytc/default-avatar.jpg'


# グローバル設定インスタンス
env_config = EnvConfig()
app_config = AppConfig()
