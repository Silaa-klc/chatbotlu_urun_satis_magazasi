
import json
import csv
import random

def load_products():
    with open('urunler.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_dataset():
    products = load_products()
    dataset = []

    # Şablonlar - Daha fazla varyasyon
    templates = {
        "greeting": [
            ("Merhaba", "Merhaba! ModaDünyası'na hoş geldiniz 🎉 Size nasıl yardımcı olabilirim?"),
            ("Selam", "Selam! Bugün ne tarz bir kıyafet bakıyorsunuz?"),
            ("Hey", "Merhaba! Size yardımcı olmak için buradayım."),
            ("Günaydın", "Günaydın! Güne şık başlamak için doğru yerdesiniz."),
            ("İyi akşamlar", "İyi akşamlar! Size nasıl yardımcı olabilirim?"),
            ("Nasılsın", "Ben bir yapay zekayım ama harika hissediyorum! Siz nasılsınız?"),
            ("Kimsin", "Ben ModaDünyası'nın akıllı asistanıyım. Size en uygun ürünleri bulmak için buradayım."),
            ("Selamın aleyküm", "Aleyküm selam! Hoş geldiniz."),
            ("Mrb", "Merhaba! Size nasıl destek olabilirim?"),
            ("Slm", "Selamlar! Ne arıyorsunuz bugün?"),
        ],
        "help": [
            ("Ne yapabilirsin", "Ürün arayabilirim, kombin önerebilirim, kargo ve iade sorularınızı yanıtlayabilirim."),
            ("Yardım et", "Tabii! Ne konuda yardıma ihtiyacınız var? Ürün mü arıyorsunuz?"),
            ("Nasıl çalışıyorsun", "Bana 'Kırmızı elbise göster' veya 'Yazlık kombin öner' gibi sorular sorabilirsiniz."),
            ("Bana yardım et", "Elbette, size moda konusunda asistanlık yapabilirim. Neye ihtiyacınız var?"),
            ("Özelliklerin neler", "Fiyat sorabilir, ürün aratabilir, kombin isteyebilir veya mağaza politikalarını öğrenebilirsiniz."),
        ],
        "general_info": [
            ("Kargo ne kadar", "📦 500 TL üzeri alışverişlerde kargo bedava! Altındaki siparişler için 39.90 TL."),
            ("Kargo süresi", "📦 Siparişleriniz 24 saat içinde kargoya verilir. Teslimat 1-3 iş günü sürer."),
            ("İade var mı", "🔄 Evet, 14 gün içinde ücretsiz iade hakkınız var."),
            ("Değişim yapıyor musunuz", "🔄 Evet, beden veya renk değişimi yapabilirsiniz."),
            ("Ödeme yöntemleri", "💳 Kredi kartı, kapıda ödeme ve havale ile ödeme yapabilirsiniz."),
            ("Mağaza nerede", "📍 Mağazamız İstanbul Kadıköy'de. Bekleriz!"),
            ("İletişim", "📞 Bize 0850 123 45 67 numarasından ulaşabilirsiniz."),
            ("Kapıda ödeme var mı", "💳 Evet, kapıda ödeme seçeneğimiz mevcut (+15 TL hizmet bedeli)."),
            ("Hangi kargo", "📦 Aras Kargo ve Yurtiçi Kargo ile çalışıyoruz."),
        ]
    }

    # 1. Statik Intentler
    for intent, pairs in templates.items():
        for q, a in pairs:
            dataset.append([q, a, intent])

    # 2. Dinamik Ürün Soruları
    for p in products:
        name = p['urun_adi']
        cat = p['kategori']
        color = p['renk']
        price = p['fiyat']
        gender = p['cinsiyet']
        desc = p['detayli_aciklama']
        stock = p.get('stok', 0)
        
        # Stok Durumu Metni
        stock_msg = "Stoklarımızda mevcut." if stock > 0 else "Maalesef stoklarımız tükenmiş."
        if 0 < stock < 5:
            stock_msg = f"Acele edin, son {stock} ürün!"

        # Ürün Adı Sorguları (Varyasyonlu)
        queries = [
            name,
            f"{name} fiyatı",
            f"{name} ne kadar",
            f"{name} özellikleri",
            f"{name} göster",
            f"{name} hakkında bilgi",
            f"{name} stokta var mı",
            f"{name} kaç para",
            f"{name} satın al",
            f"{name} detayları"
        ]
        
        answer = f"🏷️ **{name}**\n💰 Fiyat: {price} TL\n🎨 Renk: {color}\n📦 {stock_msg}\n📝 {desc}"
        
        for q in queries:
            dataset.append([q, answer, "search"])

        # Özellik Sorguları (Renk + Kategori)
        # Bu sorgulara o özellikteki spesifik bir ürünü "örnek" olarak veriyoruz.
        cat_queries = [
            f"{color} {cat}",
            f"{color} {cat} var mı",
            f"{color} {cat} modelleri",
            f"{color} {cat} fiyatları",
            f"{gender} {cat}",
            f"{cat} {color}",
            f"{color} renk {cat}",
            f"{gender} için {cat}"
        ]
        
        cat_answer = f"Evet, harika bir seçeneğimiz var: **{name}**. Fiyatı {price} TL. İncelemek ister misiniz?"
        
        for q in cat_queries:
            dataset.append([q, cat_answer, "search"])


    # 3. Kategori Bazlı Genel Sorular (Süperlatifler & Genellemeler)
    categories = set(p['kategori'] for p in products)
    for cat in categories:
        cat_products = [p for p in products if p['kategori'] == cat]
        cheapest = min(cat_products, key=lambda x: x['fiyat'])
        most_expensive = max(cat_products, key=lambda x: x['fiyat'])
        
        # En ucuz
        q_cheap = [
            f"En ucuz {cat}", 
            f"Uygun fiyatlı {cat}", 
            f"İndirimli {cat}",
            f"En düşük fiyatlı {cat}",
            f"Bütçe dostu {cat}"
        ]
        a_cheap = f"💰 Fiyat/Performans şampiyonu: **{cheapest['urun_adi']}** sadece {cheapest['fiyat']} TL!"
        for q in q_cheap:
            dataset.append([q, a_cheap, "search"])
            
        # En pahalı
        q_exp = [
            f"En pahalı {cat}", 
            f"Lüks {cat}", 
            f"Kaliteli {cat}",
            f"Premium {cat}",
            f"En iyi {cat}"
        ]
        a_exp = f"💎 Özel koleksiyonumuzdan: **{most_expensive['urun_adi']}** - {most_expensive['fiyat']} TL. Kalitesiyle fark yaratır."
        for q in q_exp:
            dataset.append([q, a_exp, "search"])
            
        # Genel kategori sorusu
        q_gen = [
            f"{cat} modelleri", 
            f"{cat} çeşitleri", 
            f"{cat} göster", 
            f"Bana {cat} öner",
            f"{cat} bakıyorum"
        ]
        random_prod = random.choice(cat_products)
        a_gen = f"🧥 {cat} kategorisinde çok şık parçalarımız var. Örneğin **{random_prod['urun_adi']}** modelini görmelisiniz ({random_prod['fiyat']} TL)."
        for q in q_gen:
             dataset.append([q, a_gen, "search"])

    # 4. Kombin Soruları (Genişletilmiş)
    styles = {
        "Düğün": {
            "keywords": ["Düğün", "Nişan", "Kına", "Davet", "Mezuniyet", "Abiye"],
            "cats": ["Takım Elbise", "Elbise", "Stiletto", "Abiye Çanta", "Kravat", "Ceket"]
        },
        "Spor": {
            "keywords": ["Spor", "Koşu", "Yürüyüş", "Gym", "Antrenman", "Rahat"],
            "cats": ["Spor Giyim", "Şort", "Tişört", "Spor Ayakkabı", "Tayt", "Sweatshirt", "Eşofman"]
        },
        "Yaz": {
            "keywords": ["Yaz", "Tatil", "Plaj", "Deniz", "Sıcak", "Yazlık"],
            "cats": ["Şort", "Tişört", "Sandalet", "Güneş Gözlüğü", "Elbise", "Plaj Giyim", "Gömlek"]
        },
        "Kış": {
            "keywords": ["Kış", "Soğuk", "Kar", "Kayak", "Kışlık"],
            "cats": ["Mont", "Kaban", "Bot", "Kazak", "Atkı", "Bere", "Eldiven", "Hırka"]
        },
        "Ofis": {
            "keywords": ["Ofis", "İş", "Toplantı", "Kurumsal", "Resmi"],
            "cats": ["Gömlek", "Pantolon", "Ceket", "Takım Elbise", "Bluz", "Kemer"]
        }
    }
    
    for style, data in styles.items():
        base_keywords = data["keywords"]
        target_cats = data["cats"]
        
        # O tarzda rastgele ürünler seç (En fazla 3)
        possible_items = [p['urun_adi'] for p in products if p['kategori'] in target_cats]
        
        if len(possible_items) >= 2:
            suggestion = ", ".join(random.sample(possible_items, min(3, len(possible_items))))
            
            answer = f"👗 **{style} Kombini** önerim:\n{suggestion} parçalarını bir arada kullanarak harika görünebilirsiniz!"
            
            for kw in base_keywords:
                dataset.append([f"{kw} kombini", answer, "combination"])
                dataset.append([f"{kw} için ne giysem", answer, "combination"])
                dataset.append([f"{kw} kıyafetleri", answer, "combination"])
                dataset.append([f"{kw} önerisi", answer, "combination"])

    # CSV Yazma
    with open('dataset.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['soru', 'cevap', 'intent'])
        writer.writerows(dataset)
    
    print(f"Maksimum kapsamlı dataset oluşturuldu: {len(dataset)} satır.")

if __name__ == "__main__":
    generate_dataset()
