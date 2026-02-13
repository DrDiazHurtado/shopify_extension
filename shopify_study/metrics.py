from datetime import datetime

class MetricsCalculator:
    @staticmethod
    def calculate_store_metrics(products_data, hero_product, urgency, bundle):
        if not products_data:
            return None

        prices = [p['price'] for p in products_data]
        avg_price = sum(prices) / len(prices) if prices else 0
        total_products = len(products_data)
        
        # 1. Sale Density: % of products with a discount
        products_with_discount = [p for p in products_data if p['compare_at_price'] and p['compare_at_price'] > p['price']]
        discount_ratio = len(products_with_discount) / total_products if total_products > 0 else 0
        
        # 2. Hero Dominance
        hero_score = hero_product['price'] / avg_price if avg_price > 0 else 0
        
        # 3. Variant Complexity
        avg_variants = sum([p['variants_count'] for p in products_data]) / total_products if total_products > 0 else 0

        # 4. Inventory Freshness: Days since last product creation
        all_dates = [p['created_at'] for p in products_data]
        if all_dates:
            last_date = max(all_dates)
            delta = (datetime.utcnow().replace(tzinfo=last_date.tzinfo) - last_date).days
            inventory_recency_days = max(0, delta)
        else:
            inventory_recency_days = 999

        # 5. Vendor diversity (Brand vs Dropshipper/Marketplace)
        vendors = set([p['vendor'] for p in products_data])
        vendor_count = len(vendors)

        return {
            'hero_score': hero_score,
            'discount_ratio': discount_ratio,
            'avg_variants': avg_variants,
            'urgency': urgency,
            'bundle': bundle,
            'total_products': total_products,
            'avg_price': avg_price,
            'inventory_recency_days': inventory_recency_days,
            'vendor_count': vendor_count
        }
