#!/usr/bin/env python3
"""
Water Level Monitor for Raspberry Pi Zero W
Monitors water level using a float switch and integrates with Apple HomeKit
"""

import RPi.GPIO as GPIO
import time
import logging
from datetime import datetime
from pyhap.accessory import Accessory
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_SENSOR

# Konfigurace
FLOAT_SWITCH_PIN = 17  # GPIO pin pro plovákový spínač (změň podle tvého zapojení)
CHECK_INTERVAL = 3600  # Interval kontroly - 1 hodina (3600 sekund)
NOTIFICATION_START_HOUR = 9   # Oznámení se posílají od 9:00
NOTIFICATION_END_HOUR = 21    # Oznámení se posílají do 21:00

# Nastavení logování
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WaterLevelSensor(Accessory):
    """
    HomeKit accessory pro monitorování hladiny vody
    Používá LeakSensor service pro Apple Home
    """
    
    category = CATEGORY_SENSOR
    
    def __init__(self, *args, pin=FLOAT_SWITCH_PIN, **kwargs):
        super().__init__(*args, **kwargs)
        self.pin = pin
        self.was_water_level_high = False
        
        # Nastavení GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Přidání LeakSensor service pro Apple Home
        leak_service = self.add_preload_service('LeakSensor')
        self.leak_detected = leak_service.configure_char('LeakDetected')
        
        # Přidání BatteryService (volitelné, ale užitečné)
        battery_service = self.add_preload_service('BatteryService')
        self.battery_level = battery_service.configure_char('BatteryLevel', value=100)
        self.charging_state = battery_service.configure_char('ChargingState', value=2)
        self.status_low_battery = battery_service.configure_char('StatusLowBattery', value=0)
        
        logger.info(f"Water Level Sensor inicializován na GPIO pin {self.pin}")
    
    def check_water_level(self):
        """
        Kontroluje stav plovákového spínače
        Returns: True pokud je detekována vysoká hladina vody
        """
        
        # GPIO.LOW znamená že plovák je nahoře (voda je vysoká)
        water_high = GPIO.input(self.pin) == GPIO.LOW
        
        return water_high
    
    def is_notification_time(self):
        """
        Kontroluje zda je aktuální čas v povoleném rozmezí pro oznámení
        Returns: True pokud je čas mezi NOTIFICATION_START_HOUR a NOTIFICATION_END_HOUR
        """
        current_hour = datetime.now().hour
        return NOTIFICATION_START_HOUR <= current_hour < NOTIFICATION_END_HOUR

    @Accessory.run_at_interval(CHECK_INTERVAL)
    async def run(self):
        """
        Pravidelně kontroluje hladinu vody a aktualizuje HomeKit
        Oznámení se posílají pouze v povoleném časovém rozmezí
        """

        is_water_level_high = self.check_water_level()
        is_allowed_time = self.is_notification_time()

        # Pokud se stav změnil
        if is_water_level_high != self.was_water_level_high:
            self.was_water_level_high = is_water_level_high

            if is_water_level_high:
                logger.warning("⚠️ VAROVÁNÍ: Vysoká hladina vody detekována! Vyprázdni barel!")
                if is_allowed_time:
                    self.leak_detected.set_value(1)  # Leak detected
                else:
                    logger.info(f"Oznámení odloženo - mimo povolený čas ({NOTIFICATION_START_HOUR}:00-{NOTIFICATION_END_HOUR}:00)")
            else:
                logger.info("✓ Hladina vody OK")
                self.leak_detected.set_value(0)  # No leak

        # Pokud je vysoká hladina a jsme v povoleném čase, pošli oznámení (i když se stav nezměnil)
        elif is_water_level_high and is_allowed_time and self.leak_detected.get_value() == 0:
            logger.info("Posílám odložené oznámení o vysoké hladině vody")
            self.leak_detected.set_value(1)
        
    def stop(self):
        """Vyčištění při ukončení"""
        super().stop()
        GPIO.cleanup()
        logger.info("GPIO cleanup dokončen")


def main():
    """Hlavní funkce pro spuštění HomeKit accessory"""
    try:
        # Vytvoření accessory driver
        driver = AccessoryDriver(port=51826)
        
        # Vytvoření water level sensor accessory
        sensor = WaterLevelSensor(driver, 'Water Level Monitor')
        
        # Přidání accessory do driveru
        driver.add_accessory(accessory=sensor)
        
        logger.info("🚀 Spouštím Water Level Monitor...")
        logger.info("📱 Otevři Apple Home app a přidej accessory")
        logger.info("🔑 Použij kód který se zobrazí v konzoli")
        
        # Spuštění event loop
        driver.start()
        
    except KeyboardInterrupt:
        logger.info("Ukončuji program...")
    except Exception as e:
        logger.error(f"Chyba: {e}", exc_info=True)
    finally:
        GPIO.cleanup()
        logger.info("Program ukončen")


if __name__ == '__main__':
    main()
