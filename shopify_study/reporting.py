import pandas as pd
import matplotlib.pyplot as plt
import os
from loguru import logger

class Reporter:
    @staticmethod
    def generate_html(stats, df, insights, output_path="shopify_study/report.html"):
        os.makedirs("shopify_study/assets", exist_ok=True)
        
        # Enhanced Visuals
        plt.style.use('dark_background')
        accent_color = '#6366f1'
        alt_accent = '#f43f5e'
        
        # Chart 1: Price Levels Distribution
        plt.figure(figsize=(10, 6))
        df['avg_price'].plot(kind='hist', bins=15, color=accent_color, edgecolor='white')
        plt.title('Segmentación de Precios en el Mercado ($)', fontsize=14, color='white', pad=20)
        plt.xlabel('Precio Promedio ($)')
        plt.ylabel('Nº de Tiendas')
        plt.grid(axis='y', alpha=0.1)
        plt.savefig('shopify_study/assets/price_seg.png', transparent=True)
        plt.close()

        # Chart 2: Triggers Heatmap (Bar)
        plt.figure(figsize=(10, 6))
        trigger_metrics = {
            'DTC Puro (1 Vendor)': stats['percent_brand_pure'],
            'Uso de Urgencia': stats['urgency_ratio'],
            'Uso de Bundles': stats['bundle_ratio'],
            'Lanzamientos <30d': stats['percent_active_last_30d']
        }
        plt.barh(list(trigger_metrics.keys()), list(trigger_metrics.values()), color=alt_accent)
        plt.xlim(0, 100)
        plt.title('Penetración de Estrategias Top (%)', fontsize=14, color='white', pad=20)
        plt.gca().invert_yaxis()
        for i, v in enumerate(trigger_metrics.values()):
            plt.text(v + 3, i, f"{v:.1f}%", color='white', va='center', fontweight='bold')
        plt.savefig('shopify_study/assets/strategy_heat.png', transparent=True)
        plt.close()

        # Generate HTML
        html_template = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Shopify Market Intelligence - Opportunity Radar</title>
            <style>
                :root {{ --primary: #818cf8; --bg: #020617; --card: #1e293b; --text: #f8fafc; --text-dim: #94a3b8; }}
                body {{ font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); padding: 40px; line-height: 1.6; }}
                .container {{ max-width: 1100px; margin: 0 auto; }}
                h1 {{ color: var(--primary); text-align: center; font-size: 3rem; margin-bottom: 50px; text-transform: uppercase; letter-spacing: -1px; }}
                h2 {{ color: var(--primary); margin-top: 40px; border-bottom: 1px solid #334155; padding-bottom: 10px; }}
                .hero-stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 40px; }}
                .stat-card {{ background: var(--card); padding: 30px; border-radius: 20px; text-align: center; border: 1px solid #334155; }}
                .stat-card h3 {{ color: var(--text-dim); font-size: 0.8rem; margin: 0; text-transform: uppercase; }}
                .stat-card .val {{ font-size: 2.5rem; font-weight: 800; color: var(--primary); margin: 10px 0; }}
                .insights-list {{ list-style: none; padding: 0; display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
                .insight-item {{ background: #0f172a; padding: 25px; border-radius: 12px; border-left: 5px solid var(--primary); font-weight: 500; }}
                .charts-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 40px; }}
                .chart-box {{ background: var(--card); padding: 20px; border-radius: 20px; border: 1px solid #334155; }}
                .footer {{ text-align: center; margin-top: 80px; color: var(--text-dim); font-size: 0.9rem; }}
                .tag {{ display: inline-block; background: var(--primary); color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; margin-bottom: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Shopify Insider Market Intelligence</h1>
                
                <div class="hero-stats">
                    <div class="stat-card"><h3>Precio Medio Mercado</h3><div class="val">${stats['avg_price_market']:.1f}</div><p>Ticket Promedio</p></div>
                    <div class="stat-card"><h3>Penetración Sale</h3><div class="val">{stats['sale_penetration']:.1f}%</div><p>Catálogo Rebajado</p></div>
                    <div class="stat-card"><h3>Active Launch</h3><div class="val">{stats['percent_active_last_30d']:.0f}%</div><p>Lanzamientos <30d</p></div>
                    <div class="stat-card"><h3>Avg Variants</h3><div class="val">{stats['avg_variants']:.1f}</div><p>Variants per Item</p></div>
                </div>

                <h2>Análisis Estratégico & Insights</h2>
                <div class="insights-list">
                    {''.join([f"<div class='insight-item'><div class='tag'>DATA INSIGHT</div>{i}</div>" for i in insights])}
                </div>

                <h2>Visualización de Datos Agregados</h2>
                <div class="charts-grid">
                    <div class="chart-box">
                        <img src="assets/price_seg.png" alt="Precios">
                    </div>
                    <div class="chart-box">
                        <img src="assets/strategy_heat.png" alt="Estrategias">
                    </div>
                </div>

                <div class="footer">
                    Generado automáticamente por Opportunity Radar & Shopify Insider. &copy; 2026.
                </div>
            </div>
        </body>
        </html>
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        return output_path
