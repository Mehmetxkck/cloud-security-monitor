
from datetime import datetime

time1 = "2026-11-21T10:00:00"
time2 = "2026-11-21T10:02:15"

date1 = datetime.fromisoformat(time1)
date2 = datetime.fromisoformat(time2)

difference = date2 - date1

print("Time difference:", difference.total_seconds())
