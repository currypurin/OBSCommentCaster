from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Dict, Optional
import json
import asyncio
import os
from dotenv import load_dotenv
from youtube_utils import YouTubeAPI
from googleapiclient.discovery import build
import base64
import aiohttp
from config import app_config  # 設定を追加
from urllib.parse import urlparse, parse_qs  # 追加

# 環境変数の読み込み
load_dotenv()

app = FastAPI()

# 静的ファイルのマウント
app.mount("/templates", StaticFiles(directory="templates"), name="templates")


# WebSocket接続を管理するクラス
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "admin": [],
            "display": []
        }
        self.selected_comment = None
        self.comments = []  # 最新のコメントを保持するリスト
        self.fetch_task = None  # コメント取得タスクを保持する変数

        # YouTube API の初期化
        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            print("Warning: YOUTUBE_API_KEY not found in environment variables")
            self.youtube_api = None
        else:
            youtube = build('youtube', 'v3', developerKey=api_key)
            self.youtube_api = YouTubeAPI(youtube)
            print("YouTube API initialized with API key")

        self.session = None  # aiohttp session for image fetching

    async def start(self):
        """セッションの初期化"""
        self.session = aiohttp.ClientSession()

    async def stop(self):
        """セッションのクリーンアップ"""
        if self.session:
            await self.session.close()

    async def fetch_and_encode_image(self, url: str) -> Optional[str]:
        """画像をフェッチしてBase64エンコードする"""
        if not url:
            return None
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    base64_image = base64.b64encode(image_data).decode('utf-8')
                    return f"data:image/jpeg;base64,{base64_image}"
                else:
                    print(f"画像の取得に失敗: {response.status}")
                    return None
        except Exception as e:
            print(f"画像の取得中にエラー: {e}")
            return None

    async def connect(self, websocket: WebSocket, client_type: str):
        await websocket.accept()
        self.active_connections[client_type].append(websocket)
        # print(f"New {client_type} connection established. Total {client_type} connections: {len(self.active_connections[client_type])}")

    def disconnect(self, websocket: WebSocket, client_type: str):
        self.active_connections[client_type].remove(websocket)
        # print(f"{client_type} connection closed. Remaining {client_type} connections: {len(self.active_connections[client_type])}")

    async def broadcast_to_displays(self, message: str):
        print(f"Broadcasting to {len(self.active_connections['display'])} display clients")
        for connection in self.active_connections["display"]:
            await connection.send_text(message)

    async def broadcast_to_admins(self, message: str):
        print(f"Broadcasting to {len(self.active_connections['admin'])} admin clients")
        for connection in self.active_connections["admin"]:
            await connection.send_text(message)

    async def fetch_youtube_comments(self):
        """YouTubeのコメントを定期的に取得"""
        while True:
            if self.youtube_api and self.youtube_api.live_chat_id:
                messages = self.youtube_api.get_live_chat_messages()
                if messages:  # messagesが存在する場合のみ処理を行う
                    for message in messages:
                        # アイコンをBase64エンコード
                        base64_icon = await self.fetch_and_encode_image(message.get('author_icon'))
                        message['author_icon'] = base64_icon or app_config.DEFAULT_PROFILE_IMAGE

                        # 表示用クライアントに送信
                        await self.broadcast_to_displays(json.dumps({
                            "type": "chat",
                            "author": message.get('author', ''),
                            "text": message.get('text', ''),
                            "timestamp": message.get('timestamp', ''),
                            "author_icon": message.get('author_icon', '')
                        }))
                        # 管理画面にも送信
                        await self.broadcast_to_admins(json.dumps({
                            "type": "new_comment",
                            "comment": {
                                "author": message.get('author', ''),
                                "text": message.get('text', ''),
                                "timestamp": message.get('timestamp', ''),
                                "message_id": message.get('message_id', ''),
                                "author_icon": message.get('author_icon', '')
                            }
                        }))
            await asyncio.sleep(5)  # 5秒待機

    async def start_fetching_comments(self):
        """コメント取得タスクを開始"""
        if self.fetch_task:
            self.fetch_task.cancel()  # 既存のタスクがあればキャンセル
        self.fetch_task = asyncio.create_task(self.fetch_youtube_comments())

    async def stop_fetching_comments(self):
        """コメント取得タスクを停止"""
        if self.fetch_task:
            self.fetch_task.cancel()
            self.fetch_task = None


manager = ConnectionManager()


@app.on_event("startup")
async def startup_event():
    """サーバー起動時の初期化"""
    await manager.start()  # aiohttp sessionの初期化
    # YouTube APIの初期化のみ行い、コメント取得は開始しない
    if manager.youtube_api:
        print("YouTube API initialized")
    else:
        print("Warning: YouTube API is not configured")


@app.on_event("shutdown")
async def shutdown_event():
    """サーバー終了時のクリーンアップ"""
    await manager.stop()  # aiohttp sessionのクリーンアップ


@app.get("/api/config")
async def get_config():
    """サーバーの設定情報を返す"""
    return {}  # SERVER_HOSTの参照を削除


@app.get("/")
async def get_overlay():
    """オーバーレイ用HTMLを返す"""
    return FileResponse('templates/chat_overlay.html')


@app.get("/admin")
async def get_admin():
    """管理画面用HTMLを返す"""
    return FileResponse('templates/admin.html')


@app.websocket("/ws/admin")
async def websocket_admin_endpoint(websocket: WebSocket):
    await manager.connect(websocket, "admin")
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message.get("type") == "select_comment":
                manager.selected_comment = message.get("comment")
                await manager.broadcast_to_displays(json.dumps({
                    "type": "selected_comment",
                    "comment": manager.selected_comment
                }))
    except WebSocketDisconnect:
        manager.disconnect(websocket, "admin")


@app.websocket("/ws/display")
async def websocket_display_endpoint(websocket: WebSocket):
    await manager.connect(websocket, "display")
    try:
        if manager.selected_comment:
            await websocket.send_text(json.dumps({
                "type": "selected_comment",
                "comment": manager.selected_comment
            }))
        while True:
            await websocket.receive_text()  # キープアライブ
    except WebSocketDisconnect:
        manager.disconnect(websocket, "display")


def extract_video_id_from_url(live_url: str) -> Optional[str]:
    """YouTubeのURLからvideo_idを抽出"""
    try:
        parsed_url = urlparse(live_url)
        # 通常のYouTube URL (例: https://www.youtube.com/watch?v=xxxx)
        if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
            qs = parse_qs(parsed_url.query)
            if "v" in qs:
                return qs["v"][0]
        # 短縮URL (例: https://youtu.be/xxxx)
        if parsed_url.hostname == "youtu.be":
            return parsed_url.path.lstrip("/")
    except Exception as e:
        print(f"URLからvideo_id抽出失敗: {e}")
    return None


@app.post("/api/youtube/set-live-chat")
async def set_live_chat(live_url: str):
    """YouTubeのライブチャットIDを設定"""
    if not manager.youtube_api:
        raise HTTPException(status_code=400, detail="YouTube API is not configured")

    # live_urlからvideo_idを抽出
    video_id = extract_video_id_from_url(live_url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube Live URL")

    # 既存のコメント取得タスクを停止
    await manager.stop_fetching_comments()

    # 新しいライブチャットIDを取得
    chat_id = manager.youtube_api.get_live_chat_id(video_id=video_id)
    if not chat_id:
        raise HTTPException(status_code=404, detail="Live chat not found")

    # ライブチャットIDを設定
    manager.youtube_api.set_live_chat_id(chat_id)

    # コメント取得タスクを開始
    await manager.start_fetching_comments()

    return {"status": "success", "chat_id": chat_id}
