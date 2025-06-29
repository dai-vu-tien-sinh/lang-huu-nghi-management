import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Optional, Union

class ChartCustomizer:
    def __init__(self):
        self.chart_types = {
            'Cột': 'bar',
            'Đường': 'line',
            'Tròn': 'pie',
            'Scatter': 'scatter',
            'Box Plot': 'box',
            'Histogram': 'histogram'
        }
        
        self.color_schemes = {
            'Mặc định': None,
            'Viridis': 'viridis',
            'Pastel': 'pastel',
            'Rainbow': 'rainbow',
            'Cividis': 'cividis'
        }
    
    def create_customizable_chart(
        self,
        data: pd.DataFrame,
        chart_type: str,
        x_column: str,
        y_column: Optional[str] = None,
        color_column: Optional[str] = None,
        title: Optional[str] = None,
        color_scheme: Optional[str] = None,
        orientation: str = 'vertical',
        show_grid: bool = True,
        custom_colors: Optional[List[str]] = None,
        animation_frame: Optional[str] = None
    ) -> Union[go.Figure, None]:
        """
        Create a customizable chart based on user preferences
        """
        try:
            # Convert Vietnamese chart type to Plotly type
            plot_type = self.chart_types.get(chart_type)
            if not plot_type:
                return None

            # Base chart configuration
            chart_config = {
                'data_frame': data,
                'title': title,
                'template': 'plotly_white'
            }

            # Add columns based on chart type
            if plot_type in ['bar', 'line', 'scatter']:
                chart_config.update({
                    'x': x_column,
                    'y': y_column,
                    'color': color_column if color_column else None,
                    'animation_frame': animation_frame if animation_frame else None
                })
            elif plot_type == 'pie':
                chart_config.update({
                    'names': x_column,
                    'values': y_column
                })

            # Apply color scheme if specified
            if color_scheme in self.color_schemes:
                chart_config['color_discrete_sequence'] = px.colors.qualitative.Set3

            # Create figure based on chart type
            if plot_type == 'bar':
                fig = px.bar(**chart_config)
                if orientation == 'horizontal':
                    fig.update_layout(barmode='group')
            elif plot_type == 'line':
                fig = px.line(**chart_config)
            elif plot_type == 'scatter':
                fig = px.scatter(**chart_config)
            elif plot_type == 'pie':
                fig = px.pie(**chart_config)
            elif plot_type == 'box':
                fig = px.box(data, x=x_column, y=y_column)
            elif plot_type == 'histogram':
                fig = px.histogram(data, x=x_column)
            else:
                return None

            # Update layout based on preferences
            fig.update_layout(
                showlegend=True,
                xaxis_showgrid=show_grid,
                yaxis_showgrid=show_grid
            )

            # Apply custom colors if provided
            if custom_colors:
                if plot_type == 'pie':
                    fig.update_traces(marker=dict(colors=custom_colors))
                else:
                    fig.update_traces(marker_color=custom_colors[0])

            return fig

        except Exception as e:
            print(f"Error creating chart: {str(e)}")
            return None

    def get_available_chart_types(self) -> List[str]:
        """Get list of available chart types"""
        return list(self.chart_types.keys())

    def get_available_color_schemes(self) -> List[str]:
        """Get list of available color schemes"""
        return list(self.color_schemes.keys())

def create_comparison_chart(
    data1: pd.DataFrame,
    data2: pd.DataFrame,
    x_column: str,
    y_column: str,
    label1: str,
    label2: str,
    title: str
) -> go.Figure:
    """
    Create a comparison chart with two datasets
    """
    fig = go.Figure()

    # Add traces for both datasets
    fig.add_trace(
        go.Scatter(
            x=data1[x_column],
            y=data1[y_column],
            name=label1,
            mode='lines+markers'
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data2[x_column],
            y=data2[y_column],
            name=label2,
            mode='lines+markers'
        )
    )

    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title=x_column,
        yaxis_title=y_column,
        showlegend=True
    )

    return fig
