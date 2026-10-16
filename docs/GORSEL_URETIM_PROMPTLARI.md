# Track Mesh — ChatGPT ile üretebileceğimiz görsel asset'ler

Bunlar **2D** üretimlerdir. Blender'daki gerçek 3D monitörleri, kamerayı, 3D mekânı ve ışık kaynaklarını `bpy` oluşturur. Görseller yalnız arka plan/ekran texture'ı/referans olacaktır. Her varlığı aşağıdaki dosya adına kaydet.

## A — Ortam görseli (`assets/backgrounds/studio.png`)

**Görsel üretim isteği:**

> Create a cinematic, photorealistic but minimal DARK PREMIUM music production studio background plate for a 3D Blender product animation. Wide 16:9 composition, graphite and deep charcoal walls, subtle textured acoustic panels, restrained warm amber ambient accents on the LEFT, subtle teal rim ambience on the RIGHT, tasteful depth, soft volumetric gradients. Middle ground kept spacious to place TWO SEPARATE 3D computer workstations later. NO computer monitors, NO desk, NO people, NO text, NO logos, NO watermarks, NO glowing sci-fi clutter. Balanced cinematography, realistic materials, believable reflections, low visual noise, camera-height perspective. 1920x1080.

Not: bu 2D görsel derinlik hissi verse de kamera fiziksel olarak çevresinde dolaşınca gerçek 3D paralaks oluşturmaz. Yavaş kamera hareketinde, arka plana yeterince uzak yerleştirerek veya HDRI/gerçek geometriyle destekleyerek kullan.

## B — DAW ekranı (`assets/screens/daw.png`)

**Görsel üretim isteği:**

> A clean, fictional digital audio workstation interface image designed as a 16:9 SCREEN TEXTURE for a Blender 3D monitor. Inspired by the general look and density of modern Ableton Live / FL Studio arrangements but NOT a direct copy. Dark gray arrangement timeline, eight colorful audio/MIDI tracks, visible waveform silhouettes and MIDI clips, clear transport controls, no real artist names, no copyrighted songs, no private file paths, no personal device identity, no watermark. Slight amber highlight. Flat orthographic FRONT view, no monitor frame, no angled perspective, NO physical computer, sharp readable UI, realistic product-demo screenshot quality. 1920x1080.

Alternatif: Gerçek DAW UI göstermek istiyorsak demo proje ve sentetik örnek içerik kullanılarak izinli bir ekran görüntüsü oluşturabiliriz; kişisel projeleri göstermeyiz.

## C — Track Mesh ekranı (`assets/screens/trackmesh.png`)

**Görsel üretim isteği:**

> High-end realistic FRONT-ON user interface mockup for "Track Mesh", a Windows desktop app for trusted direct peer-to-peer DAW project snapshots. Dark premium minimal product design with graphite surface, elegant teal accents, subtle borders, understated cards and ample whitespace. Show one fictional project named "Neon Forest Demo", a trusted peer called "Studio B", a tiny status "DIRECT · QUIC", snapshot timeline, subtle progress bar, a primary button "Receive" and a note "Close DAW project before receiving". No personal names, no real IPs, no cryptographic secrets. No browser chrome, no outer monitor, no perspective, no watermark. Text should be crisp where possible. 1920x1080 16:9.

Not: Üretilmiş görselde yazılar hatalı olabilir. **Kesin UI metinleri** ve ürün doğruluğu gerekiyorsa React/Figma mockup ile HTML/CSS ekranı üretip PNG screenshot almak daha güvenilir.

## D — Görsel referans / moodboard (dosya opsiyonel)

> Dark premium 3D tech product film moodboard, two minimalist black workstations, brushed metal, warm amber DAW side, cool teal Track Mesh side, elegant camera move, subtle physically plausible emissive connection path, no cyberpunk, understated animation, high-end software launch aesthetics, 16:9.

## Dosya kuralları

- PNG tercihen 1920×1080 veya 2560×1440, 16:9. Ekran texture'larına monitör çerçevesi dahil etme.
- Gizli kullanıcı ekranı, özel proje dosyası, gerçek cihaz kimliği, davet linki veya anahtar verme.
- Varlıkların ayrı ayrı üretimi, tek bir kolaj üretiminden daha iyi yeniden kullanım sağlar.
- Görseli bu konuşmada isteyebilirsin; başka bir konuşmada da `GORSEL_URETIM_PROMPTLARI.md` bölümünü yapıştırıp üretim isteyebilirsin.
