"""
Rate limiting middleware using Redis.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Callable
import redis

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window algorithm."""

    def __init__(self, app, redis_client: redis.Redis = None):
        super().__init__(app)
        self.redis_client = redis_client or redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )
        self.rate_limit_per_minute = settings.RATE_LIMIT_PER_MINUTE
        self.rate_limit_per_hour = settings.RATE_LIMIT_PER_HOUR

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process request with rate limiting.

        Checks both per-minute and per-hour limits.
        """
        # Skip rate limiting for health checks
        if request.url.path.startswith("/api/v1/health"):
            return await call_next(request)

        # Get client identifier (IP address or user ID from token)
        client_id = self._get_client_id(request)

        # Check rate limits
        try:
            self._check_rate_limit(client_id, "minute", self.rate_limit_per_minute, 60)
            self._check_rate_limit(client_id, "hour", self.rate_limit_per_hour, 3600)
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail},
                headers=e.headers,
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit-Minute"] = str(self.rate_limit_per_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.rate_limit_per_hour)

        return response

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request."""
        # Try to get user ID from JWT token if authenticated
        # For now, use IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0]
        return request.client.host if request.client else "unknown"

    def _check_rate_limit(
        self,
        client_id: str,
        window: str,
        limit: int,
        window_seconds: int,
    ):
        """
        Check rate limit for client using sliding window.

        Args:
            client_id: Client identifier
            window: Time window (minute/hour)
            limit: Maximum requests in window
            window_seconds: Window duration in seconds

        Raises:
            HTTPException: If rate limit exceeded
        """
        key = f"rate_limit:{client_id}:{window}"
        now = time.time()

        # Remove old entries outside the window
        self.redis_client.zremrangebyscore(key, 0, now - window_seconds)

        # Count requests in current window
        count = self.redis_client.zcard(key)

        if count >= limit:
            # Get time until oldest entry expires
            oldest = self.redis_client.zrange(key, 0, 0, withscores=True)
            if oldest:
                retry_after = int(window_seconds - (now - oldest[0][1]))
            else:
                retry_after = window_seconds

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)},
            )

        # Add current request
        self.redis_client.zadd(key, {str(now): now})
        self.redis_client.expire(key, window_seconds)
