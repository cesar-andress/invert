from anthropic import Anthropic
client = Anthropic()
conversation_history = []

def chat(user_message):
    conversation_history.append({'role': 'user', 'content': user_message})
    response = client.messages.create(model='claude-3-5-sonnet-20241022', max_tokens=8096, system='You are a Python programming expert. When asked to implement code, \nprovide only valid, working Python code without any markdown formatting, explanations, \nor text outside the code. The code should be production-ready and follow best practices.', messages=conversation_history)
    assistant_message = response.content[0].text
    conversation_history.append({'role': 'assistant', 'content': assistant_message})
    return assistant_message

def main():
    print('Turn 1: Requesting LRUCache implementation...')
# REDACTED_CONCURRENCY_PROXY
    print("Claude's response:")
    print(response1)
    print('\n' + '=' * 50 + '\n')
    print('Turn 2: Requesting test cases...')
    response2 = chat('Now provide comprehensive test cases for the LRUCache implementation. \nInclude tests for:\n1. Basic get and put operations\n2. Capacity limits and eviction\n3. LRU ordering\n4. Edge cases\nProvide only the Python test code, no explanations.')
    print("Claude's response:")
    print(response2)
    print('\n' + '=' * 50 + '\n')
    print('Turn 3: Requesting optimization review...')
    response3 = chat('Review the LRUCache implementation for any potential optimizations \nor improvements while maintaining O(1) operations. Suggest any changes and provide the \noptimized code if needed. Provide only the Python code for any improvements, no explanations.')
    print("Claude's response:")
    print(response3)
if __name__ == '__main__':
    main()