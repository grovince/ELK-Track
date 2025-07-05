import time
from collections import defaultdict
from fastapi import Request
from starlette.responses import JSONResponse
from utils.logger import get_access_logger

access_logger = get_access_logger()

class RateLimiter:
    def __init__(self, requests_per_minute: int = 3): # IP당 허용할 최대 요청 횟수는 1분에 10회 
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list) # 각 IP별로 요청 타임스탬프를 저장 

    async def __call__(self, request: Request, call_next):
        ip = request.client.host
        current_time = time.time()
        
        # 1분 이내 요청만 유지
        self.requests[ip] = [t for t in self.requests[ip] if current_time - t < 60]

        if len(self.requests[ip]) >= self.requests_per_minute:
            access_logger.warning({
                "event": "rate_limit_exceeded",
                "ip": ip,
                "url": str(request.url),
                "count": len(self.requests[ip]),
                "timestamp": current_time
            })
            return JSONResponse(status_code=429, content={"detail": "Too many requests"})

        self.requests[ip].append(current_time)
        response = await call_next(request)
        return response
