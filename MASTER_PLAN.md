# 🚀 Ecosistema Micro-SaaS: Radar de Competencia E-commerce

Esta documentación sirve como **Single Source of Truth (SSoT)** para el proyecto. El objetivo es construir una factoría de micro-extensiones que alimenten una base de datos central de inteligencia comercial, monetizando tanto el acceso a herramientas específicas como el acceso a datos agregados.

---

## 🏛️ 1. Estructuras Inamovibles (El Núcleo)

### A. Central Data Hub (Supabase + Vercel)
Cualquier nueva pieza de software **DEBE** conectarse a esta infraestructura para mantener el efecto red.
- **Base de Datos (Supabase):** Repositorio central de tiendas, productos, eventos y rankings.
- **API Entry Point (Vercel):** Puerta de entrada única (`/api/sync`) para todas las extensiones. Esto oculta las claves de Supabase del lado del cliente.
- **Lógica de Ranking:** El éxito se mide por el `Hero Score` (dominancia de producto) y el `Stock Velocity`.

### B. Modelo de Datos Universal
Toda herramienta de scraping debe mapear sus resultados a este formato:
- `domain`: Identificador único de la entidad (la tienda).
- `metrics`: Objeto JSON con `avg_price`, `hero_score` y `discount_ratio`.
- `payload`: Datos específicos (ej. niveles de stock, nombres de competidores).

---

## 📂 2. Estructura del Proyecto

```bash
/SAAS_v2
├── /shopify_insider_ext       # V1: Extractor básico de productos (MVP funcional).
├── /shopify_inventory_spy    # V2: Análisis de stock y Ranking comparativo (En desarrollo).
├── /competitor_radar_api     # Backend unificado (Vercel + esquema Supabase).
├── /landing_page             # Web de marketing principal para conversión a Pro.
├── /shopify_study            # Scripts de análisis profundo en Python (Cerebro analítico).
└── /reports                  # Datos históricos minados (Opportunity Radar).
```

---

## 💰 3. Estrategia de Monetización y Stripe

### Modelo de Precios: "Micro-Transacción Disruptiva"
- **Free:** Acceso a métricas comparativas ciegas (Rankings, Percentiles). El usuario entrega sus datos de navegación a cambio de contexto.
- **Pay-per-Insight (3€):** Pago único a través de **Stripe Payment Links** para desbloquear un informe específico (ej. Lista de los 5 competidores directos, URL de proveedores de AliExpress).
- **LTD (Lifetime Deal) (25-49€):** Acceso "Pro" de por vida a todas las extensiones del ecosistema.

### Configuración de Stripe:
1. **Webhook:** Configurar en Vercel una ruta `/api/stripe-webhook` para actualizar la tabla `isPro` en Supabase tras el pago.
2. **Product Links:** Cada extensión usará un `Price ID` diferente para traquear qué herramienta genera más conversión.

---

## 🗺️ 4. Roadmap de Crecimiento Paulatino

### Fase 1: Consolidación del "Flywheel" (Actual)
- [ ] Conectar `shopify_inventory_spy` a Supabase vía Vercel.
- [ ] Implementar el sistema de Ranking real basado en los datos acumulados en `stores`.
- [ ] Lanzar el primer Stripe Payment Link de 3€.

### Fase 2: Expansión de Captación (Mes 1)
- [ ] **Nueva Extensión: AliExpress sourcing machine.** (Usar lógica de búsqueda por imagen/título).
- [ ] **Nueva Extensión: Review Sentiment Analyzer.** (Extraer reseñas para predecir si un producto es devuelto frecuentemente).

### Fase 3: El Producto B2B (Mes 3+)
- [ ] Crear un Dashboard web (SaaS) donde **Agencias de Marketing** paguen por ver las tiendas que están creciendo más rápido en España antes de que sean famosas.

---

## ⚠️ 5. Reglas de Oro para el Agente Humano/Bot
1. **Cero AI en Producción:** Toda la lógica de análisis debe ser matemática y basada en el DOM/JSON para mantener latencia baja y costes cero.
2. **Privacidad:** Las extensiones solo deben activarse en dominios detectados como Shopify para no penalizar el rendimiento del navegador.
3. **Escalabilidad:** Siempre que se añada una función de análisis en Python (`shopify_study`), se debe crear su versión simplificada en JS para las extensiones.
4. **Persistencia:** No mover datos fuera de Supabase. El archivo local `radar.db` es solo para backups o prototipado rápido.

---

## 🌐 6. Enlaces y Credenciales (Simbolismo)
- **Repo GitHub:** [DrDiazHurtado/saas_v2](https://github.com/DrDiazHurtado/saas_v2)
- **Supabase Project:** Configurar en `.env` (Ver `/competitor_radar_api/.env.example`).
- **Vercel Deployment:** [https://tu-radar-api.vercel.app](https://tu-radar-api.vercel.app)

---
*Ultima actualización: 14 de Febrero, 2026. Objetivo: 9K€ MRR vía Micro-transacciones y Datos.*
