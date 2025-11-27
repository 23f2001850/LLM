"""
Data downloader for various file types
Handles PDF, CSV, Excel, JSON, images, API calls
"""
import io
import logging
import base64
from typing import Dict, Any, List, Optional
import aiohttp
import asyncio

logger = logging.getLogger(__name__)


class DataDownloader:
    """Downloads and loads data from various sources"""
    
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=30)
    
    async def download_all(self, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Download all required data sources
        
        Args:
            quiz_data: Parsed quiz data containing data sources
        
        Returns:
            Dictionary with downloaded data
        """
        downloaded = {
            "files": [],
            "api_responses": [],
            "embedded_data": quiz_data.get("embedded_data", []),
            "tables": quiz_data.get("tables", []),
            "images": []
        }
        
        # Download files
        data_sources = quiz_data.get("data_sources", [])
        if data_sources:
            download_tasks = []
            for source in data_sources:
                download_tasks.append(self._download_source(source))
            
            results = await asyncio.gather(*download_tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Download failed: {result}")
                elif result:
                    downloaded["files"].append(result)
        
        # Call API endpoints
        api_endpoints = quiz_data.get("api_endpoints", [])
        if api_endpoints:
            api_tasks = []
            for endpoint in api_endpoints:
                api_tasks.append(self._call_api(endpoint))
            
            api_results = await asyncio.gather(*api_tasks, return_exceptions=True)
            
            for result in api_results:
                if isinstance(result, Exception):
                    logger.error(f"API call failed: {result}")
                elif result:
                    downloaded["api_responses"].append(result)
        
        # Process images
        images = quiz_data.get("images", [])
        for img in images:
            if img.get("is_base64"):
                downloaded["images"].append({
                    "type": "base64",
                    "data": img["src"]
                })
            elif img.get("src", "").startswith("http"):
                try:
                    img_data = await self._download_image(img["src"])
                    if img_data:
                        downloaded["images"].append({
                            "type": "url",
                            "url": img["src"],
                            "data": img_data
                        })
                except Exception as e:
                    logger.error(f"Failed to download image {img['src']}: {e}")
        
        logger.info(f"Downloaded {len(downloaded['files'])} files, "
                   f"{len(downloaded['api_responses'])} API responses, "
                   f"{len(downloaded['images'])} images")
        
        return downloaded
    
    async def _download_source(self, source: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Download a single data source"""
        url = source.get("url", "")
        data_type = source.get("type", "unknown")
        
        try:
            logger.info(f"Downloading {data_type} from {url}")
            
            # Handle data: URLs (inline data)
            if url.startswith("data:"):
                logger.info("Processing inline data URL")
                try:
                    # Parse data URL format: data:mime/type;encoding,data
                    if "," in url:
                        header, data = url.split(",", 1)
                        # Decode based on encoding
                        if "base64" in header:
                            import base64
                            content = base64.b64decode(data)
                        else:
                            # URL-encoded data
                            from urllib.parse import unquote
                            content = unquote(data).encode('utf-8')
                        
                        return {
                            "type": data_type,
                            "url": url[:50] + "...",  # Truncate for logging
                            "content": content,
                            "size": len(content)
                        }
                except Exception as e:
                    logger.error(f"Failed to parse data URL: {e}")
                    return None
            
            # Handle regular HTTP/HTTPS URLs
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        return {
                            "type": data_type,
                            "url": url,
                            "content": content,
                            "size": len(content)
                        }
                    else:
                        logger.error(f"Failed to download {url}: status {response.status}")
                        return None
        
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            return None
    
    async def _call_api(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Call API endpoint"""
        try:
            logger.info(f"Calling API: {endpoint}")
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(endpoint) as response:
                    if response.status == 200:
                        # Try to parse as JSON
                        try:
                            data = await response.json()
                            return {
                                "endpoint": endpoint,
                                "type": "json",
                                "data": data
                            }
                        except:
                            # Fall back to text
                            text = await response.text()
                            return {
                                "endpoint": endpoint,
                                "type": "text",
                                "data": text
                            }
                    else:
                        logger.error(f"API call failed {endpoint}: status {response.status}")
                        return None
        
        except Exception as e:
            logger.error(f"Error calling API {endpoint}: {e}")
            return None
    
    async def _download_image(self, url: str) -> Optional[bytes]:
        """Download image"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.read()
                    return None
        except Exception as e:
            logger.error(f"Error downloading image {url}: {e}")
            return None
