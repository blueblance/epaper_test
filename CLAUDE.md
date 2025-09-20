# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Hardware and Environment

This is a C++ driver for the QYEG0579RYS683 e-paper display, specifically designed for Raspberry Pi with the bcm2835 library. The display supports 4-color output (black, white, yellow, red) and multiple orientation modes.

**Hardware Requirements:**
- Raspberry Pi running Raspbian
- QYEG0579RYS683 e-paper display
- bcm2835 C library (http://www.airspayce.com/mikem/bcm2835/)

**Pin Connections:**
- VCC → 3.3V
- GND → GND
- DIN → MOSI (Physical pin 19)
- CLK → SCLK (Physical pin 23)
- CS → CE0 (Physical pin 24, BCM 8)
- D/C → BCM 25 (Physical pin 22)
- RES → BCM 17 (Physical pin 11)
- BUSY → BCM 24 (Physical pin 18)

## Build System

**Build the project:**
```bash
make
```

**Clean build artifacts:**
```bash
make clean
```

**Run the demo (requires sudo for GPIO access):**
```bash
sudo ./epd
```

## Code Architecture

### Core Classes

**EpdIf (epdif.h/cpp)**: Hardware abstraction layer
- Provides GPIO pin control via bcm2835 library
- Handles SPI communication
- Defines pin mappings (RST_PIN=17, DC_PIN=25, CS_PIN=8, BUSY_PIN=24)

**Epd (epd0579RYS683.h/cpp)**: Main e-paper display driver
- Inherits from EpdIf for hardware access
- Implements display initialization, frame buffering, and rendering
- Supports 4 orientation modes: FPCLeft, FPCRight, FPCUp, FPCDown
- Key methods:
  - `Init(Direction)`: Initialize display with orientation
  - `SetFrameScreen_ALL_Horizontal/Vertical()`: Set image data
  - `DisplayFrame_And_Sleep()`: Refresh display and enter sleep mode
  - `ClearFrameMemory()`: Clear display to white

### Display Specifications

- Resolution: 400x272 pixels (MAX_LINE_BYTES=100, MAX_COLUMN_BYTES=272)
- Color depth: 2-bit (4 colors: black=0x00, white=0x01, yellow=0x02, red=0x03)
- Orientation support: All 4 FPC orientations with automatic rotation

### Image Data

**imagedata.h/cpp**: Contains pre-compiled image arrays
- `gImage_1`, `gImage_2`, `gImage_3`: Static image data for demo
- Images are stored as compressed byte arrays for direct display

## Development Notes

- All GPIO operations require root privileges (use `sudo`)
- The display has built-in rotation handling based on FPC orientation
- Image data format is 2-bit packed, with specific bit patterns for each color
- Display refresh cycles include automatic sleep mode for power efficiency
- The demo cycles through different orientations and images before clearing to white