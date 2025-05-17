# OBS Comment Caster

OBS配信中に、YouTubeライブチャットのコメントをリアルタイムで管理し、選択したコメントを配信画面に表示するためのWebアプリケーションです。

## 機能

- YouTubeライブチャットのリアルタイム取得
- 管理画面でコメントの一覧表示と選択
- 選択したコメントをOBS配信画面にリアルタイムで表示
- WebSocket通信によるリアルタイムな更新
- シンプルで使いやすいUI
- ライブURLの動的設定
- スパチャに応じたカラフルな演出

## 必要要件

- Python 3.8以上
- OBS Studio
- モダンなWebブラウザ（Chrome, Firefox, Safari等）
- YouTube Data API v3のAPIキー

## セットアップ

1. 仮想環境の作成とアクティベート:
```bash
python3 -m venv obs_comment_caster
source obs_comment_caster/bin/activate  # Windows: .\obs_comment_caster\Scripts\activate
```

2. 依存パッケージのインストール:
```bash
pip install -r requirements.txt
```

3. 環境変数の設定:
- `.env.example` を `.env` にコピーし、必要な情報を設定:
```bash
cp .env.example .env
```
- `.env` ファイルを編集し、以下の項目を設定:
  - `YOUTUBE_API_KEY`: YouTubeのAPIキー
  - `SERVER_HOST`: サーバーのホストアドレス（通常はローカルIPアドレス）

## サーバーの管理

### サーバーの起動
```bash
python run.py
```
サーバー起動時に環境変数の設定状態が確認できます。

### サーバーの停止
サーバーを実行しているターミナルで `Ctrl+C` を押してサーバーを停止することができます。

## 使用方法

1. 管理画面へのアクセス:
- ブラウザで `http://localhost:8000/admin` を開く
- コメントの一覧が表示され、クリックで選択可能
- ライブURLを入力して、コメント取得を開始

2. OBSでの設定:
- OBSを起動
- ソースの追加 → 「ブラウザ」を選択
- 以下の設定を行う:
  - URL: `http://localhost:8000/`
  - 幅: 1920（または必要なサイズ）
  - 高さ: 1080（または必要なサイズ）

3. 動作確認:
- 管理画面でコメントをクリックすると、OBS画面に表示
- コメントは自動的にフェードイン/アウト

### トラブルシューティング

- 「Address already in use」エラーが表示される場合:
  1. `lsof -i :8000 | grep LISTEN` で実行中のプロセスを確認
  2. `pkill -f "uvicorn server:app"` で該当プロセスを停止
  3. サーバーを再起動

- コメントが表示されない場合:
  1. `.env`ファイルの設定を確認
  2. YouTubeのAPIキーが有効か確認
  3. 対象の配信がライブ状態か確認
  4. ライブURLが正しいか確認

## 開発者向け情報

### プロジェクト構造
```
OBSCommentCaster/
├── README.md
├── requirements.txt
├── server.py
├── youtube_utils.py
├── config.py
├── run.py
├── .env.example
└── templates/
    ├── admin.html
    └── chat_overlay.html
```

### 使用技術
- バックエンド: FastAPI, YouTube Data API v3
- フロントエンド: HTML/CSS/JavaScript
- 通信: WebSocket
- OBS連携: ブラウザソース

### 設定ファイル

`config.py`で以下の設定を変更できます：
- メッセージ取得間隔（秒）
- 処理済みメッセージの最大保持数
- デフォルトのプロフィール画像URL

## ライセンス

GNU General Public License v3.0 (GPL-3.0)

このソフトウェアは自由ソフトウェアです。GNU General Public License v3.0のもとで再配布および改変が可能です。
詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 注意事項

- このアプリケーションはローカル環境での使用を想定しています
- YouTube Data API v3の利用制限に注意してください
- 本番環境で使用する場合は、適切なセキュリティ対策を実施してください 