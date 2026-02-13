import pandas as pd
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from loguru import logger
import json
from typing import List, Dict

class ReportGenerator:
    def __init__(self, config: dict):
        self.output_dir = Path(config.get("reporting", {}).get("output_dir", "reports"))
        self.output_dir.mkdir(exist_ok=True)
        # Use absolute path for template or a fallback string template
        self.template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Opportunity Radar Report</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f4f7f6; }
                header { margin-bottom: 30px; text-align: center; }
                table { width: 100%; border-collapse: collapse; background-color: #fff; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #2c3e50; color: white; }
                tr:hover { background-color: #f1f1f1; }
                .score-high { color: #27ae60; font-weight: bold; }
                .score-medium { color: #f39c12; font-weight: bold; }
                .score-low { color: #e74c3c; font-weight: bold; }
                .tag { background: #eee; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; margin-right: 4px; }
            </style>
        </head>
        <body>
            <header>
                <h1>🚀 Opportunity Radar</h1>
                <p>Generated at: {{ timestamp }}</p>
            </header>
            <table>
                <thead>
                    <tr>
                        <th>Score</th>
                        <th>Product / Keyword</th>
                        <th>Source</th>
                        <th>Money</th>
                        <th>Demand</th>
                        <th>Comp</th>
                        <th>Pain</th>
                        <th>Evidence / Links</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in items %}
                    <tr>
                        <td class="{{ 'score-high' if item.total_score > 50 else 'score-medium' if item.total_score > 10 else 'score-low' }}">
                            {{ item.total_score|round(2) }}
                        </td>
                        <td>
                            <strong>{{ item.product_name or item.keyword }}</strong><br>
                            <small>{{ item.domain or '' }}</small>
                        </td>
                        <td>{{ item.source }}</td>
                        <td>{{ item.money_score|round(1) }}</td>
                        <td>{{ item.demand_score|round(1) }}</td>
                        <td>{{ item.competition_score|round(1) }}</td>
                        <td>{{ item.pain_score|round(1) }}</td>
                        <td>
                            <a href="{{ item.url }}" target="_blank">Link</a> | 
                            {% for tag in item.tags %}
                                <span class="tag">{{ tag }}</span>
                            {% endfor %}
                            {% if item.snippets %}
                            <div style="font-size: 0.8em; color: #666; margin-top: 5px; max-width: 300px;">
                                <strong>Complaints:</strong>
                                <ul>
                                {% for s in item.snippets %}
                                    <li>{{ s }}</li>
                                {% endfor %}
                                </ul>
                            </div>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </body>
        </html>
        """

    def generate(self, data: List[Dict]):
        if not data:
            logger.warning("No data to generate report.")
            return

        df = pd.DataFrame(data)
        
        # CSV
        csv_path = self.output_dir / "report.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"CSV report saved to {csv_path}")

        # JSON
        json_path = self.output_dir / "report.json"
        df.to_json(json_path, orient="records", indent=4)
        logger.info(f"JSON report saved to {json_path}")

        # HTML
        from datetime import datetime
        env = Environment()
        template = env.from_string(self.template_str)
        
        # Prepare data for HTML (sort by score)
        items = sorted(data, key=lambda x: x['total_score'], reverse=True)
        
        html_content = template.render(
            items=items,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        html_path = self.output_dir / "report.html"
        html_path.write_text(html_content)
        logger.info(f"HTML report saved to {html_path}")
