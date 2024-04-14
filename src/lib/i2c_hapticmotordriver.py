from smbus2 import SMBus

class HapticMotorDriver:
    DEVICE_ADDRESS = 0x4A
    CHIP_REV_REG = 0x00
    EXPECTED_CHIP_REV = 0xBA
    TOP_CTL1 = 0x22
    TOP_CTL2 = 0x23
    TOP_CFG1 = 0x13
    DRO_MODE = 1
    Multiplexer_Address = 0x70 #TC9A548A I2C Multiplexer Address
    

    def __init__(self):
        self.bus = SMBus(1)  # 1 indicates /dev/i2c-1
        if self._driver_init():
            print("Haptic Motor Driver initialized successfully.")
        else:
            print("Failed to initialize Haptic Motor Driver.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.bus.close()

    def _read_register(self, register):
        return self.bus.read_byte_data(self.DEVICE_ADDRESS, register)

    def _write_register(self, register, value):
        self.bus.write_byte_data(self.DEVICE_ADDRESS, register, value)

    def _driver_init(self):
        chip_rev = self._read_register(self.CHIP_REV_REG)
        if chip_rev == self.EXPECTED_CHIP_REV:
            # Set Operation Mode
            self._write_register(self.TOP_CTL1, self.DRO_MODE)
            # Enable Frequency Tracking
            self._enable_freq_track(True)
            return True
        else:
            return False

    def _enable_freq_track(self, enable):
        current_value = self._read_register(self.TOP_CFG1)
        new_value = current_value | (1 << 3) if enable else current_value & ~(1 << 3)
        self._write_register(self.TOP_CFG1, new_value)

    def set_vibration(self, intensity):
        intensity = max(0, min(intensity, 255))  # Ensure intensity is within bounds
        self._write_register(self.TOP_CTL2, intensity)
        print(f"Vibration intensity set to {intensity}.")
