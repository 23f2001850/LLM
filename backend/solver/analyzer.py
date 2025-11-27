"""
Data analyzer
Processes PDFs, CSVs, Excel files, performs statistical analysis, and computes answers
"""
import io
import re
import json
import base64
import logging
from typing import Dict, Any, List, Optional, Union
import pandas as pd
import numpy as np
from PIL import Image
import pdfplumber
import PyPDF2
import openpyxl

logger = logging.getLogger(__name__)


class DataAnalyzer:
    """Analyzes downloaded data and computes answers"""
    
    def analyze(self, quiz_data: Dict[str, Any], downloaded_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method
        
        Args:
            quiz_data: Parsed quiz information
            downloaded_data: Downloaded files and data
        
        Returns:
            Dictionary containing analysis results and final answer
        """
        try:
            question = quiz_data.get("question", "").lower()
            answer_format = quiz_data.get("answer_format", "string")
            
            # Combine all data sources
            all_data = self._aggregate_data(downloaded_data)
            
            # Determine analysis type from question
            analysis_type = self._determine_analysis_type(question)
            
            logger.info(f"Analysis type: {analysis_type}, Answer format: {answer_format}")
            
            # Perform analysis based on type
            if analysis_type == "sum":
                result = self._compute_sum(all_data, question)
            elif analysis_type == "average":
                result = self._compute_average(all_data, question)
            elif analysis_type == "count":
                result = self._compute_count(all_data, question)
            elif analysis_type == "max":
                result = self._compute_max(all_data, question)
            elif analysis_type == "min":
                result = self._compute_min(all_data, question)
            elif analysis_type == "filter":
                result = self._apply_filter(all_data, question)
            elif analysis_type == "aggregate":
                result = self._aggregate_analysis(all_data, question)
            elif analysis_type == "extract":
                result = self._extract_value(all_data, question)
            else:
                # Default: try to find relevant values
                result = self._smart_analysis(all_data, question)
            
            # Format answer according to expected format
            answer = self._format_answer(result, answer_format)
            
            return {
                "analysis_type": analysis_type,
                "raw_result": result,
                "answer": answer,
                "data_summary": self._summarize_data(all_data)
            }
        
        except Exception as e:
            logger.error(f"Error in analysis: {e}", exc_info=True)
            return {
                "error": str(e),
                "answer": None
            }
    
    def _aggregate_data(self, downloaded_data: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate all data into usable structures"""
        aggregated = {
            "dataframes": [],
            "tables": [],
            "json_data": [],
            "text_data": [],
            "numeric_values": []
        }
        
        # Process files
        for file_info in downloaded_data.get("files", []):
            content = file_info.get("content", b"")
            file_type = file_info.get("type", "")
            
            if file_type == "pdf":
                extracted = self._extract_from_pdf(content)
                aggregated["dataframes"].extend(extracted.get("dataframes", []))
                aggregated["tables"].extend(extracted.get("tables", []))
                aggregated["text_data"].append(extracted.get("text", ""))
            
            elif file_type == "csv":
                df = self._extract_from_csv(content)
                if df is not None:
                    aggregated["dataframes"].append(df)
            
            elif file_type == "excel":
                dfs = self._extract_from_excel(content)
                aggregated["dataframes"].extend(dfs)
            
            elif file_type == "json":
                data = self._extract_from_json(content)
                if data:
                    aggregated["json_data"].append(data)
        
        # Process API responses
        for api_response in downloaded_data.get("api_responses", []):
            if api_response.get("type") == "json":
                aggregated["json_data"].append(api_response.get("data"))
            else:
                aggregated["text_data"].append(api_response.get("data", ""))
        
        # Process embedded data
        for embedded in downloaded_data.get("embedded_data", []):
            if embedded.get("type") == "json":
                aggregated["json_data"].append(embedded.get("data"))
            elif embedded.get("type") == "base64":
                # Decode base64
                try:
                    decoded = base64.b64decode(embedded.get("data", ""))
                    aggregated["text_data"].append(decoded.decode('utf-8'))
                except:
                    pass
        
        # Process HTML tables
        for table in downloaded_data.get("tables", []):
            if table and len(table) > 0:
                try:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    aggregated["dataframes"].append(df)
                except:
                    aggregated["tables"].append(table)
        
        # Extract numeric values from all text
        for text in aggregated["text_data"]:
            numbers = re.findall(r'-?\d+\.?\d*', str(text))
            aggregated["numeric_values"].extend([float(n) for n in numbers])
        
        return aggregated
    
    def _extract_from_pdf(self, content: bytes) -> Dict[str, Any]:
        """Extract data from PDF"""
        result = {"dataframes": [], "tables": [], "text": ""}
        
        try:
            # Try pdfplumber first (better table extraction)
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                text_parts = []
                for page in pdf.pages:
                    # Extract text
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                    
                    # Extract tables
                    tables = page.extract_tables()
                    for table in tables:
                        if table and len(table) > 1:
                            try:
                                # Convert to DataFrame
                                df = pd.DataFrame(table[1:], columns=table[0])
                                result["dataframes"].append(df)
                            except:
                                result["tables"].append(table)
                
                result["text"] = "\n".join(text_parts)
        
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}, trying PyPDF2")
            
            # Fallback to PyPDF2
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                text_parts = []
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                result["text"] = "\n".join(text_parts)
            except Exception as e2:
                logger.error(f"PyPDF2 also failed: {e2}")
        
        return result
    
    def _extract_from_csv(self, content: bytes) -> Optional[pd.DataFrame]:
        """Extract DataFrame from CSV"""
        try:
            df = pd.read_csv(io.BytesIO(content))
            return df
        except Exception as e:
            logger.error(f"Error reading CSV: {e}")
            # Try with different encoding
            try:
                df = pd.read_csv(io.BytesIO(content), encoding='latin-1')
                return df
            except:
                return None
    
    def _extract_from_excel(self, content: bytes) -> List[pd.DataFrame]:
        """Extract DataFrames from Excel"""
        dataframes = []
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(io.BytesIO(content))
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                dataframes.append(df)
        except Exception as e:
            logger.error(f"Error reading Excel: {e}")
        
        return dataframes
    
    def _extract_from_json(self, content: bytes) -> Optional[Any]:
        """Extract data from JSON"""
        try:
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error parsing JSON: {e}")
            return None
    
    def _determine_analysis_type(self, question: str) -> str:
        """Determine what type of analysis to perform"""
        q = question.lower()
        
        if any(word in q for word in ['sum', 'total', 'add']):
            return "sum"
        elif any(word in q for word in ['average', 'mean', 'avg']):
            return "average"
        elif any(word in q for word in ['count', 'how many', 'number of']):
            return "count"
        elif any(word in q for word in ['maximum', 'max', 'highest', 'largest']):
            return "max"
        elif any(word in q for word in ['minimum', 'min', 'lowest', 'smallest']):
            return "min"
        elif any(word in q for word in ['filter', 'where', 'greater than', 'less than']):
            return "filter"
        elif any(word in q for word in ['group', 'aggregate', 'by']):
            return "aggregate"
        else:
            return "extract"
    
    def _compute_sum(self, data: Dict[str, Any], question: str) -> float:
        """Compute sum"""
        values = self._extract_relevant_numbers(data, question)
        return sum(values) if values else 0
    
    def _compute_average(self, data: Dict[str, Any], question: str) -> float:
        """Compute average"""
        values = self._extract_relevant_numbers(data, question)
        return np.mean(values) if values else 0
    
    def _compute_count(self, data: Dict[str, Any], question: str) -> int:
        """Count items"""
        values = self._extract_relevant_numbers(data, question)
        if values:
            return len(values)
        
        # Try counting rows in dataframes
        total = 0
        for df in data.get("dataframes", []):
            total += len(df)
        return total
    
    def _compute_max(self, data: Dict[str, Any], question: str) -> float:
        """Find maximum"""
        values = self._extract_relevant_numbers(data, question)
        return max(values) if values else 0
    
    def _compute_min(self, data: Dict[str, Any], question: str) -> float:
        """Find minimum"""
        values = self._extract_relevant_numbers(data, question)
        return min(values) if values else 0
    
    def _apply_filter(self, data: Dict[str, Any], question: str) -> Any:
        """Apply filter to data"""
        # Try to extract filter conditions from question
        for df in data.get("dataframes", []):
            # Simple example: filter numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                col = numeric_cols[0]
                # Return filtered data
                return df[df[col] > df[col].median()].to_dict('records')
        
        return []
    
    def _aggregate_analysis(self, data: Dict[str, Any], question: str) -> Any:
        """Perform aggregation"""
        for df in data.get("dataframes", []):
            # Try to find grouping columns
            non_numeric = df.select_dtypes(exclude=[np.number]).columns
            numeric = df.select_dtypes(include=[np.number]).columns
            
            if len(non_numeric) > 0 and len(numeric) > 0:
                result = df.groupby(non_numeric[0])[numeric[0]].sum().to_dict()
                return result
        
        return {}
    
    def _extract_value(self, data: Dict[str, Any], question: str) -> Any:
        """Extract specific value based on question"""
        # Look for keywords in question to match column names
        keywords = re.findall(r'\b\w+\b', question.lower())
        
        for df in data.get("dataframes", []):
            for col in df.columns:
                if any(keyword in col.lower() for keyword in keywords):
                    # Return first non-null value
                    return df[col].dropna().iloc[0] if not df[col].dropna().empty else None
        
        # Check JSON data
        for json_obj in data.get("json_data", []):
            if isinstance(json_obj, dict):
                for key, value in json_obj.items():
                    if any(keyword in key.lower() for keyword in keywords):
                        return value
        
        return None
    
    def _smart_analysis(self, data: Dict[str, Any], question: str) -> Any:
        """Smart analysis when type is unclear"""
        # Default: return sum of all numeric values found
        values = self._extract_relevant_numbers(data, question)
        if values:
            return sum(values)
        
        # If no numbers, return first dataframe as dict
        if data.get("dataframes"):
            return data["dataframes"][0].to_dict('records')
        
        # If JSON data, return first JSON object
        if data.get("json_data"):
            return data["json_data"][0]
        
        return None
    
    def _extract_relevant_numbers(self, data: Dict[str, Any], question: str) -> List[float]:
        """Extract numbers relevant to the question"""
        numbers = []
        
        # From dataframes
        for df in data.get("dataframes", []):
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                numbers.extend(df[col].dropna().tolist())
        
        # From direct numeric values
        numbers.extend(data.get("numeric_values", []))
        
        return numbers
    
    def _format_answer(self, result: Any, answer_format: str) -> Any:
        """Format answer according to expected format"""
        if answer_format == "number":
            if isinstance(result, (int, float)):
                return result
            elif isinstance(result, str):
                try:
                    return float(result)
                except:
                    return 0
            return 0
        
        elif answer_format == "boolean":
            return bool(result)
        
        elif answer_format == "json":
            if isinstance(result, (dict, list)):
                return result
            return {"result": result}
        
        elif answer_format == "array":
            if isinstance(result, list):
                return result
            return [result]
        
        else:  # string
            return str(result)
    
    def _summarize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of processed data"""
        return {
            "dataframes_count": len(data.get("dataframes", [])),
            "tables_count": len(data.get("tables", [])),
            "json_objects_count": len(data.get("json_data", [])),
            "numeric_values_count": len(data.get("numeric_values", []))
        }
