# OBS Comment Caster

OBS配信中に、コメントをリアルタイムで管理し、選択したコメントを配信画面に表示するためのWebアプリケーションです。

## 機能

- 管理画面でコメントの一覧表示と選択
- 選択したコメントをOBS配信画面にリアルタイムで表示
- WebSocket通信によるリアルタイムな更新
- シンプルで使いやすいUI

## 必要要件

- Python 3.8以上
- OBS Studio
- モダンなWebブラウザ（Chrome, Firefox, Safari等）

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

## 使用方法

1. サーバーの起動:
```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

2. 管理画面へのアクセス:
- ブラウザで http://localhost:8000/static/admin.html を開く
- コメントの一覧が表示され、クリックで選択可能

3. OBSでの設定:
- OBSを起動
- ソースの追加 → 「ブラウザ」を選択
- 以下の設定を行う:
  - URL: `http://localhost:8000/static/display.html`
  - 幅: 1920（または必要なサイズ）
  - 高さ: 1080（または必要なサイズ）

4. 動作確認:
- 管理画面でコメントをクリックすると、OBS画面に表示
- コメントは自動的にフェードイン/アウト

## 開発者向け情報

### プロジェクト構造
```
OBSCommentCaster/
├── README.md
├── requirements.txt
├── server.py
└── static/
    ├── admin.html
    └── display.html
```

### 使用技術
- バックエンド: FastAPI
- フロントエンド: HTML/CSS/JavaScript
- 通信: WebSocket

## ライセンス

MIT License

## 注意事項

- このアプリケーションはローカル環境での使用を想定しています
- 本番環境で使用する場合は、適切なセキュリティ対策を実施してください 