"""
Answer submitter
Handles submission of answers to quiz endpoints
"""
import logging
from typing import Dict, Any, Optional
import aiohttp

logger = logging.getLogger(__name__)


class AnswerSubmitter:
    """Submits answers to quiz endpoints"""
    
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=30)
    
    async def submit(self, submit_url: str, answer: Any, email: str) -> Dict[str, Any]:
        """
        Submit answer to quiz endpoint
        
        Args:
            submit_url: URL to submit answer
            answer: The computed answer
            email: Student email
        
        Returns:
            Response from submit endpoint
        """
        try:
            logger.info(f"Submitting answer to {submit_url}")
            logger.debug(f"Answer: {str(answer)[:200]}")
            
            # Prepare payload
            payload = {
                "email": email,
                "answer": answer
            }
            
            # Try POST request
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                try:
                    async with session.post(submit_url, json=payload) as response:
                        response_text = await response.text()
                        
                        # Try to parse as JSON
                        try:
                            response_data = await response.json()
                        except:
                            response_data = {"text": response_text}
                        
                        logger.info(f"Submit response status: {response.status}")
                        logger.debug(f"Submit response: {str(response_data)[:500]}")
                        
                        # Add status and URL info
                        response_data["status_code"] = response.status
                        response_data["submit_url"] = submit_url
                        
                        # Extract next quiz URL if present (for chaining)
                        next_url = self._extract_next_url(response_data)
                        if next_url:
                            response_data["next_url"] = next_url
                            logger.info(f"Next quiz URL detected: {next_url}")
                        
                        return response_data
                
                except aiohttp.ClientError as e:
                    logger.error(f"HTTP error submitting answer: {e}")
                    
                    # Try with different payload formats
                    return await self._try_alternative_formats(session, submit_url, answer, email)
        
        except Exception as e:
            logger.error(f"Error submitting answer: {e}")
            return {
                "error": str(e),
                "correct": False
            }
    
    async def _try_alternative_formats(self, session: aiohttp.ClientSession, 
                                      url: str, answer: Any, email: str) -> Dict[str, Any]:
        """Try alternative payload formats"""
        
        # Try with just answer field
        try:
            payload = {"answer": answer}
            async with session.post(url, json=payload) as response:
                try:
                    return await response.json()
                except:
                    return {"text": await response.text(), "status_code": response.status}
        except:
            pass
        
        # Try form data
        try:
            form_data = aiohttp.FormData()
            form_data.add_field('email', email)
            form_data.add_field('answer', str(answer))
            
            async with session.post(url, data=form_data) as response:
                try:
                    return await response.json()
                except:
                    return {"text": await response.text(), "status_code": response.status}
        except:
            pass
        
        return {"error": "All submission methods failed", "correct": False}
    
    def _extract_next_url(self, response_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract next quiz URL from response data
        Supports various response formats for chaining
        """
        if not isinstance(response_data, dict):
            return None
        
        # Check common fields for next URL
        url_fields = ["url", "next_url", "nextUrl", "next", "redirect", "nextQuiz"]
        
        for field in url_fields:
            if field in response_data:
                url = response_data[field]
                if url and isinstance(url, str) and len(url) > 0:
                    # Validate it looks like a URL
                    if url.startswith(("http://", "https://", "/")):
                        return url
        
        # Check nested data structures
        if "data" in response_data and isinstance(response_data["data"], dict):
            nested_url = self._extract_next_url(response_data["data"])
            if nested_url:
                return nested_url
        
        return None
