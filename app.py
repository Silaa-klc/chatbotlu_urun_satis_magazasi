from flask import Flask, render_template, request, jsonify, session
from recommender import get_recommendations
import json
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_demo'

@app.route('/')
def index():
    """
    Ana sayfayı (sohbet arayüzü) render eder.
    """
    return render_template('index.html')

@app.route('/kadin')
def kadin():
    return render_template('kadin.html')

@app.route('/erkek')
def erkek():
    return render_template('erkek.html')

@app.route('/hakkimizda')
def hakkimizda():
    return render_template('hakkimizda.html')

@app.route('/urun/<int:product_id>')
def urun_detay(product_id):
    return render_template('urun_detay.html', product_id=product_id)

@app.route('/sepet')
def sepet():
    return render_template('sepet.html')

@app.route('/odeme')
def odeme():
    return render_template('odeme.html')

@app.route('/api/products')
def get_products():
    """
    Tüm ürünleri JSON olarak döndürür.
    """
    file_path = os.path.join(os.path.dirname(__file__), 'urunler.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/api/products/<int:product_id>')
def get_product_detail(product_id):
    """
    Tek bir ürünü JSON olarak döndürür.
    """
    file_path = os.path.join(os.path.dirname(__file__), 'urunler.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    product = next((item for item in data if item["id"] == product_id), None)
    if product:
        # Bedenleri dinamik olarak ekle
        if product['kategori'] == 'Ayakkabı':
            product['bedenler'] = [str(i) for i in range(36, 46)]
        elif product['kategori'] in ['Aksesuar', 'Çanta', 'Gözlük', 'Saat', 'Cüzdan', 'Şal', 'Atkı', 'Bere', 'Küpe', 'Kravat']:
            product['bedenler'] = ['Standart']
        else:
            product['bedenler'] = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
            
        return jsonify(product)
    return jsonify({"error": "Ürün bulunamadı"}), 404

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Frontend'den gelen mesajı alır, öneri motoruna gönderir ve sonucu JSON döner.
    """
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"error": "Mesaj boş olamaz"}), 400
    
    # Context'i session'dan al
    context = session.get('chat_context', {})
    
    # Öneri motorunu çalıştır
    result, updated_context = get_recommendations(user_message, context)
    
    # Güncellenmiş context'i kaydet
    session['chat_context'] = updated_context
    
    response_data = {
        "response": result["content"],
        "products": result.get("products", [])
    }
        
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
