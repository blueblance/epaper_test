#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
電子紙垂直排列圖像轉換工具
專門處理 gImage_3 的 "data horizontal, byte vertical" 排列方式

解析度: 272x792 (垂直排列)
色彩格式: 2bit (4色: 黑、白、黃、紅)
資料排列: 資料水平，位元組垂直
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

# gImage_3 的規格 (垂直排列)
WIDTH_VERTICAL = 272   # 寬度
HEIGHT_VERTICAL = 792  # 高度
BYTES_PER_COLUMN = 198  # 272/4 = 68 bytes per column, 792/4 = 198 for height

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

def pixels_to_rgb_array_vertical(pixels, width, height):
    """
    將像素值陣列轉換為RGB圖像陣列 (垂直排列方式)

    垂直排列的特點:
    - 資料按照垂直列排列
    - 每列從上到下填充
    - 然後移到下一列
    """
    if len(pixels) != width * height:
        print(f"警告: 像素數量 {len(pixels)} 不符合預期的 {width * height}")
        # 截斷或補零
        if len(pixels) > width * height:
            pixels = pixels[:width * height]
        else:
            pixels.extend([0x01] * (width * height - len(pixels)))  # 補白色

    rgb_array = np.zeros((height, width, 3), dtype=np.uint8)

    # 垂直排列：按列優先填充
    for col in range(width):
        for row in range(height):
            pixel_index = col * height + row  # 垂直排列的索引計算
            if pixel_index < len(pixels):
                pixel_val = pixels[pixel_index]
                rgb_array[row, col] = COLORS.get(pixel_val, COLORS[0x01])  # 預設白色

    return rgb_array

def convert_vertical_image_to_bmp(byte_data, output_path):
    """
    將垂直排列的位元組陣列轉換為BMP圖檔
    """
    print(f"\n正在轉換垂直排列圖像為 BMP...")

    # 解碼像素
    pixels = decode_2bit_pixels(byte_data)
    print(f"解碼得到 {len(pixels)} 個像素")

    # 轉換為RGB陣列 (垂直排列)
    rgb_array = pixels_to_rgb_array_vertical(pixels, WIDTH_VERTICAL, HEIGHT_VERTICAL)

    # 創建PIL圖像
    image = Image.fromarray(rgb_array, 'RGB')

    # 由於這是垂直顯示模式，我們可能需要旋轉圖像以符合正常檢視
    # 先儲存原始方向
    image.save(output_path, 'BMP')
    print(f"已儲存原始垂直圖像: {output_path}")

    # 也儲存旋轉90度的版本以便檢視
    rotated_image = image.rotate(90, expand=True)
    rotated_path = output_path.replace('.bmp', '_rotated.bmp')
    rotated_image.save(rotated_path, 'BMP')
    print(f"已儲存旋轉後圖像: {rotated_path}")

    return image, rotated_image

def analyze_vertical_data_structure(byte_data):
    """
    分析垂直排列資料的結構
    """
    total_bytes = len(byte_data)
    expected_bytes = WIDTH_VERTICAL * HEIGHT_VERTICAL // 4

    print(f"\n垂直排列資料分析:")
    print(f"總位元組數: {total_bytes}")
    print(f"預期位元組數: {expected_bytes}")
    print(f"圖像尺寸: {WIDTH_VERTICAL} × {HEIGHT_VERTICAL}")
    print(f"每列位元組數: {HEIGHT_VERTICAL // 4}")
    print(f"總列數: {WIDTH_VERTICAL}")

def main():
    """
    主程式：轉換 gImage_3 垂直排列圖像
    """
    cpp_file = 'imagedata.cpp'
    array_name = 'gImage_3'
    output_file = 'image3_vertical.bmp'

    print("電子紙垂直排列圖像轉換工具")
    print("="*50)
    print("專門處理 gImage_3 的垂直排列格式")

    try:
        # 解析陣列資料
        byte_data = parse_cpp_array(cpp_file, array_name)

        # 分析資料結構
        analyze_vertical_data_structure(byte_data)

        # 轉換為BMP
        original_image, rotated_image = convert_vertical_image_to_bmp(byte_data, output_file)

        print(f"\n✓ {array_name} -> {output_file} 垂直轉換完成")

        # 分析顏色分布
        img_array = np.array(original_image)
        colors = {}
        for y in range(img_array.shape[0]):
            for x in range(img_array.shape[1]):
                pixel = tuple(img_array[y, x])
                colors[pixel] = colors.get(pixel, 0) + 1

        print(f"\n垂直排列圖像顏色分布:")
        total_pixels = img_array.shape[0] * img_array.shape[1]
        sorted_colors = sorted(colors.items(), key=lambda x: x[1], reverse=True)
        for color, count in sorted_colors:
            percentage = (count / total_pixels) * 100
            color_name = "未知"
            if color == (0, 0, 0): color_name = "黑色"
            elif color == (255, 255, 255): color_name = "白色"
            elif color == (255, 255, 0): color_name = "黃色"
            elif color == (255, 0, 0): color_name = "紅色"
            print(f"  {color_name} {color}: {count} 像素 ({percentage:.1f}%)")

    except Exception as e:
        print(f"✗ 轉換 {array_name} 時發生錯誤: {e}")

    print("\n轉換完成！")
    print("\n說明:")
    print("- image3_vertical.bmp: 原始垂直排列")
    print("- image3_vertical_rotated.bmp: 旋轉90度後的版本")

if __name__ == '__main__':
    main()