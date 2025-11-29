# Water Level Monitor pro Raspberry Pi Zero W

Systém pro monitorování hladiny vody v barelu s integrací do Apple HomeKit.

## 🎯 Funkce

- ✅ Monitorování hladiny vody pomocí plovákového spínače
- 📱 Integrace s Apple Home (iOS/macOS)
- 🔔 Automatické notifikace když voda stoupne k plovaku
- 🔄 Automatické spuštění při startu systému
- 📊 Logování událostí

## 🛠️ Potřebné komponenty

### Hardware
- Raspberry Pi Zero W
- Plovákový spínač (float switch)
- Propojovací kabely
- Napájení pro RPi (5V micro USB)

### Software
- Raspberry Pi OS (Lite nebo Desktop)
- Python 3.7+
- Apple Home aplikace (iOS/macOS)

## 📦 Instalace

### 1. Příprava Raspberry Pi

```bash
# Připoj se k Raspberry Pi přes SSH nebo přímo
# Stáhni projekt
git clone <repository_url>
cd water-level-monitor

# NEBO zkopíruj soubory ručně
```

### 2. Spuštění instalačního skriptu

```bash
chmod +x install.sh
./install.sh
```

Instalační skript automaticky:
- Aktualizuje systém
- Nainstaluje potřebné balíčky
- Nainstaluje Python závislosti
- Vytvoří systemd service pro automatické spuštění

## 🔌 Zapojení Hardware

### Plovákový spínač

Připoj plovákový spínač k Raspberry Pi následovně:

```
Plovákový spínač:
- Jeden pin → GPIO 17 (nebo jiný dle tvé volby)
- Druhý pin → GND (zem)
```

**Poznámka:** Kód používá interní pull-down rezistor, takže nepotřebuješ externí rezistor.

### GPIO Pin Layout (Raspberry Pi Zero W)

```
3.3V  (1) (2)  5V
GPIO2 (3) (4)  5V
GPIO3 (5) (6)  GND
GPIO4 (7) (8)  GPIO14
GND   (9) (10) GPIO15
GPIO17(11)(12) GPIO18  ← Výchozí pin pro plovák
...
```

### Změna GPIO pinu

Pokud chceš použít jiný pin, uprav konstantu v `water_level_monitor.py`:

```python
FLOAT_SWITCH_PIN = 17  # Změň na požadovaný GPIO pin
```

## 🚀 Použití

### Ruční spuštění (pro testování)

```bash
python3 water_level_monitor.py
```

### Spuštění jako služba

```bash
# Spustit službu
sudo systemctl start water-level-monitor

# Povolit automatické spuštění při bootování
sudo systemctl enable water-level-monitor

# Zkontrolovat stav
sudo systemctl status water-level-monitor

# Zobrazit logy
sudo journalctl -u water-level-monitor -f

# Zastavit službu
sudo systemctl stop water-level-monitor
```

## 📱 Přidání do Apple Home

1. Spusť program/službu na Raspberry Pi
2. V logu najdi QR kód nebo PIN kód pro párování
3. Otevři Apple Home app na iPhone/iPad
4. Klikni na "+" a vyber "Přidat příslušenství"
5. Naskenuj QR kód nebo zadej PIN ručně
6. Potvrď přidání (může se zobrazit varování o nepodporovaném příslušenství - ignoruj)
7. Pojmenuj senzor (např. "Barel - Hladina vody")
8. Přiřaď do místnosti

### Nastavení notifikací

1. V Apple Home otevři detail senzoru
2. Přejdi do nastavení
3. Zapni "Oznámení"
4. Nastav kdy chceš být informován (např. "Když je detekována voda")

## 🔧 Konfigurace

### Změna intervalu kontroly

V souboru `water_level_monitor.py`:

```python
CHECK_INTERVAL = 1  # Interval v sekundách (výchozí: 1s)
```

### Změna HomeKit portu

```python
driver = AccessoryDriver(port=51826)  # Změň pokud je port obsazený
```

## 🐛 Řešení problémů

### Senzor se nezobrazuje v Apple Home

1. Zkontroluj že služba běží: `sudo systemctl status water-level-monitor`
2. Zkontroluj logy: `sudo journalctl -u water-level-monitor -f`
3. Ujisti se že RPi a iPhone jsou na stejné WiFi síti
4. Restartuj službu: `sudo systemctl restart water-level-monitor`

### GPIO chyby

1. Zkontroluj že používáš správný GPIO pin
2. Ujisti se že spínač je správně zapojen
3. Zkontroluj že máš správná oprávnění (uživatel `pi`)

### Python závislosti

Pokud instalace HAP-python selže:

```bash
sudo apt-get install -y python3-dev libavahi-compat-libdnssd-dev
pip3 install --break-system-packages HAP-python
```

## 📊 Logování

Všechny události jsou logovány:
- ✅ Normální hladina vody
- ⚠️ Vysoká hladina vody (potřeba vyprázdnit)
- 🔄 Změny stavu

Zobrazení logů v reálném čase:
```bash
sudo journalctl -u water-level-monitor -f
```

## 🔄 Aktualizace

```bash
# Zastav službu
sudo systemctl stop water-level-monitor

# Aktualizuj soubory
# ... zkopíruj nové verze souborů

# Restartuj službu
sudo systemctl start water-level-monitor
```

## ⚙️ Testování plovákového spínače

Jednoduchý testovací skript:

```python
import RPi.GPIO as GPIO
import time

PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    while True:
        state = GPIO.input(PIN)
        print(f"Plovák: {'NAHOŘE (voda vysoká)' if state else 'DOLE (voda nízká)'}")
        time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()
```

## 📝 Poznámky

- Program používá LeakSensor service pro kompatibilitu s Apple Home
- Vysoká hladina vody = "Leak Detected" v Apple Home
- Můžeš nastavit automatizace v Apple Home (např. zapnout červené světlo když je barel plný)

## 🔒 Bezpečnost

- HomeKit komunikace je šifrovaná
- PIN kód je generován automaticky
- Doporučuji změnit výchozí heslo Raspberry Pi

## 📄 Licence

MIT License - volně použitelné pro osobní i komerční účely.

## 🤝 Podpora

Pro problémy nebo dotazy:
1. Zkontroluj sekci "Řešení problémů" výše
2. Zkontroluj logy služby
3. Vytvoř issue v repository
