import time
import sys
sys.path.append('/opt/ops-workload-framework/heat_workload/tools')
from stopwatch import Stopwatch
def countdown(n):
    while n > 0:
        n -= 1
        time.sleep(1)

# Use 1: Explicit start/stop
t = Stopwatch()
t.start()
countdown(30)
print t.time_elapsed
t.stop()
