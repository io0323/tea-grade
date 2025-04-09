from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import random
from typing import Dict
from PIL import Image
import io
import logging
import asyncio
from fastapi.responses import JSONResponse
import sys
import traceback

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

def optimize_image(image: Image.Image, max_size: tuple[int, int] = (400, 400)) -> Image.Image:
    """画像を最適化する"""
    try:
        logger.debug(f"画像最適化開始 - 元のサイズ: {image.size}")
        
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            logger.debug(f"画像をリサイズ - 新しいサイズ: {image.size}")
        
        # メモリ使用量を最適化
        if image.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
            logger.debug("透過画像をRGBに変換")
        
        return image
    except Exception as e:
        logger.error(f"画像最適化エラー: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@app.post("/analyze")
async def analyze_tea(file: UploadFile = File(...)) -> Dict:
    """茶葉画像を分析する"""
    logger.info(f"リクエスト受信: {file.filename}")
    
    try:
        # ファイルサイズの検証（5MB以下）
        contents = await file.read()
        file_size = len(contents)
        logger.info(f"ファイルサイズ: {file_size / 1024 / 1024:.2f}MB")
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(status_code=400, detail="ファイルサイズは5MB以下にしてください")
        
        # 画像を読み込む
        try:
            image = Image.open(io.BytesIO(contents))
            logger.debug(f"画像フォーマット: {image.format}, サイズ: {image.size}, モード: {image.mode}")
        except Exception as e:
            logger.error(f"画像読み込みエラー: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=400, detail="画像の読み込みに失敗しました")
        
        # 画像フォーマットの検証
        if image.format not in ['JPEG', 'PNG']:
            raise HTTPException(status_code=400, detail="JPEGまたはPNG形式の画像のみ対応しています")
        
        # 画像の最適化
        try:
            image = optimize_image(image)
        except Exception as e:
            logger.error(f"画像最適化エラー: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail="画像の最適化に失敗しました")
        
        # モック推論処理
        try:
            variety = random.choice(TEA_VARIETIES)
            grade = random.choice(TEA_GRADES)
            confidence = random.uniform(0.7, 1.0)
            
            result = {
                "variety": variety,
                "grade": grade,
                "confidence": round(confidence, 3)
            }
            logger.info(f"分析結果: {result}")
            
            return JSONResponse(content=result)
        except Exception as e:
            logger.error(f"推論処理エラー: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail="分析処理に失敗しました")
            
    except HTTPException as he:
        logger.error(f"HTTPエラー: {str(he.detail)}")
        raise
    except Exception as e:
        logger.error(f"予期せぬエラー: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="予期せぬエラーが発生しました")

@app.get("/health")
async def health_check() -> Dict:
    """ヘルスチェックエンドポイント"""
    logger.debug("ヘルスチェックリクエストを受信")
    try:
        return JSONResponse(
            content={"status": "healthy", "message": "サーバーは正常に動作しています"},
            status_code=200
        )
    except Exception as e:
        logger.error(f"ヘルスチェックエラー: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error") 