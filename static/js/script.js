document.addEventListener('DOMContentLoaded', () => {
    loadProducts();
    setupChatbot();
    updateCartCount();
});

// Ürünleri Yükle
async function loadProducts() {
    try {
        const response = await fetch('/api/products');
        let products = await response.json();

        // 1. Tekil Grid Kontrolü (Kadın/Erkek Sayfaları)
        const mainGrid = document.getElementById('productGrid');
        if (mainGrid) {
            const genderFilter = mainGrid.getAttribute('data-gender');
            if (genderFilter) {
                products = products.filter(p => p.cinsiyet === genderFilter || p.cinsiyet === 'Unisex');
            }
            mainGrid.innerHTML = products.map(createProductCardHtml).join('');
            return;
        }

        // 2. Kategori Gridleri Kontrolü (Ana Sayfa)
        const categoryMap = {
            'grid-elbise': ['Elbise'],
            'grid-pantolon': ['Pantolon', 'Şort'],
            'grid-dis-giyim': ['Ceket', 'Dış Giyim', 'Mont', 'Kaban', 'Hırka', 'Sweatshirt', 'Kazak'],
            'grid-ayakkabi': ['Ayakkabı'],
            'grid-aksesuar': ['Aksesuar', 'Çanta', 'Saat', 'Gözlük']
        };

        let hasAnyGrid = false;
        for (const [gridId, categories] of Object.entries(categoryMap)) {
            const grid = document.getElementById(gridId);
            if (grid) {
                hasAnyGrid = true;
                const filteredProducts = products.filter(p => categories.includes(p.kategori));
                if (filteredProducts.length > 0) {
                    grid.innerHTML = filteredProducts.map(createProductCardHtml).join('');
                } else {
                    // Eğer kategori boşsa başlığı ve gridi gizle
                    if(grid.parentElement.classList.contains('category-section')) {
                        grid.parentElement.style.display = 'none';
                    }
                }
            }
        }

    } catch (error) {
        console.error('Ürünler yüklenirken hata oluştu:', error);
    }
}

function createProductCardHtml(product) {
    return `
        <div class="product-card" onclick="window.location.href='/urun/${product.id}'">
            <img src="${product.resim}" alt="${product.urun_adi}" class="product-image">
            <div class="product-info">
                <div class="product-title">${product.urun_adi}</div>
                <div class="product-price">${product.fiyat} TL</div>
                <button class="add-to-cart-btn" onclick="addToCart(event, ${product.id}, '${product.urun_adi.replace(/'/g, "\\'")}', ${product.fiyat}, '${product.resim}', null)">Sepete Ekle</button>
            </div>
        </div>
    `;
}

// Chatbot İşlemleri
function setupChatbot() {
    const toggleBtn = document.getElementById('chatToggle');
    const chatWindow = document.getElementById('chatWindow');
    const closeBtn = document.getElementById('closeChat');
    const sendBtn = document.getElementById('sendMessage');
    const outfitBtn = document.getElementById('createOutfitBtn');
    const input = document.getElementById('chatInput');
    const messages = document.getElementById('chatMessages');

    // Örnek soruları ekle
    addSuggestedQuestions();

    // Kombin Butonu
    if (outfitBtn) {
        outfitBtn.addEventListener('click', () => {
            input.value = "Bana bir kombin öner";
            handleSend();
        });
    }

    // Pencereyi aç/kapa
    toggleBtn.addEventListener('click', () => {
        chatWindow.classList.toggle('active');
        if (chatWindow.classList.contains('active')) {
            input.focus();
            scrollToBottom();
        }
    });

    closeBtn.addEventListener('click', () => {
        chatWindow.classList.remove('active');
    });

    function scrollToBottom() {
        messages.scrollTop = messages.scrollHeight;
    }

    function addSuggestedQuestions() {
        const suggestions = ["Açık renk kıyafetler", "Resmi giyim", "Kargo süresi", "İade koşulları"];
        const container = document.createElement('div');
        container.style.padding = "10px 15px";
        container.style.display = "flex";
        container.style.gap = "8px";
        container.style.flexWrap = "wrap";
        
        suggestions.forEach(text => {
            const chip = document.createElement('button');
            chip.textContent = text;
            chip.style.background = "#fff";
            chip.style.border = "1px solid #ddd";
            chip.style.borderRadius = "15px";
            chip.style.padding = "5px 10px";
            chip.style.fontSize = "0.8rem";
            chip.style.cursor = "pointer";
            chip.style.color = "#555";
            chip.style.transition = "all 0.2s";
            
            chip.onmouseover = () => { chip.style.background = "#f0f0f0"; chip.style.borderColor = "#ccc"; };
            chip.onmouseout = () => { chip.style.background = "#fff"; chip.style.borderColor = "#ddd"; };
            
            chip.onclick = () => {
                input.value = text;
                handleSend();
            };
            container.appendChild(chip);
        });
        
        // Mesajların en üstüne değil, botun ilk mesajından sonra ekleyelim
        // Ancak basitlik için input alanının hemen üstüne ekleyebiliriz veya mesaj alanının sonuna.
        // En temiz yöntem: Mesaj alanının içine, botun ilk mesajından sonra eklemek.
        messages.appendChild(container);
    }

    // Mesaj Gönderme
    function handleSend() {
        const text = input.value.trim();
        if (!text) return;

        // Kullanıcı mesajını ekle
        addMessage(text, 'user-message');
        input.value = '';

        // Typing indicator göster
        showTyping();
        scrollToBottom();

        // API isteği
        fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        })
        .then(res => res.json())
        .then(data => {
            // Typing indicator gizle
            removeTyping();

            // Botun metin cevabını ekle
            addMessage(data.response, 'bot-message');
            
            if (data.products && data.products.length > 0) {
                const productsHtml = data.products.map((p, index) => `
                    <div class="chat-product-card" style="animation-delay: ${index * 0.2}s">
                        <div class="chat-card-image-container">
                            <img src="${p.resim}" class="chat-product-img" alt="${p.urun_adi}">
                        </div>
                        <div class="chat-product-details">
                            <div class="chat-product-title">${p.urun_adi}</div>
                            ${p.fomo_text ? `<div class="chat-fomo-text">${p.fomo_text}</div>` : ''}
                            <div class="chat-product-price">${p.fiyat} TL</div>
                            <div class="chat-btn-group">
                                <button onclick="addToCart(event, ${p.id}, '${p.urun_adi.replace(/'/g, "\\'")}', ${p.fiyat}, '${p.resim}', null)" class="chat-add-btn">
                                    <i class="fas fa-shopping-bag"></i> Ekle
                                </button>
                                <button onclick="findSimilar(${p.id})" class="chat-similar-btn" title="Benzerlerini Göster">
                                    <i class="fas fa-search-plus"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                `).join('');
                
                const productBubble = document.createElement('div');
                productBubble.className = 'message bot-message';
                productBubble.style.background = "transparent";
                productBubble.style.padding = "0";
                productBubble.style.boxShadow = "none";
                productBubble.innerHTML = productsHtml;
                messages.appendChild(productBubble);
            }
            scrollToBottom();
        })
        .catch(err => {
            console.error(err);
            removeTyping();
            addMessage("Bir hata oluştu.", 'bot-message');
            scrollToBottom();
        });
    }

    sendBtn.addEventListener('click', handleSend);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSend();
    });

    function addMessage(text, className) {
        const div = document.createElement('div');
        div.className = `message ${className}`;
        div.textContent = text;
        messages.appendChild(div);
        scrollToBottom();
    }

    function showTyping() {
        const div = document.createElement('div');
        div.className = 'typing-indicator';
        div.id = 'typingIndicator';
        div.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        messages.appendChild(div);
        scrollToBottom();
    }

    function removeTyping() {
        const typing = document.getElementById('typingIndicator');
        if (typing) typing.remove();
    }
}

// Sepet ��lemleri
function addToCart(event, id, name, price, image, size = null) {
    if (event) {
        event.stopPropagation(); // Kart t�klamas�n� engelle
    }
    
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    const existingItem = cart.find(item => item.id === id && item.size === size);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            id: id,
            name: name,
            price: price,
            image: image,
            size: size,
            quantity: 1
        });
    }
    
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    
    // Basit bir bildirim g�ster
    const btn = event ? event.target : document.querySelector('.add-to-cart-btn');
    const originalText = btn.innerText;
    btn.innerText = 'Eklendi!';
    btn.style.backgroundColor = '#27ae60';
    
    setTimeout(() => {
        btn.innerText = originalText;
        btn.style.backgroundColor = '';
    }, 1000);
}

function findSimilar(id) {
    const input = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendMessage');
    
    // Kullanıcıya bilgi ver
    const messages = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = 'message user-message';
    div.textContent = "Bu ürüne benzer modelleri göster";
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;

    // Typing indicator
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>`;
    messages.appendChild(typingDiv);
    messages.scrollTop = messages.scrollHeight;

    // API isteği (Gizli komut gönderiyoruz)
    fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: `similar_to:${id}` })
    })
    .then(res => res.json())
    .then(data => {
        const typing = document.getElementById('typingIndicator');
        if (typing) typing.remove();

        // Bot cevabı
        const botDiv = document.createElement('div');
        botDiv.className = 'message bot-message';
        botDiv.textContent = data.response;
        messages.appendChild(botDiv);

        if (data.products && data.products.length > 0) {
            const productsHtml = data.products.map((p, index) => `
                <div class="chat-product-card" style="animation-delay: ${index * 0.2}s">
                    <div class="chat-card-image-container">
                        <img src="${p.resim}" class="chat-product-img" alt="${p.urun_adi}">
                    </div>
                    <div class="chat-product-details">
                        <div class="chat-product-title">${p.urun_adi}</div>
                        ${p.fomo_text ? `<div class="chat-fomo-text">${p.fomo_text}</div>` : ''}
                        <div class="chat-product-price">${p.fiyat} TL</div>
                        <div class="chat-btn-group">
                            <button onclick="addToCart(event, ${p.id}, '${p.urun_adi.replace(/'/g, "\\'")}', ${p.fiyat}, '${p.resim}', null)" class="chat-add-btn">
                                <i class="fas fa-shopping-bag"></i> Ekle
                            </button>
                            <button onclick="findSimilar(${p.id})" class="chat-similar-btn" title="Benzerlerini Göster">
                                <i class="fas fa-search-plus"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
            
            const productBubble = document.createElement('div');
            productBubble.className = 'message bot-message';
            productBubble.style.background = "transparent";
            productBubble.style.padding = "0";
            productBubble.style.boxShadow = "none";
            productBubble.innerHTML = productsHtml;
            messages.appendChild(productBubble);
        }
        messages.scrollTop = messages.scrollHeight;
    })
    .catch(err => console.error(err));
}

function updateCartCount() {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    const countElement = document.querySelector('.cart-count');
    if (countElement) {
        countElement.innerText = totalItems;
        countElement.style.display = totalItems > 0 ? 'flex' : 'none';
    }
}

