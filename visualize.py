import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import glob
import json
from datetime import datetime

def load_all_results():
    """Load all result CSV files"""
    result_files = glob.glob("results_*.csv")
    
    if not result_files:
        print("No result files found. Run evaluator.py first!")
        return None
    
    all_results = []
    for file in sorted(result_files):
        df = pd.read_csv(file)
        all_results.append(df)
    
    return pd.concat(all_results, ignore_index=True)

def create_completion_rate_chart(df):
    """Create bar chart of completion rates by model"""
    
    completion_rates = df.groupby('model')['score'].mean() * 100
    
    fig = go.Figure(data=[
        go.Bar(
            x=completion_rates.index,
            y=completion_rates.values,
            text=[f"{v:.1f}%" for v in completion_rates.values],
            textposition='auto',
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1']
        )
    ])
    
    fig.update_layout(
        title="Overall Completion Rate by Model",
        xaxis_title="Model",
        yaxis_title="Completion Rate (%)",
        yaxis_range=[0, 105],
        template="plotly_white",
        height=500
    )
    
    return fig

def create_category_breakdown_chart(df):
    """Create grouped bar chart by category"""
    
    category_scores = df.groupby(['model', 'category'])['score'].mean() * 100
    category_scores = category_scores.reset_index()
    
    fig = px.bar(
        category_scores,
        x='category',
        y='score',
        color='model',
        barmode='group',
        title="Performance by Category",
        labels={'score': 'Completion Rate (%)', 'category': 'Category'},
        color_discrete_map={
            'claude': '#FF6B6B',
            'chatgpt': '#4ECDC4',
            'gemini': '#45B7D1'
        }
    )
    
    fig.update_layout(
        template="plotly_white",
        height=500,
        yaxis_range=[0, 105]
    )
    
    return fig

def create_time_series_chart(df):
    """Create time series of performance over time"""
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    # Group by timestamp and model
    time_series = df.groupby([pd.Grouper(key='timestamp', freq='D'), 'model'])['score'].mean() * 100
    time_series = time_series.reset_index()
    
    fig = px.line(
        time_series,
        x='timestamp',
        y='score',
        color='model',
        title="Performance Over Time",
        labels={'score': 'Completion Rate (%)', 'timestamp': 'Date'},
        markers=True,
        color_discrete_map={
            'claude': '#FF6B6B',
            'chatgpt': '#4ECDC4',
            'gemini': '#45B7D1'
        }
    )
    
    fig.update_layout(
        template="plotly_white",
        height=500,
        yaxis_range=[0, 105]
    )
    
    return fig

def create_detailed_comparison(df):
    """Create detailed comparison table"""
    
    # Calculate metrics per model
    summary = []
    
    for model in df['model'].unique():
        model_df = df[df['model'] == model]
        total = len(model_df)
        passed = (model_df['score'] == 1).sum()
        failed = (model_df['score'] == 0).sum()
        rate = (passed / total * 100) if total > 0 else 0
        
        summary.append({
            'Model': model.upper(),
            'Total Tests': total,
            'Passed': passed,
            'Failed': failed,
            'Success Rate': f"{rate:.1f}%"
        })
    
    summary_df = pd.DataFrame(summary)
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(summary_df.columns),
            fill_color='#2C3E50',
            font=dict(color='white', size=14),
            align='left'
        ),
        cells=dict(
            values=[summary_df[col] for col in summary_df.columns],
            fill_color='#ECF0F1',
            font=dict(size=12),
            align='left',
            height=30
        )
    )])
    
    fig.update_layout(
        title="Detailed Model Comparison",
        height=300,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig

def generate_html_report(df, output_file="evaluation_report.html"):
    """Generate a comprehensive HTML report"""
    
    # Create all visualizations
    completion_chart = create_completion_rate_chart(df)
    category_chart = create_category_breakdown_chart(df)
    comparison_table = create_detailed_comparison(df)
    
    # Try to create time series if multiple timestamps exist
    if df['timestamp'].nunique() > 1:
        time_chart = create_time_series_chart(df)
    else:
        time_chart = None
    
    # Create HTML
    html_content = f"""
    <html>
    <head>
        <title>LLM Evaluation Report</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2C3E50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #34495e;
                margin-top: 30px;
            }}
            .metadata {{
                background-color: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
            .chart {{
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 LLM Evaluation Report</h1>
            
            <div class="metadata">
                <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                <strong>Total Tests:</strong> {len(df)}<br>
                <strong>Models Evaluated:</strong> {', '.join(df['model'].unique())}<br>
                <strong>Categories:</strong> {', '.join(df['category'].unique())}
            </div>
            
            <h2>📊 Overall Performance</h2>
            <div class="chart" id="completion-chart"></div>
            
            <h2>📈 Performance by Category</h2>
            <div class="chart" id="category-chart"></div>
            
            <h2>📋 Detailed Comparison</h2>
            <div class="chart" id="comparison-table"></div>
            
            {f'<h2>📅 Performance Over Time</h2><div class="chart" id="time-chart"></div>' if time_chart else ''}
        </div>
        
        <script>
            var completionData = {completion_chart.to_json()};
            Plotly.newPlot('completion-chart', completionData.data, completionData.layout);
            
            var categoryData = {category_chart.to_json()};
            Plotly.newPlot('category-chart', categoryData.data, categoryData.layout);
            
            var comparisonData = {comparison_table.to_json()};
            Plotly.newPlot('comparison-table', comparisonData.data, comparisonData.layout);
            
            {f"var timeData = {time_chart.to_json()}; Plotly.newPlot('time-chart', timeData.data, timeData.layout);" if time_chart else ''}
        </script>
    </body>
    </html>
    """
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"\n✓ HTML report generated: {output_file}")
    print(f"  Open it in your browser to view the interactive visualizations")

def main():
    """Main visualization function"""
    
    print("Loading results...")
    df = load_all_results()
    
    if df is None:
        return
    
    print(f"Loaded {len(df)} test results")
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    
    # Individual charts
    completion_chart = create_completion_rate_chart(df)
    completion_chart.write_html("completion_rates.html")
    print("✓ Created: completion_rates.html")
    
    category_chart = create_category_breakdown_chart(df)
    category_chart.write_html("category_breakdown.html")
    print("✓ Created: category_breakdown.html")
    
    # Comprehensive report
    generate_html_report(df)
    
    # Print summary to console
    print("\n" + "="*60)
    print("QUICK SUMMARY")
    print("="*60)
    summary = df.groupby('model')['score'].agg(['mean', 'count'])
    summary['mean'] = summary['mean'] * 100
    summary.columns = ['Success Rate (%)', 'Total Tests']
    print(summary.to_string())
    print("="*60)

if __name__ == "__main__":
    main()
