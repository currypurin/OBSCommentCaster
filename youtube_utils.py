from datetime import datetime, timedelta
from typing import Dict, List, Optional
from googleapiclient.errors import HttpError
from config import app_config


class YouTubeAPI:
    def __init__(self, youtube):
        """YouTubeAPIクライアントの初期化"""
        self.youtube = youtube
        self.live_chat_id = None
        self.last_request_time = datetime.now()
        self.processed_message_ids = set()
        self.daily_quota_used = 0
        self.quota_reset_time = datetime.now()
        self.next_page_token = None

    def _update_quota_usage(self, units: int):
        """クォータ使用量を追跡"""
        now = datetime.now()
        if (now - self.quota_reset_time).days >= 1:
            print("クォータ使用量リセット（前回: {}ユニット）".format(self.daily_quota_used))
            self.daily_quota_used = 0
            self.quota_reset_time = now

        self.daily_quota_used += units

        if self.daily_quota_used % 1000 == 0:
            print(f"現在のクォータ使用量: {self.daily_quota_used}ユニット")

    def get_live_chat_id(self, channel_id: Optional[str] = None, video_id: Optional[str] = None) -> Optional[str]:
        """ライブチャットIDを取得"""
        try:
            if video_id:
                request = self.youtube.videos().list(
                    part="liveStreamingDetails,snippet,status",
                    id=video_id,
                    fields="items(id,snippet(title,channelId,channelTitle),status,liveStreamingDetails)"
                )
                response = request.execute()
                self._update_quota_usage(1)

                if response.get("items"):
                    item = response["items"][0]
                    details = item.get("liveStreamingDetails", {})
                    return details.get("activeLiveChatId")

            if channel_id:
                request = self.youtube.search().list(
                    part="id",
                    channelId=channel_id,
                    eventType="live",
                    type="video",
                    maxResults=1
                )
                response = request.execute()
                self._update_quota_usage(100)

                if response.get("items"):
                    video_id = response["items"][0]["id"]["videoId"]
                    return self.get_live_chat_id(video_id=video_id)

            return None

        except HttpError as e:
            if e.resp.status == 403:
                print("クォータ制限に達した可能性があります")
            return None

    def get_live_chat_messages(self) -> List[Dict]:
        """ライブチャットメッセージを取得"""
        if not self.live_chat_id:
            return []

        try:
            time_since_last_request = datetime.now() - self.last_request_time
            if time_since_last_request < timedelta(seconds=app_config.MESSAGE_FETCH_INTERVAL):
                return []

            request = self.youtube.liveChatMessages().list(
                liveChatId=self.live_chat_id,
                part="snippet,authorDetails",
                maxResults=10,
                pageToken=self.next_page_token
            )
            response = request.execute()
            self.last_request_time = datetime.now()
            self._update_quota_usage(1)

            if "items" not in response:
                return []

            # 次のページトークンを保存
            self.next_page_token = response.get("nextPageToken")

            messages = []
            for item in response.get("items", []):
                message_id = item["id"]
                if message_id in self.processed_message_ids:
                    continue

                snippet = item.get("snippet", {})
                msg_type = snippet.get("type", "textMessageEvent")
                is_superchat = msg_type == "superChatEvent"
                superchat_details = snippet.get("superChatDetails", {}) if is_superchat else None

                if "displayMessage" in snippet:
                    message = {
                        "text": snippet["displayMessage"],
                        "author": item["authorDetails"]["displayName"],
                        "timestamp": snippet["publishedAt"],
                        "message_id": message_id,
                        "author_icon": item["authorDetails"].get("profileImageUrl", app_config.DEFAULT_PROFILE_IMAGE),
                        "type": "superchat" if is_superchat else "chat",
                        "superchat": superchat_details
                    }
                    messages.append(message)
                    self.processed_message_ids.add(message_id)

                    if len(self.processed_message_ids) > app_config.MAX_PROCESSED_MESSAGES:
                        self.processed_message_ids = set(list(self.processed_message_ids)[-app_config.MAX_PROCESSED_MESSAGES:])

            return messages

        except HttpError as e:
            if e.resp.status == 403:
                print("クォータ制限に達した可能性があります")
            return []

    def set_live_chat_id(self, chat_id: str):
        """ライブチャットIDを設定"""
        if self.live_chat_id != chat_id:
            self.live_chat_id = chat_id
            self.processed_message_ids.clear()
            self.next_page_token = None
