import time
from collections import defaultdict
from fastapi import Request
from starlette.responses import JSONResponse
from utils.logger import get_access_logger

access_logger = get_access_logger()

class RateLimiter:
    # 일정 시간 내 특정 IP의 요청 횟수를 측정, 초과 시 로그로 남김
    # IP 또는 사용자별로 일정 시간 내 요청 횟수 제한, 초과 시 로그 기록 및 차단 
    
    def __init__(self, requests_per_minute: int = 5): # IP당 허용할 최대 요청 횟수는 1분에 10회 
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list) # 각 IP별로 요청 타임스탬프를 저장 

    async def __call__(self, request: Request, call_next):
        ip = request.client.host
        path = request.url.path
        key = (ip, path)  # IP+경로 조합으로 key 생성
        current_time = time.time()
        
        # 1분 이내 요청만 유지
        self.requests[key] = [t for t in self.requests[key] if current_time - t < 60]

        if len(self.requests[key]) >= self.requests_per_minute:
            access_logger.warning({
                "event": "rate_limit_exceeded",
                "ip": ip,
                "path": path,
                "url": str(request.url),
                "count": len(self.requests[key]),
                "timestamp": current_time
            })
            return JSONResponse(status_code=429, content={"detail": "Too many requests"})

        self.requests[key].append(current_time)
        response = await call_next(request)
        return response



class LoginFailLimiter:
    # 동일 IP/계정의 연속 로그인 실패 횟수 측정, 임계치 초과 시 로그 기록
    
    def __init__(self, max_failures: int = 5, window_seconds: int = 300):
        # IP 또는 계정별 실패 카운트 및 마지막 실패 시각 저장
        self.failed_logins = defaultdict(lambda: {"count": 0, "last_failed": 0})
        self.max_failures = max_failures
        self.window_seconds = window_seconds

    def record_failure(self, key: str):
        now = time.time()
        data = self.failed_logins[key]
        # 최근 실패가 window 내라면 카운트 증가, 아니면 리셋
        if now - data["last_failed"] < self.window_seconds:
            data["count"] += 1
        else:
            data["count"] = 1
        data["last_failed"] = now
        self.failed_logins[key] = data

        if data["count"] >= self.max_failures:
            access_logger.warning({
                "event": "login_fail_limit_exceeded",
                "key": key,
                "fail_count": data["count"],
                "timestamp": now
            })

    def reset(self, key: str):
        if key in self.failed_logins:
            self.failed_logins[key] = {"count": 0, "last_failed": 0}

    def is_limited(self, key: str):
        data = self.failed_logins[key]
        now = time.time()
        # 제한 조건: window 내 실패 횟수 초과
        return (now - data["last_failed"] < self.window_seconds) and (data["count"] >= self.max_failures)