import json
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    """自定义编码器"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
