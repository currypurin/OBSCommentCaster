"""
YouTubeAPIの設定ファイル
"""
from dataclasses import dataclass
from os import getenv
from dotenv import load_dotenv
import logging
import sys


# 環境変数の読み込み
load_dotenv()


def setup_logging():
    """ログ設定の初期化"""
    # ログレベルの設定（環境変数で制御可能）
    log_level = getenv('LOG_LEVEL', 'INFO').upper()
    
    # ログフォーマットの設定
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # 既存のハンドラーをクリア
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # コンソールハンドラーの設定
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level, logging.INFO))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # uvicornのログレベルも調整
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    return root_logger


# ログ設定の初期化
setup_logging()


# 環境変数から取得する設定
class EnvConfig:
    """環境変数から取得する設定"""
    API_KEY: str = getenv('YOUTUBE_API_KEY', '')
    CHANNEL_ID: str = getenv('YOUTUBE_CHANNEL_ID', '')
    DEBUG: bool = getenv('DEBUG', 'false').lower() == 'true'


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
