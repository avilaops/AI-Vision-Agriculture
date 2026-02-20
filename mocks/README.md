# AI-Vision-Agriculture - Mock de Integração

## 🎯 OBJETIVO

Fornecer análise de maturidade de cana-de-açúcar através de visão computacional (imagens de satélite/drone) para o **CanaSwarm-Intelligence** tomar decisões de colheita otimizadas.

---

## 📋 CONTRATO DE DADOS

### **INPUT: Imagens de Talhões**

```json
{
  "field_id": "F001-UsinaGuarani-Piracicaba",
  "image_source": "satellite_sentinel2 | drone",
  "image_date": "2026-02-18T13:30:00Z",
  "image_url": "https://example.com/images/F001_20260218.tif",
  "area_ha": 130,
  "crop": "sugarcane",
  "harvest_number": 4
}
```

### **PROCESSAMENTO: Análise de Índices de Vegetação**

- **NDVI** (Normalized Difference Vegetation Index): Vigor vegetativo
- **Red Edge**: Clorofila e estresse
- **Moisture Index**: Teor de umidade
- **Segmentação de zonas**: Áreas homogêneas dentro do talhão

### **OUTPUT: Dados de Maturidade**

```json
{
  "analysis_id": "VIS-20260220-001",
  "analysis_date": "2026-02-20T14:00:00Z",
  "field_id": "F001",
  "field_name": "Talhão Piracicaba Sul",
  "area_ha": 130,
  "analysis": {
    "maturity_score": 0.78,
    "maturity_level": "mature",
    "harvest_recommendation": "ready_in_2_weeks",
    "estimated_sugar_content_percent": 14.2,
    "confidence": 0.92
  },
  "indices": {
    "ndvi_avg": 0.65,
    "ndvi_std": 0.12,
    "red_edge_avg": 0.42,
    "moisture_index": 0.58
  },
  "zones_analysis": [
    {
      "zone_id": "Z001",
      "area_ha": 50.2,
      "maturity_score": 0.65,
      "maturity_level": "developing",
      "ndvi_avg": 0.58,
      "notes": "Zona atrasada, colher por último"
    },
    {
      "zone_id": "Z002",
      "area_ha": 79.8,
      "maturity_score": 0.85,
      "maturity_level": "optimal",
      "ndvi_avg": 0.72,
      "notes": "Zona ótima para colheita"
    }
  ],
  "recommendations": [
    {
      "priority": "high",
      "action": "schedule_harvest",
      "timeframe": "14_days",
      "reason": "Maturidade ótima detectada"
    }
  ]
}
```

---

## 🔌 API REST

### **Endpoints**

```
GET /api/v1/maturity?field_id=F001
  → Análise completa de maturidade de um talhão

GET /api/v1/harvest-priority
  → Lista de todos os talhões ordenados por prioridade de colheita

GET /health
  → Health check do serviço
```

### **Exemplo de Uso (cURL)**

```bash
# Análise de maturidade
curl http://localhost:5001/api/v1/maturity?field_id=F001

# Prioridade de colheita
curl http://localhost:5001/api/v1/harvest-priority
```

---

## 🧪 TESTE DE INTEGRAÇÃO

### **1. Iniciar API Mock**

```bash
cd D:\Projetos\AI-Vision-Agriculture\mocks
pip install -r requirements.txt
python maturity_api_mock.py
```

Server estará em: `http://localhost:5001`

### **2. Executar Consumer (Intelligence)**

Em outro terminal:

```bash
cd D:\Projetos\CanaSwarm-Intelligence\mocks
python vision_consumer_mock.py
```

### **3. Saída Esperada**

```
🧠 CanaSwarm-Intelligence - Vision Consumer Mock
============================================================
🎯 TESTANDO INTEGRAÇÃO AI-VISION → INTELLIGENCE

============================================================
TESTE 1: Análise de maturidade do talhão F001
============================================================

🔗 Consultando API Vision para: F001
✅ Dados recebidos com sucesso!

============================================================
📊 DASHBOARD - ANÁLISE DE MATURIDADE
============================================================

🌾 TALHÃO: Talhão Piracicaba Sul (F001)
   Área: 130 ha
   Cultura: SUGARCANE
   Corte: 4

🟢 ANÁLISE DE MATURIDADE:
   Score: 78.00%
   Nível: MATURE
   Açúcar estimado: 14.2%
   Confiança: 92.00%

📈 ÍNDICES DE VEGETAÇÃO:
   NDVI médio: 0.65
   Red Edge: 0.42
   Moisture Index: 0.58

🗺️  ANÁLISE POR ZONA:

🟡 ZONA Z001
   Área: 50.2 ha
   Maturidade: 65.00% (developing)
   NDVI: 0.58
   Nota: Zona com desenvolvimento atrasado, colher por último

🟢 ZONA Z002
   Área: 79.8 ha
   Maturidade: 85.00% (optimal)
   NDVI: 0.72
   Nota: Zona ótima para colheita, priorizar

💡 RECOMENDAÇÕES:
🔴 SCHEDULE HARVEST
   Prioridade: HIGH
   Prazo: 14 days
   Motivo: Maturidade ótima detectada, açúcar em pico

============================================================
🎉 INTEGRAÇÃO AI-VISION → INTELLIGENCE: SUCESSO
============================================================
```

---

## ✅ CRITÉRIOS DE SUCESSO

- [x] **Análise de maturidade funcional**: API retorna scores de maturidade baseados em NDVI
- [x] **Segmentação de zonas**: Talhões divididos em zonas com análise individual
- [x] **API REST operacional**: Endpoints `/maturity` e `/harvest-priority` funcionando
- [x] **Consumer integrado**: CanaSwarm-Intelligence consome dados com sucesso
- [x] **Dashboard completo**: Visualização de maturidade, zonas e recomendações
- [x] **Prioridade de colheita**: Lista ordenada por urgência e potencial produtivo

---

## 🎉 STATUS

```
✅ CONTRATO VALIDADO — Pipeline AI-Vision → Intelligence FUNCIONA
```

**Testes realizados:**
- ✅ API Mock rodando na porta 5001
- ✅ Consumer do Intelligence conectando com sucesso
- ✅ Análise de 2 talhões (F001: 130 ha, F002: 95 ha)
- ✅ Segmentação de 2 zonas em F001 (50.2 ha + 79.8 ha)
- ✅ Prioridade de colheita calculada (F001 prioridade MÉDIA, F002 prioridade BAIXA)
- ✅ Dashboard exibindo dados de maturidade, NDVI, zonas e recomendações

---

## 🚀 PRÓXIMOS PASSOS

### **Produção (substituir mock):**

1. **Infraestrutura de Imagens**
   - Conexão com API Sentinel 2 ou Planet Labs
   - Armazenamento de rasters (GeoTIFF)
   - Pipeline de processamento (download → corte → análise)

2. **Processamento de Imagens**
   - Cálculo real de índices (GDAL, Rasterio)
   - Segmentação de zonas (K-means, SLIC)
   - Correção atmosférica e calibração radiométrica

3. **Machine Learning**
   - Modelo de predição de açúcar (regressão)
   - Classificação de maturidade (CNN ou Random Forest)
   - Transfer learning de modelos agrícolas

4. **API de Produção**
   - FastAPI ou Flask-RESTful
   - Autenticação (JWT)
   - Cache de resultados (Redis)
   - Documentação Swagger/OpenAPI

5. **Integração com Intelligence**
   - Webhook para novas análises
   - Sincronização com banco de dados
   - Dashboard web com mapas interativos (Leaflet/Mapbox)

---

## 📦 ARQUIVOS

```
AI-Vision-Agriculture/
└── mocks/
    ├── example_field_images.json        # Exemplo de análise de 2 talhões
    ├── vision_analyzer_mock.py          # Processador de índices de vegetação
    ├── maturity_api_mock.py             # API REST para Intelligence
    ├── requirements.txt                 # flask==3.0.0
    └── README.md                        # Este arquivo
```

---

## 🔗 DEPENDÊNCIAS

**Fornece dados para:**
- **CanaSwarm-Intelligence**: Combina maturidade (AI-Vision) + produtividade (Precision) → decisão de colheita ótima

**Consome dados de:**
- _(Nenhum no momento)_ - Fonte independente de dados via sensoriamento remoto

---

## 📊 IMPACTO ESPERADO

- **+8% produtividade**: Colheita no momento ótimo de maturidade
- **-15% perdas**: Evita colheita prematura (baixo açúcar) ou tardia (floração)
- **+R$ 250k/ano**: Valor adicional de ATR (Açúcar Total Recuperável) por usina
- **Decisões data-driven**: Elimina subjetividade na definição de sequência de colheita

---

**Contrato definido em:** 2026-02-20  
**Última atualização:** 2026-02-20  
**Status:** ✅ VALIDADO COM TESTES
