import asyncio
from backend.main import MultiAIApp

async def test_app():
    app = MultiAIApp()
    print('Available models:', app.get_available_models())
    print('Synthesis available:', app.is_synthesis_available())
    
    print('\nTesting Gemini model...')
    response = await app.process_prompt('Hello, how are you today?', model='gemini')
    print(f'Gemini response: {response}')
    
    print('\nTesting Hugging Face model...')
    response = await app.process_prompt('Explain quantum computing.', model='huggingface')
    print(f'Hugging Face response: {response}')
    
    print('\nTesting Llama model...')
    response = await app.process_prompt('What is machine learning?', model='llama')
    print(f'Llama response: {response}')
    
    print('\nTesting synthesis with multiple models...')
    result = await app.process_prompt('What is artificial intelligence?', use_multiple=True, synthesize=True)
    print(f'Synthesis result: {result}')

if __name__ == "__main__":
    asyncio.run(test_app())
