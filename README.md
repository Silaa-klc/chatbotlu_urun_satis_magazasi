# 🛍️ Moda Dünyası - AI Destekli E-Ticaret Asistanı

Bu proje, modern bir e-ticaret deneyimini yapay zeka destekli bir sanal asistan ile birleştiren kapsamlı bir web uygulamasıdır. Kullanıcılar ürünleri gezebilir, sepete ekleyebilir ve doğal dil işleme (NLP) yeteneklerine sahip chatbot ile etkileşime geçerek kişiselleştirilmiş öneriler alabilirler.

## 🚀 Öne Çıkan Özellikler

### 🤖 Akıllı Chatbot Asistanı
Python ve Scikit-learn kullanılarak geliştirilen chatbot, kullanıcıların doğal dilde yazdığı mesajları anlar ve buna uygun cevaplar verir.
- **Niyet Analizi:** Selamlaşma, kargo sorgulama, iade koşulları gibi genel soruları yanıtlar.
- **Varlık Çıkarımı (Entity Extraction):** Mesaj içindeki renk (kırmızı, mavi), kategori (elbise, pantolon), cinsiyet ve fiyat tercihlerini (ucuz, pahalı) algılar.

### 👗 Akıllı Kombin Oluşturucu
"Ne giysem?" derdine son! Chatbot, mevsime ve tarza göre dinamik kombinler oluşturur.
- **Stiller:** Yazlık, Kışlık, Spor, Resmi (Formal), Günlük (Casual).
- **Algoritma:** Seçilen tarza uygun alt giyim, üst giyim, ayakkabı ve aksesuarları bir araya getirerek sunar.

### 📏 Beden Danışmanı
Kullanıcının fiziksel özelliklerine göre beden önerisi yapar.
- **Örnek:** "Boyum 180 kilom 85" yazıldığında, sistem BMI ve kilo tablolarını baz alarak tahmini bir beden (M, L, XL vb.) önerir.

### 🔍 Benzer Ürün Önerisi (Recommendation Engine)
Beğenilen bir ürünün detay sayfasında veya sohbet penceresinde, o ürüne içerik ve tarz olarak en yakın diğer ürünleri listeler.
- **Teknoloji:** TF-IDF Vektörleştirme ve Cosine Similarity (Kosinüs Benzerliği) kullanır.

### 🛒 E-Ticaret Özellikleri
- **Dinamik Ürün Listeleme:** Kategoriye göre filtreleme.
- **Sepet Yönetimi:** Ürünleri sepete ekleme ve adet güncelleme.
- **Stok Uyarıları (FOMO):** Stok azaldığında "Tükenmek üzere!" gibi uyarılarla kullanıcıyı bilgilendirir.

## 🛠️ Teknolojiler

- **Backend:** Python
- **Veri İşleme & AI:** Pandas, Scikit-learn (TfidfVectorizer, Cosine Similarity)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Veri Kaynağı:** JSON (NoSQL yapısında ürün verisi)

## 📂 Proje Yapısı

- `recommender.py`: Öneri motorunun, niyet analizinin ve kombin mantığının bulunduğu ana Python dosyası.
- `urunler.json`: Ürünlerin detaylı bilgilerini (fiyat, stok, açıklama, resim vb.) içeren veri seti.
- `static/js/script.js`: Frontend tarafındaki dinamik işlemler, API iletişimi ve chatbot arayüz kontrolü.
- `readme.md`: Proje dokümantasyonu.

## 💡 Nasıl Kullanılır?

### Kurulum

1. Projeyi bilgisayarınıza indirin.
2. Gerekli Python kütüphanelerini yükleyin:
   ```bash
   pip install pandas scikit-learn
   ```
3. Uygulamayı başlatın (Flask sunucusu üzerinden):
   ```bash
   python app.py
   ```

### Örnek Chatbot Sorguları

- **Ürün Arama:** "Kırmızı yazlık elbise arıyorum", "Ucuz erkek ayakkabısı göster"
- **Kombin İsteği:** "Hafta sonu için spor bir kombin yap", "Düğün için şık ne giyebilirim?"
- **Beden Danışma:** "Boyum 1.65 kilom 55, hangi beden almalıyım?"
- **Bilgi Alma:** "Kargo kaç günde gelir?", "İade var mı?"
