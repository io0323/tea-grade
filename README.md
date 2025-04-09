# Tea Grade - 茶葉品質評価システム

茶葉の画像をアップロードすると、AIが品種と等級を判定するWebアプリケーションです。

## 機能

- 茶葉画像のアップロード
- 品種判定（やぶきた、さえみどり、つゆひかり）
- 等級判定（優良、中等、低級）
- 判定結果の信頼度スコア表示
- 画像の最適化処理
- レスポンシブデザイン

## 技術スタック

### フロントエンド
- Next.js 14
- TypeScript
- Tailwind CSS
- Shadcn UI
- Sonner (トースト通知)

### バックエンド
- FastAPI
- Python
- PIL (Python Imaging Library)
- Uvicorn

## セットアップ

### バックエンド

```bash
# 仮想環境のセットアップ
cd backend
python3 -m venv .venv
source .venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt

# サーバーの起動
uvicorn main:app --host 0.0.0.0 --port 3333 --reload
```

### フロントエンド

```bash
# 依存パッケージのインストール
cd frontend
npm install

# 開発サーバーの起動
npm run dev
```

## 使用方法

1. バックエンドサーバーを起動 (http://localhost:3333)
2. フロントエンド開発サーバーを起動 (http://localhost:3001)
3. ブラウザでフロントエンドにアクセス
4. 「クリックして画像を選択」から茶葉の画像をアップロード
5. 分析結果（品種、等級、信頼度）が表示される

## 機能の詳細

### 画像処理
- 最大ファイルサイズ: 5MB
- 対応フォーマット: JPEG, PNG
- 自動リサイズ: 最大400x400px

### 分析結果
- 品種判定: やぶきた、さえみどり、つゆひかり
- 等級判定: 優良、中等、低級
- 信頼度スコア: 0.7 ~ 1.0

## 注意事項

- 現在のバージョンではモック推論処理を実装しており、ランダムな結果を返します
- 実際の画像分類モデルは今後実装予定です
- 開発環境での使用を想定しています

## 開発者向け情報

### APIエンドポイント

- `GET /health` - ヘルスチェック
- `POST /analyze` - 画像分析

### 環境要件

- Node.js 18以上
- Python 3.8以上
- npm 9以上 