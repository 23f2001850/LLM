"""
Comprehensive test suite for LLM Analysis Quiz Bot
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import json

# Ensure solver package is importable
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_page_content():
    """Mock page content from browser"""
    return {
        "url": "https://example.com/quiz",
        "status": 200,
        "html": """
        <html>
            <head><title>Quiz</title></head>
            <body>
                <h1>What is the sum of all values?</h1>
                <a href="https://example.com/data.csv">Download CSV</a>
                <form action="https://example.com/submit" method="POST">
                    <input name="answer" type="text" />
                </form>
                <table>
                    <tr><th>Name</th><th>Value</th></tr>
                    <tr><td>A</td><td>10</td></tr>
                    <tr><td>B</td><td>20</td></tr>
                </table>
            </body>
        </html>
        """,
        "text": "What is the sum of all values? A 10 B 20",
        "scripts": [],
        "links": [
            {"href": "https://example.com/data.csv", "text": "Download CSV"}
        ],
        "data_attrs": [],
        "forms": [
            {
                "action": "https://example.com/submit",
                "method": "POST",
                "id": "quiz-form",
                "fields": [{"name": "answer", "type": "text"}]
            }
        ],
        "tables": [
            [["Name", "Value"], ["A", "10"], ["B", "20"]]
        ],
        "images": [],
        "iframes": []
    }


@pytest.fixture
def sample_csv_data():
    """Sample CSV data"""
    return b"Name,Score,Grade\nAlice,85,A\nBob,72,B\nCharlie,90,A\nDave,65,C\n"


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content (mock)"""
    return b"%PDF-1.4 mock pdf content"


class TestQuizParser:
    """Test quiz content parser"""
    
    def test_parse_question(self, mock_page_content):
        from solver.parser import QuizParser
        
        parser = QuizParser(mock_page_content)
        result = parser.parse()
        
        assert result is not None
        assert "question" in result
        assert "sum" in result["question"].lower()
    
    def test_extract_submit_url(self, mock_page_content):
        from solver.parser import QuizParser
        
        parser = QuizParser(mock_page_content)
        result = parser.parse()
        
        assert result["submit_url"] == "https://example.com/submit"
    
    def test_extract_data_sources(self, mock_page_content):
        from solver.parser import QuizParser
        
        parser = QuizParser(mock_page_content)
        result = parser.parse()
        
        assert len(result["data_sources"]) > 0
        assert any("csv" in source["url"] for source in result["data_sources"])
    
    def test_extract_tables(self, mock_page_content):
        from solver.parser import QuizParser
        
        parser = QuizParser(mock_page_content)
        result = parser.parse()
        
        assert len(result["tables"]) > 0
        assert result["tables"][0][0] == ["Name", "Value"]


class TestDataDownloader:
    """Test data downloader"""
    
    @pytest.mark.asyncio
    async def test_download_csv(self, sample_csv_data):
        from solver.downloader import DataDownloader
        
        downloader = DataDownloader()
        
        # Mock aiohttp response
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.read = AsyncMock(return_value=sample_csv_data)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            quiz_data = {
                "data_sources": [
                    {"type": "csv", "url": "https://example.com/data.csv"}
                ],
                "api_endpoints": [],
                "embedded_data": [],
                "tables": [],
                "images": []
            }
            
            result = await downloader.download_all(quiz_data)
            
            assert len(result["files"]) > 0
            assert result["files"][0]["type"] == "csv"
    
    @pytest.mark.asyncio
    async def test_api_call(self):
        from solver.downloader import DataDownloader
        
        downloader = DataDownloader()
        
        mock_api_response = {"data": [1, 2, 3], "total": 6}
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_api_response)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await downloader._call_api("https://api.example.com/data")
            
            assert result is not None
            assert result["type"] == "json"
            assert result["data"] == mock_api_response


class TestDataAnalyzer:
    """Test data analyzer"""
    
    def test_csv_analysis(self, sample_csv_data):
        from solver.analyzer import DataAnalyzer
        import pandas as pd
        
        analyzer = DataAnalyzer()
        
        # Create mock downloaded data
        df = pd.read_csv(pd.io.common.BytesIO(sample_csv_data))
        downloaded_data = {
            "files": [],
            "api_responses": [],
            "embedded_data": [],
            "tables": [],
            "images": []
        }
        
        quiz_data = {
            "question": "What is the average score?",
            "answer_format": "number"
        }
        
        # Add DataFrame to downloaded data
        all_data = {
            "dataframes": [df],
            "tables": [],
            "json_data": [],
            "text_data": [],
            "numeric_values": []
        }
        
        result = analyzer._compute_average(all_data, quiz_data["question"])
        
        # Average of [85, 72, 90, 65] = 78
        assert abs(result - 78.0) < 0.1
    
    def test_sum_computation(self):
        from solver.analyzer import DataAnalyzer
        
        analyzer = DataAnalyzer()
        
        data = {
            "dataframes": [],
            "tables": [],
            "json_data": [],
            "text_data": [],
            "numeric_values": [10, 20, 30, 40]
        }
        
        result = analyzer._compute_sum(data, "sum of all values")
        assert result == 100
    
    def test_count_computation(self):
        from solver.analyzer import DataAnalyzer
        
        analyzer = DataAnalyzer()
        
        data = {
            "dataframes": [],
            "tables": [],
            "json_data": [],
            "text_data": [],
            "numeric_values": [1, 2, 3, 4, 5]
        }
        
        result = analyzer._compute_count(data, "count items")
        assert result == 5
    
    def test_max_min_computation(self):
        from solver.analyzer import DataAnalyzer
        
        analyzer = DataAnalyzer()
        
        data = {
            "dataframes": [],
            "tables": [],
            "json_data": [],
            "text_data": [],
            "numeric_values": [15, 3, 42, 8, 23]
        }
        
        max_result = analyzer._compute_max(data, "maximum value")
        min_result = analyzer._compute_min(data, "minimum value")
        
        assert max_result == 42
        assert min_result == 3


class TestDataVisualizer:
    """Test data visualizer"""
    
    def test_create_bar_chart(self):
        from solver.visualizer import DataVisualizer
        
        visualizer = DataVisualizer()
        
        analysis_result = {
            "raw_result": {"A": 10, "B": 20, "C": 15}
        }
        
        base64_image = visualizer.create_visualization(analysis_result)
        
        assert base64_image is not None
        assert base64_image.startswith("data:image/png;base64,")
    
    def test_create_line_chart(self):
        from solver.visualizer import DataVisualizer
        
        visualizer = DataVisualizer()
        
        analysis_result = {
            "raw_result": [10, 15, 13, 17, 20, 18]
        }
        
        base64_image = visualizer.create_visualization(analysis_result)
        
        assert base64_image is not None
        assert "base64" in base64_image


class TestAnswerSubmitter:
    """Test answer submitter"""
    
    @pytest.mark.asyncio
    async def test_submit_success(self):
        from solver.submitter import AnswerSubmitter
        
        submitter = AnswerSubmitter()
        
        mock_response = {"correct": True, "message": "Correct answer!"}
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_resp = AsyncMock()
            mock_resp.status = 200
            mock_resp.json = AsyncMock(return_value=mock_response)
            mock_resp.text = AsyncMock(return_value=json.dumps(mock_response))
            mock_post.return_value.__aenter__.return_value = mock_resp
            
            result = await submitter.submit(
                "https://example.com/submit",
                42,
                "test@example.com"
            )
            
            assert result["correct"] == True
            assert result["status_code"] == 200
    
    @pytest.mark.asyncio
    async def test_submit_incorrect(self):
        from solver.submitter import AnswerSubmitter
        
        submitter = AnswerSubmitter()
        
        mock_response = {"correct": False, "message": "Try again"}
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_resp = AsyncMock()
            mock_resp.status = 200
            mock_resp.json = AsyncMock(return_value=mock_response)
            mock_resp.text = AsyncMock(return_value=json.dumps(mock_response))
            mock_post.return_value.__aenter__.return_value = mock_resp
            
            result = await submitter.submit(
                "https://example.com/submit",
                99,
                "test@example.com"
            )
            
            assert result["correct"] == False


class TestUtils:
    """Test utility functions"""
    
    def test_timeout_manager(self):
        from solver.utils import TimeoutManager
        import time
        
        mgr = TimeoutManager(max_seconds=2)
        
        assert not mgr.is_expired()
        assert mgr.remaining() > 1.5
        
        time.sleep(1)
        
        assert mgr.elapsed() >= 1.0
        assert mgr.remaining() <= 1.0
    
    def test_sanitize_string(self):
        from solver.utils import sanitize_string
        
        dirty = "Hello\x00World\x01Test"
        clean = sanitize_string(dirty)
        
        assert "\x00" not in clean
        assert "\x01" not in clean
        assert "Hello" in clean
    
    def test_extract_numbers(self):
        from solver.utils import extract_numbers
        
        text = "The values are 10, 20.5, and -5.3"
        numbers = extract_numbers(text)
        
        assert 10.0 in numbers
        assert 20.5 in numbers
        assert -5.3 in numbers


class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_quiz_flow(self, mock_page_content, sample_csv_data):
        """Test complete quiz solving flow"""
        from solver.parser import QuizParser
        from solver.downloader import DataDownloader
        from solver.analyzer import DataAnalyzer
        
        # Parse quiz
        parser = QuizParser(mock_page_content)
        quiz_data = parser.parse()
        
        assert quiz_data is not None
        assert quiz_data["submit_url"] is not None
        
        # Mock download
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.read = AsyncMock(return_value=sample_csv_data)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            downloader = DataDownloader()
            downloaded_data = await downloader.download_all(quiz_data)
        
        # Analyze
        analyzer = DataAnalyzer()
        analysis_result = analyzer.analyze(quiz_data, downloaded_data)
        
        assert analysis_result is not None
        assert "answer" in analysis_result


# Run tests with: pytest tests/test_backend.py -v
