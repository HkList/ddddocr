from fastapi import FastAPI
import ddddocr
import onnxruntime
import requests
import uvicorn
import time

onnxruntime.set_default_logger_severity(3)
ocr = ddddocr.DdddOcr()
app = FastAPI()


@app.get("/")
def get_baidu_vcode(type="sharedownload", vcode_str=None):
    if type == "sharedownload":
        return handleSharedownload()
    elif type == "login":
        return handleLogin(vcode_str)
    else:
        return {"code": 400, "message": "请求参数错误", "data": None}


def handleSharedownload():
    while True:
        # 获取百度验证码信息
        try:
            api_resp = requests.get(
                "https://pan.baidu.com/api/getvcode?prod=pan", timeout=30
            )
            data = api_resp.json()
        except:
            return {"code": 500, "message": "请求百度网盘接口超时", "data": None}

        if "vcode" not in data or "img" not in data:
            return {"code": 500, "message": "请求百度网盘接口失败", "data": data}

        vcode_str = data["vcode"]
        vcode_img_url = data["img"]

        # 下载验证码图片
        try:
            img_resp = requests.get(vcode_img_url, timeout=30)
        except:
            return {"code": 500, "message": "验证码图片下载失败", "data": None}

        if img_resp.status_code != 200:
            return {"code": 500, "message": "验证码图片下载失败", "data": None}

        # 识别验证码
        image_bytes = img_resp.content
        result = ocr.classification(image_bytes)
        if len(result) == 4:
            return {
                "code": 200,
                "message": "请求成功",
                "data": {"vcode_str": vcode_str, "vcode_input": result},
            }


def handleLogin(vcode_str):
    while True:
        if not vcode_str:
            return {"code": 400, "message": "请求参数错误", "data": None}

        # 下载验证码图片
        try:
            timestamp = int(time.time() * 1000)
            img_resp = requests.get(
                f"https://wappass.baidu.com/cgi-bin/genimage?{vcode_str}&v={timestamp}",
                timeout=30,
            )
        except:
            return {"code": 500, "message": "验证码图片下载失败", "data": None}

        if img_resp.status_code != 200:
            return {"code": 500, "message": "验证码图片下载失败", "data": None}

        # 识别验证码
        image_bytes = img_resp.content
        result = ocr.classification(image_bytes)
        if len(result) == 4:
            return {
                "code": 200,
                "message": "请求成功",
                "data": {"vcode_str": vcode_str, "vcode_input": result},
            }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
