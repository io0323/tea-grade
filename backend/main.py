"""Tea Grade backend API.

FastAPI application providing endpoints to analyze tea images and health check.
This module is formatted to satisfy pylint and provides explicit response models.
"""

import io
import logging
import random
import sys
import traceback

from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

# ロギングの設定を強化
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "Content-Type"],
)

# 茶葉の品種リスト
TEA_VARIETIES = ["やぶきた", "さえみどり", "つゆひかり"]
TEA_GRADES = ["優良", "中等", "低級"]


class AnalyzeResponse(BaseModel):
    """分析結果のレスポンスモデル"""

    variety: str
    grade: str
    confidence: float


class HealthResponse(BaseModel):
    """ヘルスチェックのレスポンスモデル"""

    status: str
    message: str

def optimize_image(image: Image.Image, max_size: tuple[int, int] = (400, 400)) -> Image.Image:
    """画像を最適化する"""
    try:
        logger.debug("画像最適化開始 - 元のサイズ: %s", image.size)

        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            logger.debug("画像をリサイズ - 新しいサイズ: %s", image.size)

        # メモリ使用量を最適化
        if image.mode in ("RGBA", "LA"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
            logger.debug("透過画像をRGBに変換")

        return image
    except Exception as err:  # pylint: disable=broad-except
        logger.error("画像最適化エラー: %s", str(err))
        logger.error(traceback.format_exc())
        raise

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_tea(file: UploadFile = File(...)) -> AnalyzeResponse:
    """茶葉画像を分析する"""
    logger.info("リクエスト受信: %s", file.filename)

    try:
        # ファイルサイズの検証（5MB以下）
        contents = await file.read()
        file_size = len(contents)
        logger.info("ファイルサイズ: %.2fMB", file_size / 1024 / 1024)

        if file_size > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(status_code=400, detail="ファイルサイズは5MB以下にしてください")

        # 画像を読み込む
        try:
            image = Image.open(io.BytesIO(contents))
            logger.debug("画像フォーマット: %s, サイズ: %s, モード: %s", image.format, image.size, image.mode)
        except Exception as err:  # pylint: disable=broad-except
            logger.error("画像読み込みエラー: %s", str(err))
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=400, detail="画像の読み込みに失敗しました") from err

        # 画像フォーマットの検証
        if image.format not in ["JPEG", "PNG"]:
            raise HTTPException(status_code=400, detail="JPEGまたはPNG形式の画像のみ対応しています")

        # 画像の最適化
        try:
            image = optimize_image(image)
        except Exception as err:  # pylint: disable=broad-except
            logger.error("画像最適化エラー: %s", str(err))
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail="画像の最適化に失敗しました") from err

        # モック推論処理
        try:
            variety = random.choice(TEA_VARIETIES)
            grade = random.choice(TEA_GRADES)
            confidence = random.uniform(0.7, 1.0)

            result = AnalyzeResponse(
                variety=variety,
                grade=grade,
                confidence=round(confidence, 3),
            )
            logger.info("分析結果: %s", result.model_dump())

            return result
        except Exception as err:  # pylint: disable=broad-except
            logger.error("推論処理エラー: %s", str(err))
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail="分析処理に失敗しました") from err

    except HTTPException as http_err:
        logger.error("HTTPエラー: %s", str(http_err.detail))
        raise
    except Exception as err:  # pylint: disable=broad-except
        logger.error("予期せぬエラー: %s", str(err))
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="予期せぬエラーが発生しました") from err

@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """ヘルスチェックエンドポイント"""
    logger.debug("ヘルスチェックリクエストを受信")
    try:
        return HealthResponse(status="healthy", message="サーバーは正常に動作しています")
    except Exception as err:  # pylint: disable=broad-except
        logger.error("ヘルスチェックエラー: %s", str(err))
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error") from err
