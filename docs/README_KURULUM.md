# Track Mesh 3D Video — Windows Hızlı Başlangıç

## 0. Script ne yapar?

`setup-trackmesh-blender.ps1` tek komutla user profile altında bir **TrackMeshVideo** çalışma klasörü hazırlar. Mevcut Blender 5.0'ı kaldırmaz. Blender **5.2.2 Windows x64 portable ZIP** dosyasını resmî `download.blender.org` üzerinden yaklaşık 386 MiB indirir; sabitlenmiş SHA256 ile doğrular, `$HOME\TrackMeshBlenderTools` içine açar. `uvx` yoksa `winget` üzerinden `uv` kurmayı dener. Topluluk `blender-mcp` eklentisini **yalnız Blender 5.2 kullanıcı eklentisi dizinine** kurar. Bilgisayarda Claude Code veya Codex CLI varsa `blender` MCP sunucusunu kaydeder; yoksa atlar. Kodla basit 3D sahne oluşturur ve isteğe bağlı tek 960×540 still render alır.

Bu işlem paket indirip çalıştırdığı için önce scripti incele. Aşağıdaki komutu paket içindeki **setup-trackmesh-blender.ps1 dosyasının bulunduğu klasörde** çalıştır.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\setup-trackmesh-blender.ps1
```

PowerShell 7 de kullanılabilir: `pwsh -File .\setup-trackmesh-blender.ps1`. `-ExecutionPolicy Bypass` yalnız bu **yeni PowerShell işlemi** içindir; makinenin kalıcı politika ayarını değiştirmez.

### Opsiyonel parametreler

- Blender'ı zaten kurduysan ve portable indirmek istemiyorsan `-SkipBlenderDownload` kullan; otomatik sahne üretiminin portable exe bulunmadığında atlanacağını bil.
- MCP'yi daha sonra kuracaksan `-SkipMcp` kullan.
- Yalnız .blend üretip render almak istemiyorsan `-SkipPreview` kullan.
- Özel proje konumu: `-ProjectRoot 'D:\CodeSpace\track-mesh-video'`.

## 1. GUI'de kaçınılmaz kısa adım

Blender portable'ı aç: `$HOME\TrackMeshBlenderTools\blender-5.2.2-windows-x64\blender.exe`.

`Edit > Preferences > Add-ons` bölümünde **Blender MCP** eklentisini etkinleştir (görünmüyorsa Blender'ı yeniden başlat). Sonra 3D Viewport'ta `N` tuşu -> `BlenderMCP` -> **Start MCP Server** veya **Connect to Claude**. Eklentinin buton metni sürüme göre değişebilir. MCP sunucusu yalnız localhost'ta çalışmalı; portu internete açma. Claude Code veya Codex'i yeniden başlat. **Aynı anda yalnız bir MCP istemcisiyle bağlan**.

Bunlar yalnızca gerekli yerel uygulama izin/adımlarıdır; script uzaktan UI düğmesine basmış gibi davranmaz.

## 2. Dosyalar

- `scenes/trackmesh-starter.blend` — iki fiziksel 3D monitör/masa, kamera, ışıklar, sembolik P2P parçacıkları.
- `renders/previews/trackmesh-proof-of-concept.png` — yalnız render başarıyla tamamlandıysa oluşur.
- `assets/screens/daw.png` — ChatGPT'de üretilen sol monitör görüntüsü (opsiyonel).
- `assets/screens/trackmesh.png` — ChatGPT'de üretilen sağ monitör görüntüsü (opsiyonel).
- `assets/backgrounds/studio.png` — ayrı üretilen arka plan görüntüsü (opsiyonel).
- `docs/TRACKMESH_VIDEO_MASTER_PROMPT.md` — Codex/Claude Code'a verilecek master talimat.
- `docs/GORSEL_URETIM_PROMPTLARI.md` — ChatGPT'de asset üretimi talimatları.

Ekran/arka plan görselleri sonradan eklendiğinde Blender 5.2 CLI üzerinden tekrar üret:

```powershell
$env:TRACKMESH_VIDEO_PROJECT = "$HOME\TrackMeshVideo"
& "$HOME\TrackMeshBlenderTools\blender-5.2.2-windows-x64\blender.exe" --background --factory-startup --python "$HOME\TrackMeshVideo\scripts\build_scene.py" -- --preview
```

Bu manuel komut `trackmesh-starter.blend` üzerine yazar; önce Blender'ın sahne kopyasını `scenes/versions` içine kaydet.

## 3. Sonraki adım

`TrackMeshVideo` klasöründe Claude Code veya Codex başlat. `docs/TRACKMESH_VIDEO_MASTER_PROMPT.md` içindeki metni gönder. Önce yalnız sahne inceleme ve 1 hero frame iste; animasyonun tamamını izinsiz render ettirme.

## 4. Sınırlar

- Blender 5.2 Portable indirmesi/internet gerekir; 386 MiB ZIP ve çıkarılmış dosyalar disk alanı tüketir.
- Script Claude Code/Codex'i **yüklemez veya hesaplarına giriş yapmaz**; mevcut olanlara MCP ekler. Gerekirse ayrı kur.
- UPnP, Supabase, Track Mesh gerçek Windows DAW dosyalarıyla scriptin hiçbir ilişkisi yoktur; gerçek projeye veya özel dosyaya dokunmaz.
- İlk sahne bir prosedürel başlangıçtır, son kalite reklam filmi değildir. Kullanıcı tasarım onayı ve birkaç render revizyonu gerekir.
- Renderer GPU zorunlu kılmaz; CPU Cycles fallback kullanır, performans donanıma bağlıdır.
- MCP üçüncü parti eklentiyle Blender içinde kod çalıştırır; eklentiye yalnız güvendiğin istemciden localhost bağlantısı sağla.
