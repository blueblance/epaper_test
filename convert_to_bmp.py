#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
電子紙圖像陣列轉 BMP 圖檔工具
將 imagedata.cpp 中的圖像陣列資料轉換為 BMP 圖檔格式

解析度: 792x272 (但實際顯示為 400x272，因為每個位元組包含4個像素)
色彩格式: 2bit (4色: 黑、白、黃、紅)
資料排列: 水平掃描方式
"""

import re
import struct
from PIL import Image
import numpy as np

# 電子紙色彩定義
COLORS = {
    0x00: (0, 0, 0),       # black - 黑色
    0x01: (255, 255, 255), # white - 白色
    0x02: (255, 255, 0),   # yellow - 黃色
    0x03: (255, 0, 0)      # red - 紅色
}

# 顯示器規格
WIDTH = 792   # 實際是 400*2 (每個位元組包含4個像素，但水平方向需要*2)
HEIGHT = 272
BYTES_PER_ROW = 198  # 792/4 = 198 bytes per row

def parse_cpp_array(file_path, array_name):
    """
    從 C++ 檔案中解析指定的陣列資料
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 尋找陣列定義的開始 - 支持多種格式
    patterns = [
        rf'const unsigned char {array_name}\[53856\] = \{{[^{{]*?',
        rf'const unsigned char {array_name}\[53856\] = \s*\{{[^{{]*?',
        rf'const unsigned char {array_name}\[53856\] =\s*\{{\s*'
    ]

    match = None
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            break

    if not match:
        raise ValueError(f"找不到陣列 {array_name}")

    start_pos = match.end()

    # 從開始位置尋找陣列資料結束
    brace_count = 1
    current_pos = start_pos
    while brace_count > 0 and current_pos < len(content):
        char = content[current_pos]
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
        current_pos += 1

    array_data = content[start_pos:current_pos-1]

    # 提取16進位數值
    hex_values = re.findall(r'0X([0-9A-Fa-f]{2})', array_data)
    if not hex_values:
        raise ValueError(f"無法解析陣列 {array_name} 的資料")

    # 轉換為整數陣列
    byte_data = [int(hex_val, 16) for hex_val in hex_values]

    print(f"成功解析 {array_name}: 找到 {len(byte_data)} 個位元組")
    return byte_data

def decode_2bit_pixels(byte_data):
    """
    解碼2bit像素資料
    每個位元組包含4個像素 (2bit × 4 = 8bit)
    """
    pixels = []

    for byte_val in byte_data:
        # 從高位元開始提取4個像素
        pixel1 = (byte_val >> 6) & 0x03  # bits 7-6
        pixel2 = (byte_val >> 4) & 0x03  # bits 5-4
        pixel3 = (byte_val >> 2) & 0x03  # bits 3-2
        pixel4 = byte_val & 0x03         # bits 1-0

        pixels.extend([pixel1, pixel2, pixel3, pixel4])

    return pixels

def pixels_to_rgb_array(pixels, width, height):
    """
    將像素值陣列轉換為RGB圖像陣列
    """
    if len(pixels) != width * height:
        print(f"警告: 像素數量 {len(pixels)} 不符合預期的 {width * height}")
        # 截斷或補零
        if len(pixels) > width * height:
            pixels = pixels[:width * height]
        else:
            pixels.extend([0x01] * (width * height - len(pixels)))  # 補白色

    rgb_array = np.zeros((height, width, 3), dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            pixel_val = pixels[y * width + x]
            rgb_array[y, x] = COLORS.get(pixel_val, COLORS[0x01])  # 預設白色

    return rgb_array

def convert_array_to_bmp(byte_data, output_path, array_name):
    """
    將位元組陣列轉換為BMP圖檔
    """
    print(f"\n正在轉換 {array_name} 為 BMP...")

    # 解碼像素
    pixels = decode_2bit_pixels(byte_data)
    print(f"解碼得到 {len(pixels)} 個像素")

    # 轉換為RGB陣列
    rgb_array = pixels_to_rgb_array(pixels, WIDTH, height=HEIGHT)

    # 創建PIL圖像
    image = Image.fromarray(rgb_array, 'RGB')

    # 由於實際顯示器是400x272，我們將寬度縮放一半
    resized_image = image.resize((400, 272), Image.NEAREST)

    # 儲存BMP檔案
    resized_image.save(output_path, 'BMP')
    print(f"已儲存 {output_path}")

    return resized_image

def main():
    """
    主程式：轉換三個圖像陣列
    """
    cpp_file = 'imagedata.cpp'

    arrays_to_convert = [
        ('gImage_1', 'image1.bmp'),
        ('gImage_2', 'image2.bmp'),
        ('gImage_3', 'image3.bmp')
    ]

    print("電子紙圖像陣列轉BMP工具")
    print("="*50)

    for array_name, output_file in arrays_to_convert:
        try:
            # 解析陣列資料
            byte_data = parse_cpp_array(cpp_file, array_name)

            # 轉換為BMP
            image = convert_array_to_bmp(byte_data, output_file, array_name)

            print(f"✓ {array_name} -> {output_file} 轉換完成")

        except Exception as e:
            print(f"✗ 轉換 {array_name} 時發生錯誤: {e}")

    print("\n轉換完成！")

    # 顯示色彩對照
    print("\n色彩對照:")
    print("0x00 (00) -> 黑色")
    print("0x01 (01) -> 白色")
    print("0x02 (10) -> 黃色")
    print("0x03 (11) -> 紅色")

if __name__ == '__main__':
    main()