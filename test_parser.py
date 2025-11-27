import asyncio
import sys
sys.path.insert(0, 'c:/Krishna_Jain/LLM/backend')

from solver.browser import BrowserManager
from solver.parser import QuizParser

async def test():
    browser = BrowserManager()
    await browser.start()
    
    # Load test page
    page_content = await browser.load_page("http://127.0.0.1:5500/test-quiz.html")
    
    print(f"\n=== PAGE CONTENT ===")
    print(f"Links found: {len(page_content['links'])}")
    
    # Check for data: URLs
    data_urls = [l for l in page_content['links'] if 'data:' in l.get('href', '')]
    print(f"Data URLs found: {len(data_urls)}")
    
    if data_urls:
        for url in data_urls:
            print(f"\nData URL:")
            print(f"  href: {url['href'][:100]}...")
            print(f"  text: {url.get('text', '')}")
    
    # Parse with QuizParser
    parser = QuizParser(page_content)
    quiz_data = parser.parse()
    
    print(f"\n=== PARSED QUIZ ===")
    print(f"Question: {quiz_data['question'][:100]}...")
    print(f"Data sources: {len(quiz_data['data_sources'])}")
    
    for source in quiz_data['data_sources']:
        print(f"\nSource:")
        print(f"  type: {source['type']}")
        print(f"  url: {source['url'][:100]}...")
    
    await browser.close()

asyncio.run(test())
