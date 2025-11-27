"""
Quiz content parser
Extracts questions, instructions, data sources, and submit URLs from page content
"""
import re
import json
import logging
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class QuizParser:
    """Parses quiz page content to extract relevant information"""
    
    def __init__(self, page_content: Dict[str, Any]):
        self.page_content = page_content
        self.soup = BeautifulSoup(page_content.get("html", ""), 'html.parser')
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse all quiz content
        
        Returns:
            Dictionary containing:
            - question: The main question text
            - instructions: Any special instructions
            - data_sources: List of data files/URLs to download
            - submit_url: URL to submit answer
            - answer_format: Expected answer format
            - requires_visualization: Whether visualization is needed
        """
        try:
            result = {
                "question": self._extract_question(),
                "instructions": self._extract_instructions(),
                "data_sources": self._extract_data_sources(),
                "submit_url": self._extract_submit_url(),
                "answer_format": self._extract_answer_format(),
                "requires_visualization": self._check_visualization_required(),
                "embedded_data": self._extract_embedded_data(),
                "api_endpoints": self._extract_api_endpoints(),
                "tables": self._extract_tables(),
                "images": self._extract_images()
            }
            
            logger.info(f"Parsed quiz: question length={len(result['question'])}, "
                       f"data_sources={len(result['data_sources'])}, "
                       f"submit_url={'found' if result['submit_url'] else 'missing'}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error parsing quiz content: {e}")
            return {}
    
    def _extract_question(self) -> str:
        """Extract main question text"""
        question = ""
        
        # Try common question selectors
        selectors = [
            'h1', 'h2', '.question', '#question', 
            '[class*="question"]', '[id*="question"]',
            'p', 'div'
        ]
        
        for selector in selectors:
            elements = self.soup.select(selector)
            for el in elements:
                text = el.get_text(strip=True)
                if len(text) > len(question) and ('?' in text or len(text) > 20):
                    question = text
        
        # Also check text content
        text_content = self.page_content.get("text", "")
        lines = text_content.split('\n')
        for line in lines:
            line = line.strip()
            if '?' in line and len(line) > len(question):
                question = line
                break
        
        return question
    
    def _extract_instructions(self) -> str:
        """Extract special instructions"""
        instructions = ""
        
        # Look for instruction keywords
        keywords = ['instruction', 'note', 'hint', 'help', 'guide']
        
        for keyword in keywords:
            elements = self.soup.find_all(class_=re.compile(keyword, re.I))
            for el in elements:
                text = el.get_text(strip=True)
                if len(text) > len(instructions):
                    instructions = text
        
        return instructions
    
    def _extract_data_sources(self) -> List[Dict[str, str]]:
        """Extract data file URLs and API endpoints"""
        sources = []
        
        # Extract from links
        links = self.page_content.get("links", [])
        logger.info(f"Checking {len(links)} links for data sources")
        for link in links:
            href = link.get("href", "")
            if self._is_data_url(href):
                logger.info(f"Found data source: {href[:100]}...")
                sources.append({
                    "type": self._guess_data_type(href),
                    "url": href,
                    "text": link.get("text", "")
                })
        
        # Extract from data attributes
        for data_attr in self.page_content.get("data_attrs", []):
            for key in ['url', 'api', 'file']:
                url = data_attr.get(key, "")
                if url and self._is_data_url(url):
                    sources.append({
                        "type": self._guess_data_type(url),
                        "url": url,
                        "text": key
                    })
        
        # Extract from scripts (embedded URLs)
        for script in self.page_content.get("scripts", []):
            urls = re.findall(r'https?://[^\s\'"<>]+', script)
            for url in urls:
                if self._is_data_url(url):
                    sources.append({
                        "type": self._guess_data_type(url),
                        "url": url,
                        "text": "script"
                    })
        
        # Remove duplicates
        unique_sources = []
        seen_urls = set()
        for source in sources:
            if source["url"] not in seen_urls:
                unique_sources.append(source)
                seen_urls.add(source["url"])
        
        return unique_sources
    
    def _extract_submit_url(self) -> Optional[str]:
        """Extract submit URL dynamically"""
        base_url = self.page_content.get("url", "")
        logger.info(f"[SUBMIT_URL_DEBUG] Extracting submit URL from base: {base_url}")
        
        # Helper to make absolute URL
        def make_absolute(url):
            if not url:
                return None
            if url.startswith('http'):
                return url
            if url.startswith('/'):
                # Absolute path - use base URL origin
                from urllib.parse import urlparse
                parsed = urlparse(base_url)
                return f"{parsed.scheme}://{parsed.netloc}{url}"
            # Relative path
            from urllib.parse import urljoin
            return urljoin(base_url, url)
        
        # Check forms
        forms = self.page_content.get("forms", [])
        logger.info(f"[SUBMIT_URL_DEBUG] Found {len(forms)} forms")
        for i, form in enumerate(forms):
            action = form.get("action", "")
            logger.info(f"[SUBMIT_URL_DEBUG] Form {i}: action='{action}', method='{form.get('method', '')}'")
            if action and ('submit' in action.lower() or 'answer' in action.lower()):
                abs_url = make_absolute(action)
                logger.info(f"[SUBMIT_URL_DEBUG] Found submit URL in form: {abs_url}")
                return abs_url
            if action and action.startswith('http'):
                logger.info(f"[SUBMIT_URL_DEBUG] Found http URL in form: {action}")
                return action
        
        # Check data attributes
        for data_attr in self.page_content.get("data_attrs", []):
            submit_url = data_attr.get("submit", "")
            if submit_url:
                return make_absolute(submit_url)
        
        # Check links with submit keyword
        for link in self.page_content.get("links", []):
            href = link.get("href", "")
            text = link.get("text", "").lower()
            if 'submit' in text or 'answer' in text or 'submit' in href.lower():
                return make_absolute(href)
        
        # Check scripts for submit URLs
        for script in self.page_content.get("scripts", []):
            # Look for fetch/axios/ajax calls
            submit_patterns = [
                r'fetch\([\'"]([^\'"]+)[\'"]',
                r'axios\.post\([\'"]([^\'"]+)[\'"]',
                r'\.ajax\([\'"]([^\'"]+)[\'"]',
                r'submitUrl[\'"]?\s*[:=]\s*[\'"]([^\'"]+)[\'"]',
                r'SUBMIT_URL\s*=\s*[\'"]([^\'"]+)[\'"]'
            ]
            for pattern in submit_patterns:
                matches = re.findall(pattern, script)
                for match in matches:
                    if 'submit' in match.lower() or match.startswith('http'):
                        return make_absolute(match)
        
        # Look for text mentioning "/submit" or similar
        text_content = self.page_content.get("text", "")
        if '/submit' in text_content:
            abs_url = make_absolute('/submit')
            logger.info(f"[SUBMIT_URL_DEBUG] Found /submit in text content: {abs_url}")
            return abs_url
        
        # If still not found, look for any POST endpoint
        for form in forms:
            if form.get("method", "").upper() == "POST":
                abs_url = make_absolute(form.get("action", ""))
                logger.info(f"[SUBMIT_URL_DEBUG] Using POST form action: {abs_url}")
                return abs_url
        
        # Last resort: construct submit URL from base URL
        # Most quiz systems follow a pattern like /submit or /answer
        if base_url:
            from urllib.parse import urlparse
            parsed = urlparse(base_url)
            # Try common submit endpoints - return /submit
            potential_url = f"{parsed.scheme}://{parsed.netloc}/submit"
            logger.info(f"[SUBMIT_URL_DEBUG] Using fallback: {potential_url}")
            return potential_url
        
        logger.warning("[SUBMIT_URL_DEBUG] No submit URL found and no base_url!")
        return None
    
    def _extract_answer_format(self) -> str:
        """Determine expected answer format"""
        text = self.page_content.get("text", "").lower()
        
        if "json" in text or "object" in text:
            return "json"
        elif "base64" in text or "image" in text or "chart" in text:
            return "base64"
        elif "true" in text or "false" in text or "boolean" in text:
            return "boolean"
        elif "number" in text or "integer" in text or "count" in text:
            return "number"
        elif "array" in text or "list" in text:
            return "array"
        else:
            return "string"
    
    def _check_visualization_required(self) -> bool:
        """Check if visualization is required"""
        text = self.page_content.get("text", "").lower()
        keywords = ['chart', 'graph', 'plot', 'visualiz', 'diagram', 'image', 'png', 'base64']
        return any(keyword in text for keyword in keywords)
    
    def _extract_embedded_data(self) -> List[Dict[str, Any]]:
        """Extract data embedded in scripts (JSON, CSV, etc.)"""
        embedded = []
        
        for script in self.page_content.get("scripts", []):
            # Try to find JSON objects
            try:
                # Look for JSON assignments
                json_patterns = [
                    r'const\s+\w+\s*=\s*(\{.+?\});',
                    r'var\s+\w+\s*=\s*(\{.+?\});',
                    r'let\s+\w+\s*=\s*(\{.+?\});',
                    r'data\s*=\s*(\{.+?\})',
                    r'JSON\.parse\([\'"](.+?)[\'"]\)'
                ]
                
                for pattern in json_patterns:
                    matches = re.findall(pattern, script, re.DOTALL)
                    for match in matches:
                        try:
                            data = json.loads(match)
                            embedded.append({"type": "json", "data": data})
                        except:
                            pass
            except Exception as e:
                logger.debug(f"Error extracting JSON from script: {e}")
            
            # Look for base64 encoded data
            base64_pattern = r'atob\([\'"]([A-Za-z0-9+/=]+)[\'"]\)'
            base64_matches = re.findall(base64_pattern, script)
            for b64_data in base64_matches:
                embedded.append({"type": "base64", "data": b64_data})
        
        return embedded
    
    def _extract_api_endpoints(self) -> List[str]:
        """Extract API endpoints to call"""
        endpoints = []
        
        for script in self.page_content.get("scripts", []):
            # Look for API URLs
            api_patterns = [
                r'fetch\([\'"]([^\'"]+api[^\'"]+)[\'"]',
                r'axios\.[get|post]+\([\'"]([^\'"]+)[\'"]',
                r'apiUrl[\'"]?\s*[:=]\s*[\'"]([^\'"]+)[\'"]',
                r'API_ENDPOINT\s*=\s*[\'"]([^\'"]+)[\'"]'
            ]
            
            for pattern in api_patterns:
                matches = re.findall(pattern, script)
                endpoints.extend(matches)
        
        return list(set(endpoints))  # Remove duplicates
    
    def _extract_tables(self) -> List[List[List[str]]]:
        """Extract HTML tables"""
        return self.page_content.get("tables", [])
    
    def _extract_images(self) -> List[Dict[str, str]]:
        """Extract image information"""
        images = []
        for img in self.page_content.get("images", []):
            if img.get("src"):
                images.append({
                    "src": img["src"],
                    "alt": img.get("alt", ""),
                    "is_base64": img.get("isBase64", False)
                })
        return images
    
    def _is_data_url(self, url: str) -> bool:
        """Check if URL points to data file"""
        data_extensions = ['.pdf', '.csv', '.xlsx', '.xls', '.json', '.xml', '.txt']
        url_lower = url.lower()
        # Also check for data: URLs (inline data)
        if url_lower.startswith('data:'):
            return True
        return any(ext in url_lower for ext in data_extensions) or '/api/' in url_lower
    
    def _guess_data_type(self, url: str) -> str:
        """Guess data type from URL"""
        url_lower = url.lower()
        # Check for data: URLs (inline data)
        if url_lower.startswith('data:text/csv'):
            return 'csv'
        elif url_lower.startswith('data:application/pdf'):
            return 'pdf'
        elif url_lower.startswith('data:application/json'):
            return 'json'
        elif url_lower.startswith('data:'):
            return 'csv'  # Default to CSV for data: URLs
        elif '.pdf' in url_lower:
            return 'pdf'
        elif '.csv' in url_lower:
            return 'csv'
        elif '.xlsx' in url_lower or '.xls' in url_lower:
            return 'excel'
        elif '.json' in url_lower:
            return 'json'
        elif '/api/' in url_lower:
            return 'api'
        else:
            return 'unknown'
