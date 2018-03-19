from datetime import *

now = datetime.now()
print(now)

timespan = timedelta(seconds=60 * 60)

now = now + timespan

print(now)