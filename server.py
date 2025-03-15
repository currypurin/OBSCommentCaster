from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from typing import List, Dict
import json
from datetime import datetime
import asyncio

app = FastAPI()

# 静的ファイルのマウント
app.mount("/static", StaticFiles(directory="static"), name="static")

# WebSocket接続を管理するクラス
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "admin": [],
            "display": []
        }
        self.selected_comment = None
        self.comments = []  # 最新のコメントを保持するリスト

    async def connect(self, websocket: WebSocket, client_type: str):
        await websocket.accept()
        self.active_connections[client_type].append(websocket)

    def disconnect(self, websocket: WebSocket, client_type: str):
        self.active_connections[client_type].remove(websocket)

    async def broadcast_to_displays(self, message: str):
        for connection in self.active_connections["display"]:
            await connection.send_text(message)

    async def broadcast_to_admins(self, message: str):
        for connection in self.active_connections["admin"]:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/admin")
async def websocket_admin_endpoint(websocket: WebSocket):
    await manager.connect(websocket, "admin")
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message.get("type") == "select_comment":
                manager.selected_comment = message.get("comment")
                # 選択されたコメントを表示画面に送信
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

# テスト用のダミーコメント追加エンドポイント
@app.post("/api/add_comment")
async def add_comment(comment: dict):
    manager.comments.append({
        "text": comment["text"],
        "timestamp": datetime.now().isoformat()
    })
    # 管理画面に新しいコメントを通知
    await manager.broadcast_to_admins(json.dumps({
        "type": "new_comment",
        "comment": comment
    }))
    return {"status": "success"}
