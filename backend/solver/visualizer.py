"""
Data visualizer
Creates charts and converts them to base64 for submission
"""
import io
import base64
import logging
from typing import Dict, Any, Optional
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DataVisualizer:
    """Creates visualizations from analyzed data"""
    
    def create_visualization(self, analysis_result: Dict[str, Any]) -> Optional[str]:
        """
        Create visualization and return as base64 string
        
        Args:
            analysis_result: Analysis results containing data to visualize
        
        Returns:
            Base64 encoded PNG image
        """
        try:
            raw_result = analysis_result.get("raw_result")
            
            # Determine chart type based on data structure
            if isinstance(raw_result, dict):
                return self._create_bar_chart(raw_result)
            elif isinstance(raw_result, list):
                return self._create_line_chart(raw_result)
            elif isinstance(raw_result, (int, float)):
                return self._create_single_value_chart(raw_result)
            else:
                logger.warning(f"Unknown data type for visualization: {type(raw_result)}")
                return None
        
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            return None
    
    def _create_bar_chart(self, data: Dict[str, Any]) -> str:
        """Create bar chart from dictionary"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        keys = list(data.keys())
        values = list(data.values())
        
        # Convert values to numeric if possible
        numeric_values = []
        for v in values:
            try:
                numeric_values.append(float(v))
            except:
                numeric_values.append(0)
        
        ax.bar(keys, numeric_values)
        ax.set_xlabel('Categories')
        ax.set_ylabel('Values')
        ax.set_title('Data Analysis Results')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def _create_line_chart(self, data: list) -> str:
        """Create line chart from list"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Convert to numeric
        numeric_data = []
        for item in data:
            try:
                if isinstance(item, dict):
                    # Use first numeric value
                    for v in item.values():
                        try:
                            numeric_data.append(float(v))
                            break
                        except:
                            continue
                else:
                    numeric_data.append(float(item))
            except:
                pass
        
        if numeric_data:
            ax.plot(numeric_data, marker='o')
            ax.set_xlabel('Index')
            ax.set_ylabel('Value')
            ax.set_title('Data Trend')
            plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def _create_single_value_chart(self, value: float) -> str:
        """Create chart for single value (gauge-like)"""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        ax.text(0.5, 0.5, f'{value:.2f}', 
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=48,
                transform=ax.transAxes)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.set_title('Result', fontsize=20)
        
        return self._fig_to_base64(fig)
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        buffer.seek(0)
        
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        return f"data:image/png;base64,{image_base64}"
    
    def create_dataframe_visualization(self, df: pd.DataFrame) -> Optional[str]:
        """Create visualization from DataFrame"""
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Find numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) > 0:
                # Plot first few numeric columns
                df[numeric_cols[:3]].plot(ax=ax, kind='bar')
                ax.set_title('Data Analysis')
                ax.set_xlabel('Index')
                ax.set_ylabel('Value')
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                return self._fig_to_base64(fig)
            else:
                plt.close(fig)
                return None
        
        except Exception as e:
            logger.error(f"Error creating DataFrame visualization: {e}")
            return None
