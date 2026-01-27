//===========================================================================================================================
// DigiRella Documentation Handler
// Manages documentation modal display and content rendering
//===========================================================================================================================

//----------------------------------------------------------------------------------------------------------------------------
// Documentation content in Azerbaijani (embedded for offline access)
//----------------------------------------------------------------------------------------------------------------------------
const DOCUMENTATION_AZ = `
# DigiRella - Kənd Təsərrüfatı Qərar Dəstək Sistemi

## 📖 İstifadəçi Təlimatı

### Sistemin Məqsədi

DigiRella süni intellekt əsaslı kənd təsərrüfatı qərar dəstək sistemidir. Bu sistem real vaxt sensor məlumatları və ətraf mühit şəraitinə əsasən ağıllı təsərrüfat tövsiyələri təqdim edir.

### Əsas İmkanlar

- ✅ **Müxtəlif Təsərrüfat Tipləri**: Buğda, heyvandarlıq, bağçılıq, istixana və qarışıq təsərrüfat
- ✅ **Ağıllı Tövsiyələr**: Hava, torpaq, bitki mərhələsi və resurs mövcudluğuna əsaslı qərarlar
- ✅ **Konflikt Həlli**: Ziddiyyətli fəaliyyətlərin avtomatik prioritetləşdirilməsi
- ✅ **Çoxdilli Dəstək**: Azərbaycan dilində tövsiyələr
- ✅ **İnteraktiv İnterfeys**: Ssenari seçimi və chatbot

---

## 💻 İstifadə Təlimatı

### Addım 1: API-yə Qoşulma

1. **API Baza Ünvanı** sahəsinə backend serverinizin ünvanını daxil edin
   - Standart: \`http://127.0.0.1:8000\`
2. **"Bağlan"** düyməsini klikləyin
3. Sistem təsərrüfat tiplərini avtomatik yükləyəcək

### Addım 2: Təsərrüfat Tipi Seçimi

Mövcud təsərrüfat tiplərindən birini seçin:

- **🌾 Buğda (Wheat)**: Taxıl bitkisi becərməsi
- **🐄 Heyvandarlıq (Livestock)**: Süd inəkləri idarəetməsi
- **🍎 Bağçılıq (Orchard)**: Meyvə ağacları becərməsi
- **🏠 İstixana (Greenhouse)**: Qorunan bitki istehsalı
- **🌱 Qarışıq (Mixed)**: İnteqrasiya olunmuş bitki və heyvan təsərrüfatı

### Addım 3: Ssenari Seçimi

1. Təsərrüfat tipi seçildikdən sonra mövcud ssenarilər yüklənəcək
2. Ssenarini klikləyərək seçin
3. Hər ssenari müəyyən hava şəraiti, torpaq vəziyyəti və resurs mövcudluğunu təmsil edir

### Addım 4: Tövsiyələri Oxuma

Ssenari seçildikdən sonra sistem iki siyahı göstərəcək:

#### ✅ Edilməli (Tövsiyələr)
- Bu gün görülməli fəaliyyətlər
- Hər fəaliyyət üçün prioritet səviyyəsi: **yüksək**, **orta**, **aşağı**
- Hər tövsiyənin ətraflı səbəbləri

#### ❌ Edilməməli (Məhdudiyyətlər)
- Hazırki şəraitdə görülməməli fəaliyyətlər
- Məhdudiyyətlərin səbəbləri

### Addım 5: Chatbot ilə Söhbət

Ssenari haqqında sual verin:

**Nümunə suallar:**
- "Bu gün nə etməliyəm?"
- "Vəziyyət necədir?"
- "Niyə suvarma tövsiyə olunur?"
- "Hava şəraiti necədir?"

**Qeyd:** Chatbot hər sorğuda avtomatik olaraq ssenari 1-i seçir.

---

## 📊 Tövsiyə Nümunələri

### Buğda Təsərrüfatı

**Ssenari:** Quraqlıq və isti hava şəraiti

**Edilməli:**
- **Suvarma** (yüksək prioritet)
  - Torpaq rütubəti aşağıdır (16%)
  - Quru şərait var (son 24 saat yağış=0 mm)
  - Növbəti 48 saatda yağış gözlənilmir

**Edilməməli:**
- **Gübrələmə**
  - Torpaq çox quru, gübrə həll olmayacaq
  - Gübrə itki riski yüksəkdir

### Heyvandarlıq Təsərrüfatı

**Ssenari:** İsti stress riski

**Edilməli:**
- **Su çıxışını artırın** (yüksək prioritet)
  - İsti stress riski (temp=32°C)
  - Susuzlaşma təhlükəsi
- **Kölgə təmin edin**
  - Heyvanları sərin saxlayın

**Edilməməli:**
- **Heyvanları hərəkət etdirməyin**
  - İsti vaxtda hərəkət stress yaradır

---

## 🎯 Qərar Məntiqi

### Sistem Necə İşləyir?

1. **Məlumat Toplama**: Sensor və müşahidə məlumatları
2. **Təhlil**: Hava, torpaq, bitki mərhələsi analizi
3. **Qaydaların Tətbiqi**: Təsərrüfat tipinə xas qərar qaydaları
4. **Konflikt Həlli**: Ziddiyyətli tövsiyələrin həlli
5. **Nəticənin Formalaşdırılması**: Azərbaycan dilində tövsiyələr

### Prioritet Sistemi

- **Yüksək**: Təcili fəaliyyətlər, bitki/heyvan sağlamlığı riskləri
- **Orta**: Vaxtında görülməli planlı fəaliyyətlər
- **Aşağı**: İxtiyari, məsləhət xarakterli tövsiyələr

---

## 🔍 Tez-Tez Verilən Suallar

### S: Niyə bəzi fəaliyyətlər həm "edilməli", həm də "edilməməli" siyahılarında görünmür?

C: Sistem konflikt həlli mexanizmi ilə ziddiyyətli tövsiyələri avtomatik həll edir. "Edilməməli" siyahısındakı fəaliyyətlər "edilməli" siyahısından avtomatik silinir.

### S: Prioritetlər necə müəyyən edilir?

C: Prioritetlər aşağıdakı amillərə əsasən verilir:
- Bitki/heyvan sağlamlığı riskləri
- Hava şəraiti təcililiyi
- Resurs mövcudluğu
- Böyümə mərhələsinin kritikliyi

### S: Chatbot hansı dildə cavab verir?

C: Chatbot hazırda yalnız Azərbaycan dilində cavab verir. Sistem çoxdilli dəstək üçün hazırlanıb və gələcəkdə başqa dillər əlavə edilə bilər.

### S: Öz ssenarilərimi necə əlavə edə bilərəm?

C: Yeni ssenari əlavə etmək üçün:
1. \`assets/farms/{farm_type}/synthetic_scenarios/\` qovluğuna keçin
2. \`scenario_X.json\` formatında yeni fayl yaradın
3. Ssenari strukturunu digər fayllardan nümunə götürərək doldurun
4. Serveri yenidən başladın

---

## 🛠️ Problemlərin Həlli

### Problem: Backend başlamır

**Həll:**
- Python versiyasını yoxlayın (3.13 və ya daha yeni olmalıdır)
- Asılılıqları quraşdırın: \`pip install -r backend/requirements.txt\`
- Detallı log ilə başladın: \`uvicorn app:app --reload --log-level debug\`

### Problem: Frontend API-yə qoşula bilmir

**Həll:**
1. Backend-in işlədiyini yoxlayın: \`http://127.0.0.1:8000/health\`
2. CORS parametrlərini yoxlayın
3. Brauzer konsolunda xəta mesajlarına baxın
4. Firewall və ya antivirus proqramlarını yoxlayın

### Problem: Tövsiyələr göstərilmir

**Həll:**
1. Ssenari düzgün seçildiyini təsdiq edin
2. Backend loglarına baxın
3. Ssenari JSON faylının düzgün formatda olduğunu yoxlayın

---

## 🌟 Tövsiyələr

### İstifadə üçün ən yaxşı təcrübələr:

1. **Gündəlik Yoxlama**: Hər gün səhər tövsiyələrə baxın
2. **Hava Proqnozu**: 48 saatlıq hava proqnozunu nəzərə alın
3. **Prioritetlərə Diqqət**: Yüksək prioritetli tövsiyələri ilk növbədə yerinə yetirin
4. **Resurs Planlaması**: Məhdudiyyətlərə əsasən resurslarınızı planlaşdırın
5. **Qeydlər**: Fəaliyyətlərin nəticələrini qeyd edin və müqayisə edin

### Təhlükəsizlik Məsləhətləri:

- ⚠️ Həmişə yerli aqronom məsləhəti ilə tövsiyələri təsdiqləyin
- ⚠️ Həddindən artıq gübrə və kimyəvi maddə istifadəsindən çəkinin
- ⚠️ Hava şəraiti dəyişikliklərini real vaxtda izləyin
- ⚠️ Heyvan sağlamlığı problemləri zamanı dərhal veterinar çağırın

---

**DigiRella ilə məhsuldarlığınızı artırın! 🌱**

*Versiya: 1.0.0*
`;

//----------------------------------------------------------------------------------------------------------------------------
// Simple markdown-like parser for documentation
//----------------------------------------------------------------------------------------------------------------------------
function parseMarkdownToHTML(markdown) {
  let html = markdown;

  // Headers
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

  // Bold
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  // Code blocks
  html = html.replace(/`(.+?)`/g, '<code>$1</code>');

  // Lists
  html = html.replace(/^\- (.+$)/gim, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

  // Horizontal rule
  html = html.replace(/^---$/gim, '<hr/>');

  // Line breaks
  html = html.replace(/\n\n/g, '</p><p>');
  html = html.replace(/\n/g, '<br/>');

  // Wrap in paragraphs
  html = '<p>' + html + '</p>';

  // Clean up multiple paragraph tags
  html = html.replace(/<p><\/p>/g, '');
  html = html.replace(/<p><h/g, '<h');
  html = html.replace(/<\/h([1-6])><\/p>/g, '</h$1>');
  html = html.replace(/<p><hr\/><\/p>/g, '<hr/>');
  html = html.replace(/<p><ul>/g, '<ul>');
  html = html.replace(/<\/ul><\/p>/g, '</ul>');

  return html;
}

//----------------------------------------------------------------------------------------------------------------------------
// Show documentation modal
//----------------------------------------------------------------------------------------------------------------------------
function showDocumentation() {
  const modal = document.getElementById('docsModal');
  const content = document.getElementById('docsContent');

  // Parse markdown to HTML
  content.innerHTML = parseMarkdownToHTML(DOCUMENTATION_AZ);

  // Show modal
  modal.style.display = 'flex';
  document.body.style.overflow = 'hidden'; // Prevent background scrolling
}

//----------------------------------------------------------------------------------------------------------------------------
// Hide documentation modal
//----------------------------------------------------------------------------------------------------------------------------
function hideDocumentation() {
  const modal = document.getElementById('docsModal');
  modal.style.display = 'none';
  document.body.style.overflow = ''; // Restore scrolling
}

//----------------------------------------------------------------------------------------------------------------------------
// Initialize documentation handlers
//----------------------------------------------------------------------------------------------------------------------------
function initDocumentation() {
  const docsBtn = document.getElementById('docsBtn');
  const docsModal = document.getElementById('docsModal');
  const docsClose = document.getElementById('docsClose');

  // Open documentation
  if (docsBtn) {
    docsBtn.addEventListener('click', showDocumentation);
  }

  // Close documentation
  if (docsClose) {
    docsClose.addEventListener('click', hideDocumentation);
  }

  // Close on background click
  if (docsModal) {
    docsModal.addEventListener('click', (e) => {
      if (e.target === docsModal) {
        hideDocumentation();
      }
    });
  }

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      hideDocumentation();
    }
  });
}

//----------------------------------------------------------------------------------------------------------------------------
// Auto-initialize on DOM load
//----------------------------------------------------------------------------------------------------------------------------
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initDocumentation);
} else {
  initDocumentation();
}
