from fastapi import HTTPException, status
from typing import Optional
from datetime import datetime

def get_validated_timestamp_bounds(start_dt: Optional[int] = None, end_dt: Optional[int] = None):
    if start_dt is None and end_dt is None:
        return None, None
    try:
        if start_dt is not None:
            assert start_dt > 0
            start_dt = datetime.fromtimestamp(start_dt)
            assert start_dt <= datetime.now()
            assert start_dt >= datetime(2023, 1, 1, 0, 0)
        if end_dt is not None:
            assert end_dt > 0
            end_dt = datetime.fromtimestamp(end_dt)
            assert end_dt <= datetime.now()
            assert end_dt >= datetime(2023, 1, 1, 0, 0)
        if start_dt is not None and end_dt is not None:
            assert start_dt <= end_dt
        return start_dt, end_dt
    except AssertionError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Timestamp bounds were not provided correctly."
        )
