#!/usr/bin/env python3
"""
AI-Vision-Agriculture - Maturity API Mock

API REST para fornecer dados de maturidade para CanaSwarm-Intelligence
"""

import json
from pathlib import Path
from flask import Flask, jsonify, request

app = Flask(__name__)

# Carrega dados de exemplo
DATA_FILE = Path(__file__).parent / "example_field_images.json"

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    ANALYSIS_DATA = json.load(f)


@app.route('/')
def home():
    return jsonify({
        'service': 'AI-Vision-Agriculture API',
        'version': '1.0.0-mock',
        'status': 'running',
        'endpoints': {
            '/api/v1/maturity': 'GET - Análise de maturidade por field_id',
            '/api/v1/harvest-priority': 'GET - Lista de prioridade de colheita',
            '/health': 'GET - Health check'
        }
    })


@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': '2026-02-20T14:00:00Z'})


@app.route('/api/v1/maturity', methods=['GET'])
def get_maturity():
    """
    Retorna análise de maturidade para um talhão
    
    Query params:
        field_id: ID do talhão (ex: F001)
    """
    field_id = request.args.get('field_id')
    
    if not field_id:
        return jsonify({'error': 'field_id é obrigatório'}), 400
    
    # Busca talhão
    field_data = None
    for field in ANALYSIS_DATA['fields']:
        if field['field_id'] == field_id:
            field_data = field
            break
    
    if not field_data:
        return jsonify({'error': f'Talhão {field_id} não encontrado'}), 404
    
    # Retorna análise
    response = {
        'analysis_id': ANALYSIS_DATA['analysis_id'],
        'analysis_date': ANALYSIS_DATA['analysis_date'],
        'field_id': field_data['field_id'],
        'field_name': field_data['field_name'],
        'area_ha': field_data['area_ha'],
        'crop': field_data['crop'],
        'harvest_number': field_data['harvest_number'],
        'maturity': field_data['analysis'],
        'indices': field_data['indices'],
        'zones': field_data.get('zones_analysis', []),
        'recommendations': field_data.get('recommendations', [])
    }
    
    return jsonify(response)


@app.route('/api/v1/harvest-priority', methods=['GET'])
def get_harvest_priority():
    """
    Retorna lista de talhões ordenada por prioridade de colheita
    """
    fields_priority = []
    
    for field in ANALYSIS_DATA['fields']:
        analysis = field['analysis']
        
        # Calcula prioridade
        if analysis['maturity_level'] == 'optimal':
            priority = 1
            priority_label = 'ALTA'
        elif analysis['maturity_level'] == 'mature':
            priority = 2
            priority_label = 'MÉDIA'
        elif analysis['maturity_level'] == 'developing':
            priority = 3
            priority_label = 'BAIXA'
        else:
            priority = 4
            priority_label = 'AGUARDAR'
        
        fields_priority.append({
            'field_id': field['field_id'],
            'field_name': field['field_name'],
            'area_ha': field['area_ha'],
            'maturity_score': analysis['maturity_score'],
            'maturity_level': analysis['maturity_level'],
            'sugar_content_percent': analysis['estimated_sugar_content_percent'],
            'harvest_recommendation': analysis['harvest_recommendation'],
            'priority': priority,
            'priority_label': priority_label
        })
    
    # Ordena por prioridade
    fields_priority.sort(key=lambda x: x['priority'])
    
    return jsonify({
        'analysis_id': ANALYSIS_DATA['analysis_id'],
        'total_fields': len(fields_priority),
        'fields': fields_priority
    })


if __name__ == '__main__':
    print("🤖 AI-Vision-Agriculture - Maturity API Mock")
    print("="*60)
    print("\n🚀 Servidor iniciando em http://localhost:5001")
    print("\n📡 Endpoints disponíveis:")
    print("   GET /api/v1/maturity?field_id=F001")
    print("   GET /api/v1/harvest-priority")
    print("   GET /health")
    print("\n✅ Pronto para receber requisições do CanaSwarm-Intelligence\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
