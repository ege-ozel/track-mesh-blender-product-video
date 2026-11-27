# Video sahneleri — inceleme devri, 21 Ekim 2026

İncelenecek sürüm: **studios-v09**. Önceki sahneler korunmuştur. v05 kamera kontrolünde başarısız olan ara sürümdür; inceleme hedefi v09'dur.

## Dosyalar

- Blender: `D:/CodeSpace/track-mesh-blender-product-video/scenes/versions/trackmesh-studios-v09.blend`
- Dokuz planlık storyboard: `D:/CodeSpace/track-mesh-blender-product-video/renders/previews/studios-v09-storyboard.png`
- Düzenlenmiş 960×540 önizlemeler: `renders/previews/studios-v09-50/edit/`
- Yakın planların 1920×1080 önizlemeleri: `renders/previews/studios-v09-100/edit/`
- Sahne kontrolü: `logs/audit-studios-v08.json`
- Masaüstü kaynak kimliği: `logs/review-source-v5.json`; sabit kaynak kopyası `demo-ui-v5/source/`
- Ekran kayıtları: `logs/ui-capture-v5.json`, `logs/native-vst3-capture-v5.json`

## v09 — altyazı zamanlaması

Örnek veri altyazısının başlangıcı 390'dan 400. kareye alındı; indirme başlangıcıyla eşleşir. v08'in ham render'ları yeni sürüme kopyalanarak 12 adet 960×540 compose karesi, üç adet 1080p compose karesi ve storyboard yeniden üretildi. v09 `.blend` dosyası v08'den sürümlendi; kamera ve geometri aynı kaldı. 398 ve 400. kareler değişti; 370, 430 ve 690. karelerin v08 ile piksel olarak aynı olduğu doğrulandı. Önceki sürümler korunuyor. Sahne kontrolünün mevcut kanıtı v08 auditidir; v09'da yalnız edit zamanlaması ve sürüm bilgisi değişti.

## v08 — kullanıcı onaylı inceleme düzeltmeleri

`CLAUDE_REVIEW_studios-v07.md` içindeki (b) kararı uygulandı. Önceki dosyalar ve inceleme raporu korundu.

- Videodaki ve storyboard başlıklarındaki şehir isimleri kaldırıldı. Etiketler yalnızca `STUDIO A` ve `STUDIO B`; üçüncü plan altyazısı `Another studio.`. Sıcak ve soğuk oda görünümleri korunuyor. Şehirler arasındaki aktarım iddiası yok.
- Veri altyazısı: `Only the changed parts travel. Example: 44 MB new in a 1.6 GB project.` Sentetik yeni veri örneği olarak ifade edilir; ölçülmüş toplam ağ trafiği değildir.
- `PC to PC.` ve `A direct link. No cloud copy of your project files.` korundu. Windows, iki PC'nin çevrimiçi olması, en az bir erişilebilir bağlantı ve relay bulunmaması açıklaması İngilizce/Türkçe `VIDEO_DESCRIPTION.md` içinde hazırlandı.
- Kapanışa `For Windows` eklendi.
- Get yakın planı neredeyse önden gösterilir; f/8 ile ekran netliği korunur. Onay 332–399 arasında 68 kare / 2,83 saniye durur (önce 350–387, 38 kare / 1,58 saniye). Veri alımı 400. karede başlar. Film yine 30 saniyedir.
- Yakın plan altyazıları uygulamanın sol kenar çubuğu üzerine gelmeyecek biçimde sağa kaydırıldı. Diyalog metni ve ürün ekran verileri değiştirilmedi; önceki v5 ekran varlıkları kullanıldı.
- Kaydedilmiş **v08** dosyası 720 kare kontrolünü sıfır hatayla geçti. 12 örnek an (398/400 geçişi ve 560 tamamlanma dahil; 15 ham görsel) 960×540 düzenlenmiş kareye dönüştürüldü. 370, 430 ve 690. kareler ayrıca 1920×1080 üretildi; yakın planlar ve kapanış gözle incelendi. Storyboard yeniden oluşturuldu. Python sözdizimi ve `git diff --check` geçti.

Tam animasyon/final encode ve v08'in bağımsız ikinci incelemesi henüz tamamlanmış sayılmaz. Aşağıdaki v05–v07 kanıtları önceki hazırlığın geçmişidir; güncel inceleme hedefi yukarıdaki v08 dosyalarıdır.

## Önceki hazırlık ve kanıt (v05–v07)

30 saniye, 24 fps, 1920×1080, altı plan, iki ayrı stüdyo ve altı kamera. İstanbul'un sıcak ışığı korunmuştur. Berlin'de yanan pencere oranı yaklaşık %21'den %14'e, pencere emisyonu 1.3'ten 0.55'e, raf ışığı 30 W'tan 18 W'a düşürüldü; oda dolgusu 14 W'tan 18 W'a çıktı. Monitörün şehirden öne gelmesi amaçlandı. Bu şehirler hikâye mekânlarıdır; ayrı fiziksel ağlar arasında yapılmış aktarımın kanıtı değildir.

Masaüstü kaynakları ürün deposundan salt okunur kopyalandı: HEAD `690e6b5091825a34125128dfc8d7ec4cf5607fc9`. Kopyalama anında ürün çalışma ağacında `apps/desktop/src-tauri/Cargo.toml` değişikliği vardı; değiştirilmedi. Dosya SHA-256 değerleri manifesttedir. Başka ajanların sonraki değişiklikleri otomatik olarak bu çekime girmez.

Gerçek React bileşenleri ve stilleri kullanıldı; Tauri çağrıları yalıtılmış sentetik durumla değiştirildi. Yedi durum yakalandı; tarayıcı hatası yok. Get onayı eski DAW-kapalı sorusundan güncel `receive.rs` içindeki dosya listesi + yeni veri miktarı + DAW'ı kapatma + yedek açıklaması + Get/Cancel akışına güncellendi. Bu pencere tarayıcıda yeniden çizimdir; gerçek native diyaloğun piksel kaydı değildir. Dosya adları ve 128 GB boş alan dahil bütün veriler örnektir.

VST3 dört durumu mevcut derlenmiş gerçek native editörden yalıtılmış SDK host/Named Pipe ile yeniden yakalandı. Binary SHA-256: `5dcd6e4e3a14a66bfb5ded4c14c97ccba55d70bb0248692be0ad5b3b67cf1ce2`. Bu binary'nin bütün güncel kaynaklardan yeniden derlendiği burada doğrulanmadı. Yakalanan boyut 580×384; sahne oranı ve Paylaş düğmesine basan imleç buna uyarlandı. Otomatik paylaşım kapalıdır; kaydetme sonrasında bir Paylaş tıklaması gösterilir.

v05 kontrolü Berlin yakın planında 420–456 aralığında ekran köşesinin taşmasını yakaladı. Kamera v06'da geri çekildi. Kaydedilmiş v06 yeniden açılarak 720 karenin tamamında her ekran için tam bir görünür durum, ekranın dört köşesinin kadrajda kalması, ekran merkezinin kamera kesme düzlemleri içinde olması, altı marker, çıktı biçimi ve tüm dosya görsellerinin paketlenmesi kontrol edildi: **0 hata**. Bu kontrol keyfi mesh kesişmelerini veya ürünün çalışmasını kanıtlamaz.

Dokuz örnek an render edildi; iki split anı iki yarım görüntü kullanır (toplam 11 ham görsel). Get onayı ve ilerleme için iki ek 1080p still alındı. Storyboard ve düzenlenmiş kareler gözle incelendi. Ekran aktarımı bittiği anda (560. kare) hareketli paket metaforu durur. Her düzenlenmiş karede Concept visualization ibaresi bulunur; Blender'ın ham render'ında edit yazıları bulunmaz. Nihai çıktı **compose_studios.py** üzerinden geçmelidir.

## Pilado ve Codex için kontrol

v07 ayrıca beyaz onay penceresinin emisyonunu 1.9'dan 1.0'a, bloom gücünü 0.45'ten 0.22'ye düşürür ve eşiğini 0.55'ten 1.1'e çıkarır. Amaç ince metnin parlamada kaybolmasını azaltmaktır. v07 de kaydedilmiş dosyadan 720 kare kontrolünü sıfır hatayla geçti; dokuz plan önizlemesi ve iki 1080p yakın plan yeniden üretildi.

1. Kaynak kopyasının ve native binary kimliğinin çekilecek son ürün sürümüyle uyumunu değerlendirin. Ürün değiştiyse ekranları yeni bir asset sürümünde yenileyin.
2. Get öncesi değişiklik listesi, yedekleme ve DAW kapatma koşulunu; varsayılan kapalı auto-share ve açık Paylaş tıklamasını doğrulayın.
3. 370 ve 430. kareleri 1080p'de açıp onay metninin ve ilerlemenin okunurluğunu; Studio B ışığı, perspektif, kamera kesmeleri ve ekran önüne gelen altyazıları değerlendirin. Storyboard'daki küçük metinlerin telefonda okunacağı varsayılmasın.
4. `D:/CodeSpace/track-mesh/docs/IMPLEMENTATION.md` içindeki güncel canlı kanıtlarla iddiaları karşılaştırın. 44 MB / 1.6 GB, hız ölçümü değildir. Bu üretimde gerçek paylaşım, dosya aktarımı, DAW ses/DPI veya WAN/CGNAT denemesi yapılmadı. Son build'deki canlı çekim akışı ürün tarafında ayrıca doğrulanmalıdır.
5. Bulguları önem derecesi, kare/nesne/dosya ve somut gerekçeyle bu devre ekleyin. Görsel ve ürün incelemesi bitmeden sahneye nihai onay verilmiş sayılmasın.

## Yeniden çalıştırma

Proje kökünde PowerShell:

```powershell
$blenderVideo = '.\tools\blender\blender-5.2.2-windows-x64\blender.exe'
& $blenderVideo --background scenes/versions/trackmesh-studios-v09.blend --python-exit-code 1 --python scripts/audit_studios.py
& $blenderVideo --background scenes/versions/trackmesh-studios-v09.blend --python-exit-code 1 --python scripts/render_studios.py -- --stills 60,135,175,210,300,370,430,530,690 --percent 50
python scripts/compose_studios.py studios-v09 --percent 50
python scripts/storyboard_studios.py studios-v09
```

Yeni sahne üretmek için `build_studios.py -- --screens v5 --review-lighting` sonraki boş sürüm numarasını seçer. Tam animasyon/final encode bu hazırlık turunda yapılmadı.
