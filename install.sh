#!/bin/bash
# Instalační skript pro Water Level Monitor

echo "🔧 Instalace Water Level Monitor pro Raspberry Pi Zero W"
echo "========================================================="

# Update systému
echo "📦 Aktualizuji systém..."
sudo apt-get update
sudo apt-get upgrade -y

# Instalace potřebných balíčků
echo "📦 Instaluji potřebné balíčky..."
sudo apt-get install -y python3 python3-pip python3-dev libavahi-compat-libdnssd-dev

# Instalace Python závislostí
echo "🐍 Instaluji Python závislosti..."
pip3 install --break-system-packages -r requirements.txt

# Nastavení práv pro spuštění
echo "🔑 Nastavuji práva..."
chmod +x water_level_monitor.py

# Vytvoření systemd service
echo "⚙️ Vytvářím systemd service..."
sudo tee /etc/systemd/system/water-level-monitor.service > /dev/null <<EOF
[Unit]
Description=Water Level Monitor HomeKit Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/water_level_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

echo "✅ Instalace dokončena!"
echo ""
echo "📋 Další kroky:"
echo "1. Zkontroluj GPIO pin v souboru water_level_monitor.py (výchozí: GPIO 17)"
echo "2. Připoj plovákový spínač k Raspberry Pi"
echo "3. Spusť službu: sudo systemctl start water-level-monitor"
echo "4. Povolit automatické spuštění: sudo systemctl enable water-level-monitor"
echo "5. Zkontrolovat stav: sudo systemctl status water-level-monitor"
echo "6. Přidej do Apple Home pomocí kódu který se zobrazí v logu"
echo ""
echo "📱 Pro zobrazení logů použij: sudo journalctl -u water-level-monitor -f"
