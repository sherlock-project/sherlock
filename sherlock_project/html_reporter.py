"""
HTML Raporlama Modulu
Jinja2 ile HTML sablonu export
"""

from pathlib import Path
from typing import List
from datetime import datetime

from jinja2 import Template

from sherlock_project.result import QueryResult


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sherlock Report - {{ username }}</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            color: #eee;
            padding: 20px;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: #3498db;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .meta {
            color: #888;
            margin-bottom: 20px;
        }
        .summary {
            background: #16213e;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .summary h2 {
            color: #3498db;
            margin-bottom: 10px;
        }
        .stats {
            display: flex;
            gap: 30px;
            margin-top: 15px;
        }
        .stat {
            text-align: center;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #2ecc71;
        }
        .stat-label {
            color: #888;
            font-size: 0.9em;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: #16213e;
            border-radius: 10px;
            overflow: hidden;
        }
        th {
            background: #1f538d;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #2a2a4a;
        }
        tr:hover {
            background: #1a2a5a;
        }
        .status-found {
            color: #2ecc71;
            font-weight: bold;
        }
        .status-not-found {
            color: #e74c3c;
        }
        a {
            color: #3498db;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Sherlock Report</h1>
        <p class="meta">Username: <strong>{{ username }}</strong> | Generated: {{ timestamp }}</p>

        <div class="summary">
            <h2>Summary</h2>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{{ found_count }}</div>
                    <div class="stat-label">Accounts Found</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{{ total_checked }}</div>
                    <div class="stat-label">Sites Checked</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{{ success_rate }}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
            </div>
        </div>

        <h2>Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Site</th>
                    <th>Status</th>
                    <th>Response Time</th>
                    <th>URL</th>
                </tr>
            </thead>
            <tbody>
                {% for result in results %}
                <tr>
                    <td>{{ result.site_name }}</td>
                    <td class="{% if result.status == 'Claimed' %}status-found{% else %}status-not-found{% endif %}">
                        {{ result.status }}
                    </td>
                    <td>{{ "%.2f"|format(result.query_time) }}s</td>
                    <td><a href="{{ result.site_url_user }}" target="_blank">{{ result.site_url_user }}</a></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
'''


class HTMLReporter:
    """HTML rapor uretici"""

    def generate(
        self,
        username: str,
        results: List[QueryResult],
        output_path: str
    ) -> str:
        """
        HTML raporu olustur

        Args:
            username: Aranan kullanici adi
            results: Tarama sonuclari
            output_path: Cikis dosya yolu

        Returns:
            Olusturulan dosya yolu
        """
        template = Template(HTML_TEMPLATE)

        found_count = sum(1 for r in results if r.status.value == 'Claimed')
        total = len(results)
        success_rate = round((found_count / total * 100), 1) if total > 0 else 0

        html = template.render(
            username=username,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M'),
            results=results,
            found_count=found_count,
            total_checked=total,
            success_rate=success_rate
        )

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return output_path
