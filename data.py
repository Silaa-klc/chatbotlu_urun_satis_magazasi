import pandas as pd

def get_data():
    """
    Örnek ürün verilerini içeren Pandas DataFrame oluşturur ve döndürür.
    """
    data = [
        {
            "id": 1,
            "urun_adi": "Kırmızı Yazlık Çiçekli Elbise",
            "kategori": "Elbise",
            "renk": "Kırmızı",
            "fiyat": 450.00,
            "detayli_aciklama": "Yaz ayları için ideal, terletmeyen, pamuklu kumaştan üretilmiş, kırmızı renkli, üzerinde beyaz papatya desenleri olan askılı mini elbise. Plaj ve günlük kullanım için uygundur."
        },
        {
            "id": 2,
            "urun_adi": "Slim Fit Mavi Kot Pantolon",
            "kategori": "Pantolon",
            "renk": "Mavi",
            "fiyat": 350.00,
            "detayli_aciklama": "Günlük kullanım için rahat, esnek yapılı, dar kesim (slim fit) mavi jean pantolon. Dört mevsim giyilebilir, klasik beş cepli tasarım."
        },
        {
            "id": 3,
            "urun_adi": "Siyah Deri Motorcu Ceketi",
            "kategori": "Ceket",
            "renk": "Siyah",
            "fiyat": 1200.00,
            "detayli_aciklama": "Hakiki deriden üretilmiş, rüzgar geçirmeyen, fermuarlı ve zımba detaylı siyah motorcu ceketi. Sonbahar ve kış ayları için şık ve sıcak tutan bir seçenek."
        },
        {
            "id": 4,
            "urun_adi": "Beyaz Koşu ve Yürüyüş Ayakkabısı",
            "kategori": "Ayakkabı",
            "renk": "Beyaz",
            "fiyat": 850.00,
            "detayli_aciklama": "Ortopedik tabanlı, nefes alan file yüzeyli, hafif ve rahat beyaz spor ayakkabı. Koşu, yürüyüş ve antrenmanlar için yüksek performans sağlar."
        },
        {
            "id": 5,
            "urun_adi": "Yeşil İpek Şal",
            "kategori": "Aksesuar",
            "renk": "Yeşil",
            "fiyat": 200.00,
            "detayli_aciklama": "%100 saf ipekten üretilmiş, yumuşak dokulu, parlak görünümlü zümrüt yeşili şal. Özel davetlerde abiye üzerine veya günlük şıklık için kullanılabilir."
        },
        {
            "id": 6,
            "urun_adi": "Gri Kumaş Ofis Pantolonu",
            "kategori": "Pantolon",
            "renk": "Gri",
            "fiyat": 400.00,
            "detayli_aciklama": "İş hayatı ve ofis şıklığı için tasarlanmış, ütü gerektirmeyen kumaştan, klasik kesim gri pantolon. Gömlek ve ceketlerle mükemmel uyum sağlar."
        },
        {
            "id": 7,
            "urun_adi": "Sarı Kapüşonlu Yağmurluk",
            "kategori": "Dış Giyim",
            "renk": "Sarı",
            "fiyat": 550.00,
            "detayli_aciklama": "Su geçirmez kumaştan, kapüşonlu, canlı sarı renkte yağmurluk. Bahar yağmurlarında ıslanmanızı önler, içi astarlıdır ve sıcak tutar."
        },
        {
            "id": 8,
            "urun_adi": "Lacivert Slim Fit Takım Elbise",
            "kategori": "Takım Elbise",
            "renk": "Lacivert",
            "fiyat": 2500.00,
            "detayli_aciklama": "Düğün, mezuniyet ve iş toplantıları için ideal, modern kesim, yün karışımlı lacivert takım elbise. Ceket ve pantolon dahildir."
        },
        {
            "id": 9,
            "urun_adi": "Pembe V Yaka Tişört",
            "kategori": "Tişört",
            "renk": "Pembe",
            "fiyat": 150.00,
            "detayli_aciklama": "Yazın vazgeçilmezi, %100 organik pamuk, V yaka, kısa kollu, canlı pembe renkli basic tişört. Kot pantolon veya şortla kombinlenebilir."
        },
        {
            "id": 10,
            "urun_adi": "Kahverengi Kışlık Deri Bot",
            "kategori": "Ayakkabı",
            "renk": "Kahverengi",
            "fiyat": 1100.00,
            "detayli_aciklama": "Zorlu kış şartlarına uygun, su geçirmez, içi yünlü, kaymaz tabanlı kahverengi deri bot. Karlı ve yağmurlu havalarda ayakları sıcak ve kuru tutar."
        }
    ]
    
    return pd.DataFrame(data)
