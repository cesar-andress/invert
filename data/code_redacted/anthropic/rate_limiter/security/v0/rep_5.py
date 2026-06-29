import anthropic
import time
from collections import deque

def create_rate_limiter():
    client = anthropic.Anthropic()
# REDACTED_CONCURRENCY_PROXY
    message = client.messages.create(model='claude-3-5-sonnet-20241022', max_tokens=1024, messages=[{'role': 'user', 'content': prompt}])
    return message.content[0].text
implementation = create_rate_limiter()
exec(implementation)
if __name__ == '__main__':
    limiter = RateLimiter(max_calls=3, period_seconds=1.0)
    assert limiter.allow() == True, 'First call should be allowed'
    assert limiter.allow() == True, 'Second call should be allowed'
    assert limiter.allow() == True, 'Third call should be allowed'
    assert limiter.allow() == False, 'Fourth call should be denied'
    time.sleep(1.1)
    assert limiter.allow() == True, 'Call after period should be allowed'
    limiter2 = RateLimiter(max_calls=2, period_seconds=0.5)
    assert limiter2.allow() == True
    assert limiter2.allow() == True
    assert limiter2.allow() == False
    time.sleep(0.3)
    assert limiter2.allow() == False
    time.sleep(0.3)
    assert limiter2.allow() == True
    print('All tests passed!')