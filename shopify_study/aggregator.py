import pandas as pd
from loguru import logger

class Aggregator:
    def __init__(self, session):
        self.session = session

    def get_global_stats(self):
        from shopify_study.storage import Metric
        data = self.session.query(Metric).all()
        if not data:
            return None

        df = pd.DataFrame([{
            'hero_score': m.hero_score,
            'discount_ratio': m.discount_ratio,
            'avg_variants': m.avg_variants,
            'urgency': m.urgency,
            'bundle': m.bundle,
            'total_products': m.total_products,
            'avg_price': m.avg_price,
            'inventory_recency': m.inventory_recency_days,
            'vendor_count': m.vendor_count
        } for m in data])

        stats = {
            'avg_products': df['total_products'].mean(),
            'avg_price_market': df['avg_price'].mean(),
            'sale_penetration': df['discount_ratio'].mean() * 100,
            'urgency_ratio': df['urgency'].mean() * 100,
            'bundle_ratio': df['bundle'].mean() * 100,
            'avg_launch_recency': df['inventory_recency'].mean(),
            'avg_variants': df['avg_variants'].mean(),
            # Segmentations
            'percent_brand_pure': (df['vendor_count'] == 1).mean() * 100,
            'percent_active_last_30d': (df['inventory_recency'] <= 30).mean() * 100
        }
        return stats, df

    def generate_insights(self, stats):
        insights = []
        
        if stats['sale_penetration'] > 30:
            insights.append(f"Agresividad Promocional: El {stats['sale_penetration']:.1f}% del catálogo medio está rebajado. El mercado compite por precio.")
        else:
            insights.append(f"Mantenimiento de Margen: Solo el {stats['sale_penetration']:.1f}% de productos tienen descuento. Estrategia de marca premium.")

        if stats['percent_active_last_30d'] > 60:
            insights.append("Alta Velocidad de Venta: Más del 60% de las tiendas han lanzado novedades en los últimos 30 días.")
        
        if stats['urgency_ratio'] > 50:
            insights.append(f"Conversión Presurizada: El {stats['urgency_ratio']:.0f}% de las webs analizadas usan FOMO agresivo.")

        if stats['percent_brand_pure'] > 70:
            insights.append("Soberanía de Marca: El 70% de las tiendas operan como marcas propias (DTC puro), no como revendedores.")

        insights.append(f"La complejidad media de producto es de {stats['avg_variants']:.1f} variantes. La personalización es el nuevo estándar.")

        return insights
