import time

import uvicorn
from fastapi import FastAPI, APIRouter
from starlette.requests import Request
from starlette.responses import JSONResponse

test_route=APIRouter(prefix="/test")
# 测试接口
@test_route.get('/api/hello')
def hello(request:Request):
    data = request.json() or {}
    name = data.get('name', '未知用户')
    return JSONResponse({
        "code": 200,
        "message": f"你好 {name}！Python HTTP服务已正常响应",
        "timestamp": time.time()
    })

# 健康检查接口
@test_route.get('/api/health')
def health_check():
    return JSONResponse({
        "status": "healthy",
        "service": "python-http-backend",
        "port": 8080
    })

if __name__ == '__main__':

    app=FastAPI()
    app.include_router(test_route)
    uvicorn.run(
        app,
        host='127.0.0.1',
        port=8080
    )