from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import json
import os
import random
import re

# Veriyi JSON dosyasından yükle
# Data reload trigger v2
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), 'urunler.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    # Arama için birleşik metin alanı oluştur
    df['search_text'] = df['urun_adi'] + " " + df['detayli_aciklama'] + " " + df['kategori'] + " " + df['renk'] + " " + df['cinsiyet']
    return df

df = load_data()

# TF-IDF Vektörleştiriciyi başlat
turkish_stop_words = [
    'acaba', 'ama', 'aslında', 'az', 'bazı', 'belki', 'biri', 'birkaç', 'birşey', 'biz', 
    'bu', 'çok', 'çünkü', 'da', 'daha', 'de', 'defa', 'diye', 'eğer', 'en', 'gibi', 'hem', 
    'hep', 'hepsi', 'her', 'hiç', 'için', 'ile', 'ise', 'kez', 'ki', 'kim', 'mı', 'mi', 
    'mu', 'mü', 'nasıl', 'ne', 'neden', 'nerde', 'nerede', 'nereye', 'niçin', 'niye', 'o', 
    'sanki', 'şey', 'siz', 'şu', 'tüm', 've', 'veya', 'ya', 'yani', 'bir', 'ben', 'sen',
    'istiyorum', 'arıyorum', 'var', 'yok', 'bana', 'göster', 'bul',
    'kıyafet', 'kıyafetler', 'ürün', 'ürünler', 'eşya', 'parça', 'model', 'modeller',
    'ucuz', 'pahalı', 'uygun', 'ekonomik', 'lüks', 'kaliteli'
]

tfidf_vectorizer = TfidfVectorizer(stop_words=turkish_stop_words)

# Ürün açıklamalarını vektör matrisine dönüştür
tfidf_matrix = tfidf_vectorizer.fit_transform(df['search_text'])

def format_product(product, score=1.0):
    stock = int(product.get('stok', 0))
    fomo_text = ""
    if stock < 4:
        fomo_text = f"🔥 Acele et, son {stock} ürün!"
    elif stock < 8:
        fomo_text = "⚡ Tükenmek üzere!"
        
    return {
        "id": int(product['id']),
        "urun_adi": product['urun_adi'],
        "fiyat": float(product['fiyat']),
        "aciklama": product['detayli_aciklama'],
        "resim": product.get('resim', ''),
        "skor": float(score),
        "stok": stock,
        "fomo_text": fomo_text
    }

def get_similar_products(product_id):
    """
    Verilen ürün ID'sine göre Cosine Similarity kullanarak en benzer ürünleri bulur.
    """
    # Ürünün indexini bul
    try:
        product_idx = df[df['id'] == product_id].index[0]
    except IndexError:
        return []

    # Benzerlik hesapla
    cosine_sim = cosine_similarity(tfidf_matrix[product_idx], tfidf_matrix)
    
    # Skorları listele (index, skor)
    sim_scores = list(enumerate(cosine_sim[0]))
    
    # Skora göre sırala (en yüksekten en düşüğe)
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # İlk eleman kendisi olacağı için onu atla, sonraki 3 ürünü al
    sim_scores = sim_scores[1:4]
    
    product_indices = [i[0] for i in sim_scores]
    
    similar_products = []
    for i in product_indices:
        product = df.iloc[i]
        similar_products.append(format_product(product, sim_scores[product_indices.index(i)][1]))
        
    return similar_products

def get_intent(query):
    """
    Gelişmiş kural tabanlı niyet analizi.
    """
    query = query.lower()
    
    # Özel Durum: Kargo Pantolon
    if "kargo pantolon" in query:
        return "search"
    
    patterns = {
        "greeting": ['merhaba', 'selam', 'hey', 'günaydın', 'iyi günler', 'tünaydın', 'iyi akşamlar'],
        "thanks": ['teşekkür', 'sağol', 'mersi', 'eyvallah', 'eline sağlık'],
        "help": ['yardım', 'ne yapabilirsin', 'nasıl çalışır', 'komutlar', 'neler var'],
        "surprise": ['rastgele', 'farketmez', 'öneri yap', 'şaşırt beni', 'herhangi', 'şansıma'],
        "shipping": ['kargo', 'teslimat', 'süresi', 'kaç günde', 'gelir', 'gönderim', 'nakliye'],
        "return": ['iade', 'değişim', 'geri', 'beğenmedim', 'garanti', 'iptal'],
        "payment": ['ödeme', 'taksit', 'kart', 'kapıda', 'havale', 'eft', 'nakit'],
        "contact": ['iletişim', 'telefon', 'adres', 'yeriniz', 'nerede', 'mail', 'eposta', 'ulaşım'],
        "combination": ['kombin', 'takım yap', 'ne giysem', 'kıyafet seç', 'giydir'],
        "size_help": ['beden', 'boyum', 'kilom', 'kaç beden', 'hangi beden', 'ölçü']
    }

    # Eğer sorguda açıkça bir kategori varsa (örn: 'pantolon öner'), bunu kombin olarak değil arama olarak algıla
    # Ancak 'kombin' kelimesi geçiyorsa yine kombin olsun.
    is_explicit_combination = 'kombin' in query or 'takım' in query
    
    if not is_explicit_combination:
        # Kategorileri kontrol et
        categories = ['elbise', 'pantolon', 'ceket', 'ayakkabı', 'şal', 'yağmurluk', 'takım elbise', 'tişört', 'bot', 'hırka', 'çanta', 'gömlek', 'şort', 'gözlük', 'kazak', 'etek', 'saat', 'bere', 'sandalet', 'cüzdan', 'tayt', 'yelek', 'bluz', 'kemer', 'pijama', 'eşofman', 'küpe', 'kravat', 'trençkot', 'boxer', 'mayo', 'atkı']
        if any(cat in query for cat in categories):
            return "search"

    for intent, keywords in patterns.items():
        if any(word in query for word in keywords):
            return intent
            
    return "search"

def extract_entities(query):
    """
    Sorgudan renk, kategori, cinsiyet ve fiyat tercihlerini çıkarır.
    """
    query = query.lower()
    entities = {
        "color": None,
        "category": None,
        "gender": None,
        "sort": None # 'cheap', 'expensive'
    }
    
    # Renkler
    colors = ['kırmızı', 'mavi', 'yeşil', 'sarı', 'siyah', 'beyaz', 'gri', 'lacivert', 'bordo', 'pembe', 'turuncu', 'kahverengi', 'bej', 'krem', 'mor', 'lila', 'haki', 'gümüş', 'altın']
    for color in colors:
        if color in query:
            entities["color"] = color
            break # İlk bulunan rengi al
            
    # Kategoriler (Basit eşleştirme)
    categories = ['elbise', 'pantolon', 'ceket', 'ayakkabı', 'şal', 'yağmurluk', 'takım elbise', 'tişört', 'bot', 'hırka', 'çanta', 'gömlek', 'şort', 'gözlük', 'kazak', 'etek', 'saat', 'bere', 'sandalet', 'cüzdan', 'tayt', 'yelek', 'bluz', 'kemer', 'pijama', 'eşofman', 'küpe', 'kravat', 'trençkot', 'boxer', 'mayo', 'atkı', 'sweatshirt', 'mont', 'kaban', 'jean', 'kot', 'takım', 'iç giyim', 'plaj giyim', 'ev giyim']
    # Uzun kelimeleri önce kontrol et (Örn: 'takım elbise' vs 'elbise')
    categories.sort(key=len, reverse=True)
    
    for cat in categories:
        if cat in query:
            entities["category"] = cat
            break
            
    # Cinsiyet
    if any(w in query for w in ['kadın', 'bayan', 'kız', 'bayanlara']):
        entities["gender"] = ['Kadın', 'Unisex']
    elif any(w in query for w in ['erkek', 'bay', 'adam', 'erkeklere']):
        entities["gender"] = ['Erkek', 'Unisex']
        
    # Fiyat Sıralaması
    if any(w in query for w in ['ucuz', 'uygun', 'ekonomik', 'düşük fiyat']):
        entities["sort"] = 'cheap'
    if any(w in query for w in ['pahalı', 'lüks', 'kaliteli', 'yüksek fiyat']):
        entities["sort"] = 'expensive'
        
    return entities

def create_outfit(query, df):
    """
    Kullanıcı sorgusuna göre mantıklı bir kombin oluşturur.
    """
    query = query.lower()
    
    # 1. Stil/Mevsim Belirleme
    style = None
    if any(w in query for w in ['yaz', 'sıcak', 'plaj', 'tatil', 'deniz']):
        style = "summer"
    elif any(w in query for w in ['kış', 'soğuk', 'kar', 'yağmur']):
        style = "winter"
    elif any(w in query for w in ['spor', 'koşu', 'yürüyüş', 'rahat', 'gym']):
        style = "sport"
    elif any(w in query for w in ['düğün', 'davet', 'iş', 'ofis', 'klasik', 'şık', 'resmi', 'gece']):
        style = "formal"
    elif any(w in query for w in ['günlük', 'rahat', 'casual']):
        style = "casual"
    
    # Eğer stil belirtilmemişse, rastgele mantıklı bir stil seç
    if not style:
        style = random.choice(["casual", "sport", "formal", "summer", "winter"])
        
    # 2. Cinsiyet Belirleme
    gender = None
    if any(w in query for w in ['kadın', 'bayan', 'kız']):
        gender = "Kadın"
    elif any(w in query for w in ['erkek', 'bay', 'adam']):
        gender = "Erkek"
    
    # Eğer cinsiyet belirtilmemişse, rastgele bir cinsiyet seçelim ki kombin tutarlı olsun
    # Veya "Unisex" ürünleri de dahil edelim.
    target_gender = gender if gender else random.choice(["Kadın", "Erkek"])

    # Renk Tercihi Belirleme
    color_pref = None
    if any(w in query for w in ['açık renk', 'beyaz', 'bej', 'krem', 'canlı']):
        color_pref = "light"
    elif any(w in query for w in ['koyu renk', 'siyah', 'lacivert', 'karanlık']):
        color_pref = "dark"

    light_colors = ['Beyaz', 'Bej', 'Krem', 'Gri', 'Sarı', 'Pembe', 'Gümüş', 'Altın', 'Mavi', 'Yeşil', 'Turuncu', 'Camel', 'Çok Renkli', 'Siyah-Beyaz', 'Siyah-Gri-Beyaz']
    dark_colors = ['Siyah', 'Lacivert', 'Kahverengi', 'Bordo', 'Haki', 'Kırmızı', 'Kırmızı-Siyah']
        
    # 3. Kombin Şablonları (Kategori Listesi ve Opsiyonel Anahtar Kelimeler)
    # Format: {"cats": [Kategoriler], "keywords": [Aranacak Kelimeler (Opsiyonel)], "required": True/False}
    
    templates = {
        "summer": {
            "Kadın": [
                {"cats": ["Elbise", "Plaj Giyim"], "keywords": ["yazlık", "çiçekli", "askılı", "mini", "uçuş"], "required": True},
                {"cats": ["Ayakkabı"], "keywords": ["sandalet", "terlik", "açık"], "required": True},
                {"cats": ["Aksesuar"], "keywords": ["gözlük", "şapka", "çanta"], "required": False}
            ],
            "Erkek": [
                {"cats": ["Tişört", "Gömlek"], "keywords": ["kısa kol", "keten", "yazlık"], "required": True},
                {"cats": ["Şort", "Plaj Giyim"], "keywords": [], "required": True},
                {"cats": ["Ayakkabı"], "keywords": ["sandalet", "terlik", "sneaker"], "required": True},
                {"cats": ["Aksesuar"], "keywords": ["gözlük", "şapka"], "required": False}
            ]
        },
        "winter": {
            "Kadın": [
                {"cats": ["Dış Giyim"], "keywords": ["mont", "kaban", "parka"], "required": True},
                {"cats": ["Kazak", "Sweatshirt", "Hırka"], "keywords": ["yünlü", "kalın", "örgü"], "required": True},
                {"cats": ["Pantolon"], "keywords": ["kadife", "yünlü", "kalın", "jean"], "required": True},
                {"cats": ["Ayakkabı"], "keywords": ["bot", "çizme"], "required": True},
                {"cats": ["Aksesuar"], "keywords": ["bere", "atkı", "eldiven"], "required": False}
            ],
            "Erkek": [
                {"cats": ["Dış Giyim"], "keywords": ["mont", "kaban", "parka"], "required": True},
                {"cats": ["Kazak", "Sweatshirt", "Hırka"], "keywords": ["yünlü", "kalın", "örgü"], "required": True},
                {"cats": ["Pantolon"], "keywords": ["kadife", "yünlü", "kalın", "jean"], "required": True},
                {"cats": ["Ayakkabı"], "keywords": ["bot"], "required": True},
                {"cats": ["Aksesuar"], "keywords": ["bere", "atkı"], "required": False}
            ]
        },
        "sport": {
            "Kadın": [
                {"cats": ["Spor Giyim", "Tayt"], "keywords": [], "required": True},
                {"cats": ["Tişört", "Sweatshirt"], "keywords": ["fit", "dry", "spor"], "required": True},
                {"cats": ["Ayakkabı"], "keywords": ["spor", "koşu", "yürüyüş"], "required": True}
            ],
            "Erkek": [
                {"cats": ["Spor Giyim", "Eşofman"], "keywords": [], "required": True},
                {"cats": ["Tişört", "Sweatshirt"], "keywords": ["fit", "dry", "spor"], "required": True},
                {"cats": ["Ayakkabı"], "keywords": ["spor", "koşu"], "required": True}
            ]
        },
        "formal": {
            "Kadın": [
                {"cats": ["Elbise", "Takım Elbise"], "keywords": ["abiye", "şık", "gece", "davet", "düğün", "nişan", "mezuniyet", "zarif", "asil", "kadife", "saten"], "required": True},
                {"cats": ["Ayakkabı"], "keywords": ["topuklu", "stiletto", "klasik"], "required": True},
                {"cats": ["Aksesuar"], "keywords": ["çanta", "takı", "portföy"], "required": False}
            ],
            "Erkek": [
                {"cats": ["Takım Elbise"], "keywords": ["klasik", "şık", "davet"], "required": True},
                {"cats": ["Ayakkabı"], "keywords": ["klasik", "deri", "kösele"], "required": True},
                {"cats": ["Aksesuar"], "keywords": ["kemer", "kravat"], "required": True}
            ]
        },
        "casual": {
            "Kadın": [
                {"cats": ["Pantolon", "Etek"], "keywords": ["kot", "jean", "rahat"], "required": True},
                {"cats": ["Tişört", "Gömlek", "Bluz"], "keywords": ["basic", "günlük"], "required": True},
                {"cats": ["Ayakkabı"], "keywords": ["sneaker", "günlük", "babet"], "required": True},
                {"cats": ["Aksesuar"], "keywords": ["çanta", "sırt çantası"], "required": False}
            ],
            "Erkek": [
                {"cats": ["Pantolon"], "keywords": ["kot", "jean", "chino"], "required": True},
                {"cats": ["Tişört", "Gömlek", "Sweatshirt"], "keywords": ["basic", "polo", "günlük"], "required": True},
                {"cats": ["Ayakkabı"], "keywords": ["sneaker", "günlük"], "required": True}
            ]
        }
    }
    
    # Seçilen şablona göre ürünleri bul
    # Eğer stil/cinsiyet kombinasyonu yoksa casual/target_gender kullan
    style_templates = templates.get(style, templates["casual"])
    selected_template = style_templates.get(target_gender, templates["casual"]["Erkek"]) # Fallback to Erkek if something goes wrong
    
    outfit = []
    used_ids = set()
    
    for step in selected_template:
        categories = step["cats"]
        keywords = step["keywords"]
        is_required = step.get("required", False)
        
        # 1. Kategori ve Cinsiyet Filtresi
        # Cinsiyet: Hedef cinsiyet VEYA Unisex
        candidates = df[
            (df['kategori'].isin(categories)) & 
            (df['cinsiyet'].isin([target_gender, 'Unisex'])) &
            (~df['id'].isin(used_ids))
        ]

        # Renk Filtresi
        if color_pref == "light":
            color_candidates = candidates[candidates['renk'].isin(light_colors)]
            if not color_candidates.empty:
                candidates = color_candidates
        elif color_pref == "dark":
            color_candidates = candidates[candidates['renk'].isin(dark_colors)]
            if not color_candidates.empty:
                candidates = color_candidates
        
        # 2. Anahtar Kelime Filtresi (Varsa)
        if keywords:
            if not candidates.empty:
                # Regex ile kelime araması
                keyword_pattern = '|'.join(keywords)
                filtered_candidates = candidates[
                    candidates['search_text'].str.contains(keyword_pattern, case=False, na=False)
                ]
                
                # Eğer anahtar kelimeye uyan ürün varsa onları kullan
                if not filtered_candidates.empty:
                    candidates = filtered_candidates
                else:
                    # Anahtar kelimeye uyan yoksa
                    if is_required:
                        # Eğer zorunlu bir parçaysa (örn: elbise), filtrelemeden devam et (hiç yoktan iyidir)
                        pass 
                    else:
                        # Zorunlu değilse (örn: aksesuar), atla
                        continue
        
        # ÖZEL KURAL: Formal stilde bot önerme
        if style == "formal" and "Ayakkabı" in categories:
             # Bot kelimesi geçenleri ele
             candidates = candidates[~candidates['search_text'].str.contains("bot", case=False, na=False)]

        if not candidates.empty:
            # Rastgele bir ürün seç
            product = candidates.sample(1).iloc[0]
            outfit.append(format_product(product))
            used_ids.add(product['id'])
            
    return outfit, style, target_gender

def get_recommendations(user_query, context=None):
    """
    Kullanıcı sorgusuna göre en benzer ürünleri döndürür.
    """
    if context is None:
        context = {}

    intent = get_intent(user_query)
    
    # Standart Yanıtlar
    responses = {
        "greeting": "Merhaba! Size nasıl yardımcı olabilirim? Bugün ne tarz bir kıyafet arıyorsunuz?",
        "thanks": "Rica ederim! Başka bir isteğiniz var mı? Size her zaman yardımcı olmaktan mutluluk duyarım.",
        "help": "Ben yapay zeka destekli bir moda asistanıyım. Bana 'Kırmızı elbise arıyorum', 'En ucuz ayakkabılar hangileri?' veya 'Kışlık bot önerir misin?' gibi sorular sorabilirsiniz.",
        "shipping": "📦 **Kargo Bilgisi:** Siparişleriniz 24 saat içinde kargoya verilir. Teslimat süresi genellikle 1-3 iş günüdür. 500 TL üzeri alışverişlerde kargo ücretsizdir.",
        "return": "🔄 **İade ve Değişim:** Satın aldığınız ürünleri 14 gün içinde ücretsiz iade edebilir veya değiştirebilirsiniz. Ürünün etiketi koparılmamış olmalıdır.",
        "payment": "💳 **Ödeme Seçenekleri:** Kredi kartına 12 taksit, kapıda ödeme ve havale/EFT seçeneklerimiz mevcuttur. Ödemeleriniz 256-bit SSL ile güvence altındadır.",
        "contact": "📞 **İletişim:** Bize 0850 123 45 67 numarasından veya destek@modadunyasi.com adresinden 7/24 ulaşabilirsiniz."
    }
    
    if intent in responses:
        return {"type": "text", "content": responses[intent]}, context

    # Özel Durum: Benzer Ürün Arama
    if user_query.startswith("similar_to:"):
        try:
            product_id = int(user_query.split(":")[1])
            similar_products = get_similar_products(product_id)
            if similar_products:
                return {
                    "type": "product_list",
                    "content": "İşte beğendiğiniz ürüne tarz olarak en çok benzeyen diğer seçenekler:",
                    "products": similar_products
                }, context
            else:
                return {"type": "text", "content": "Benzer bir ürün bulamadım."}, context
        except:
             return {"type": "text", "content": "Bir hata oluştu."}, context

    # Özel Durum: Beşiktaş Forması
    if "beşiktaş" in user_query.lower():
        besiktas_products = df[df['urun_adi'].str.contains('Beşiktaş', case=False, na=False)]
        if not besiktas_products.empty:
            recommendations = []
            for _, product in besiktas_products.iterrows():
                recommendations.append(format_product(product))
            return {
                "type": "product_list",
                "content": "İşte şanlı Beşiktaş forması:",
                "products": recommendations
            }, context

    if intent == "size_help":
        # Regex ile boy ve kilo çek
        # Boy: 175, 1.75, 1,75 gibi formatları yakala
        height_match = re.search(r'boy(?:um)?\s*[:=]?\s*(\d{1,3}(?:[.,]\d{1,2})?)', user_query, re.IGNORECASE)
        weight_match = re.search(r'kilo(?:m)?\s*[:=]?\s*(\d{2,3})', user_query, re.IGNORECASE)
        
        if height_match and weight_match:
            height_str = height_match.group(1).replace(',', '.')
            height = float(height_str)
            
            # Metre cinsinden girildiyse cm'ye çevir
            if height < 3.0:
                height = int(height * 100)
            else:
                height = int(height)
                
            weight = int(weight_match.group(1))
            
            # Basit Beden Hesaplama Mantığı
            size = "Standart"
            
            # BMI Hesabı (Opsiyonel ama daha doğru sonuç verir)
            # bmi = weight / ((height / 100) ** 2)
            
            # Basit Kilo Bazlı Tablo
            if weight < 50:
                size = "XS"
            elif 50 <= weight < 65:
                size = "S"
            elif 65 <= weight < 75:
                size = "M"
            elif 75 <= weight < 85:
                size = "L"
            elif 85 <= weight < 95:
                size = "XL"
            else:
                size = "XXL"
                
            # Boya göre küçük düzeltmeler
            if height > 190 and size in ["S", "M"]:
                size = "L (Boydan dolayı)"
            elif height < 160 and size in ["L", "XL"]:
                size = "M (Boydan dolayı)"
                
            return {
                "type": "text", 
                "content": f"Verdiğiniz bilgilere göre (Boy: {height}cm, Kilo: {weight}kg), sizin için önerdiğim beden: **{size}**.\n\nBu sadece bir öneridir, ürün kalıplarına göre değişiklik gösterebilir."
            }, context
        else:
            return {
                "type": "text",
                "content": "Beden önerisi yapabilmem için boy ve kilonuzu belirtmeniz gerekiyor. Lütfen 'Boyum 175, kilom 70' şeklinde yazın."
            }, context
        
    if intent == "surprise":
        random_products = df.sample(3)
        recommendations = []
        for _, product in random_products.iterrows():
            recommendations.append(format_product(product))
        return {
            "type": "product_list",
            "content": "Bugün şanslı gününüzdesiniz! İşte sizin için rastgele seçtiğim harika parçalar:",
            "products": recommendations
        }, context

    if intent == "combination":
        outfit, style, gender = create_outfit(user_query, df)
        
        style_names = {
            "summer": "yazlık",
            "winter": "kışlık",
            "sport": "sportif",
            "formal": "şık/resmi",
            "casual": "günlük"
        }
        
        style_desc = style_names.get(style, "günlük")
        
        if not outfit:
             return {"type": "text", "content": "Üzgünüm, şu an size uygun bir kombin oluşturamadım. Lütfen daha sonra tekrar deneyin."}, context
             
        return {
            "type": "product_list",
            "content": f"Sizin için harika bir {style_desc} kombin hazırladım! İşte parçalar:",
            "products": outfit
        }, context

    # Search Intent - Gelişmiş Arama
    new_entities = extract_entities(user_query)
    
    # TF-IDF Skoru
    query_vec = tfidf_vectorizer.transform([user_query])
    similarity_scores = cosine_similarity(query_vec, tfidf_matrix)
    scores = similarity_scores[0]

    # KONTROL: Eğer yeni sorgu anlamsızsa (entity yok ve skor düşük), context'i kullanma
    # Bu sayede "asdasd" gibi rastgele yazılarda önceki filtreler (örn: ayakkabı) uygulanmaz.
    is_gibberish = False
    if not any(new_entities.values()) and (len(scores) == 0 or max(scores) < 0.15):
        is_gibberish = True

    # Context Merging (Hafıza)
    # Eğer yeni sorguda bir kriter belirtilmemişse, eskini koru.
    # Eğer belirtilmişse, yenisini kullan.
    
    if is_gibberish:
        entities = {}
    else:
        entities = context.copy()
        
        if new_entities["category"]:
            entities["category"] = new_entities["category"]
        if new_entities["color"]:
            entities["color"] = new_entities["color"]
        if new_entities["gender"]:
            entities["gender"] = new_entities["gender"]
        if new_entities["sort"]:
            entities["sort"] = new_entities["sort"]
        
    # Eğer hiçbir kriter yoksa (ne yeni ne eski), entities boş kalır.
    
    scored_products = []
    for i, score in enumerate(scores):
        product = df.iloc[i]
        final_score = score
        
        # Filtreleme Kuralları
        
        # 1. Cinsiyet Filtresi
        if entities.get("gender"):
            if product.get('cinsiyet', 'Unisex') not in entities["gender"]:
                continue
                
        # 2. Renk Filtresi (Kesin eşleşme veya metin içinde geçme)
        if entities.get("color"):
            # Eğer ürünün rengi belirtilen renk değilse ve açıklamasında geçmiyorsa puanı düşür veya ele
            # Burada esnek davranıp puanı artırıyoruz
            if entities["color"] in product['renk'].lower():
                final_score += 0.5 # Renk tutuyorsa puanı artır
            elif entities["color"] not in product['search_text'].lower():
                continue # Renk hiç geçmiyorsa ele
                
        # 3. Kategori Filtresi
        if entities.get("category"):
            if entities["category"] in product['kategori'].lower() or entities["category"] in product['urun_adi'].lower():
                final_score += 0.5
            else:
                # Kullanıcı kesin bir kategori belirttiyse (örn: pantolon), diğer kategorileri ele.
                continue

        if final_score > 0.15:
            scored_products.append(format_product(product, final_score))
            
    # FALLBACK: Eğer metin araması sonucu çok az ürün geldiyse ve bir sıralama isteği varsa
    # (Örn: "ucuz kıyafet" dediğinde "kıyafet" kelimesi sadece 1 üründe geçiyorsa)
    if (len(scored_products) < 3) and entities.get("sort"):
        existing_ids = {p['id'] for p in scored_products}
        
        all_candidates = []
        for i in range(len(df)):
            product = df.iloc[i]
            if product['id'] in existing_ids:
                continue
                
            # Filtreleri uygula
            if entities.get("gender"):
                if product.get('cinsiyet', 'Unisex') not in entities["gender"]:
                    continue
            
            if entities.get("category"):
                 if entities["category"] not in product['kategori'].lower() and entities["category"] not in product['urun_adi'].lower():
                    continue
            
            if entities.get("color"):
                 if entities["color"] not in product['renk'].lower() and entities["color"] not in product['search_text'].lower():
                    continue

            all_candidates.append(format_product(product, 0.1))
            
        scored_products.extend(all_candidates)

    # Sıralama
    if entities.get("sort") == 'cheap':
        scored_products.sort(key=lambda x: x['fiyat'])
    elif entities.get("sort") == 'expensive':
        scored_products.sort(key=lambda x: x['fiyat'], reverse=True)
    else:
        scored_products.sort(key=lambda x: x['skor'], reverse=True)
        
    # "Öner" kelimesi geçiyorsa tek ürün göster, yoksa 3 tane
    if "öner" in user_query.lower():
        recommendations = scored_products[:1]
    else:
        recommendations = scored_products[:3]
            
    if not recommendations and ((entities.get("gender") and not new_entities.get("gender")) or (entities.get("color") and not new_entities.get("color"))):
        # Eğer sonuç bulunamadıysa ve cinsiyet/renk filtresi bağlamdan geliyorsa (yeni sorguda yoksa),
        # Bu filtreleri kaldırıp tekrar dene.
        
        if not new_entities.get("gender"):
            entities["gender"] = None
        if not new_entities.get("color"):
            entities["color"] = None
        
        scored_products = []
        for i, score in enumerate(scores):
            product = df.iloc[i]
            final_score = score
            
            # 1. Cinsiyet Filtresi
            if entities.get("gender"):
                if product.get('cinsiyet', 'Unisex') not in entities["gender"]:
                    continue

            # 2. Renk Filtresi
            if entities.get("color"):
                if entities["color"] in product['renk'].lower():
                    final_score += 0.5 
                elif entities["color"] not in product['search_text'].lower():
                    continue
                    
            # 3. Kategori Filtresi
            if entities.get("category"):
                if entities["category"] in product['kategori'].lower() or entities["category"] in product['urun_adi'].lower():
                    final_score += 0.5
                else:
                    continue

            if final_score > 0.15:
                scored_products.append(format_product(product, final_score))
        
        # Tekrar Sıralama
        if entities.get("sort") == 'cheap':
            scored_products.sort(key=lambda x: x['fiyat'])
        elif entities.get("sort") == 'expensive':
            scored_products.sort(key=lambda x: x['fiyat'], reverse=True)
        else:
            scored_products.sort(key=lambda x: x['skor'], reverse=True)
            
        if "öner" in user_query.lower():
            recommendations = scored_products[:1]
        else:
            recommendations = scored_products[:3]

    if not recommendations:
        return {"type": "text", "content": "Üzgünüm, aradığınız kriterlere tam uyan bir ürün bulamadım. Farklı kelimelerle tekrar deneyebilir misiniz? (Örn: 'Bana bir kombin öner')"}, entities

    added_complementary = False
    # Pantolon için tamamlayıcı ürün önerisi (Cross-sell) - İPTAL EDİLDİ (Kullanıcı isteği üzerine sadece aranan kategori dönecek)
    # if entities.get("category") and "pantolon" in entities["category"]:
    #     ...
    
    # Dinamik Cevap
    response_text = "İşte bulduğum en güzel seçenekler:"
    
    if added_complementary:
         response_text = f"Aradığınız pantolon modelleri ve onlarla harika gidecek kombin önerilerim:"
    elif entities.get("color"):
        response_text = f"İşte sizin için seçtiğim {entities['color']} renkli ürünler:"
    elif entities.get("category"):
        response_text = f"Aradığınız {entities['category']} modelleri burada:"
    elif entities.get("sort") == 'cheap':
        response_text = "Bütçe dostu en uygun fiyatlı ürünlerimiz:"
    elif entities.get("sort") == 'expensive':
        response_text = "Kaliteden ödün vermeyenler için en özel ve lüks seçeneklerimiz:"
    
    return {
        "type": "product_list",
        "content": response_text,
        "products": recommendations
    }, entities
