#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BMP 圖像檢視工具
"""

from PIL import Image
import numpy as np

def analyze_bmp(file_path):
    """
    分析 BMP 圖像的基本資訊
    """
    try:
        img = Image.open(file_path)

        print(f"\n檔案: {file_path}")
        print(f"格式: {img.format}")
        print(f"模式: {img.mode}")
        print(f"尺寸: {img.size[0]} x {img.size[1]} 像素")

        # 轉換為numpy陣列分析像素分布
        img_array = np.array(img)

        # 統計顏色分布
        if img.mode == 'RGB':
            # 計算每個顏色的像素數量
            colors = {}
            for y in range(img.size[1]):
                for x in range(img.size[0]):
                    pixel = img.getpixel((x, y))
                    pixel_key = f"RGB{pixel}"
                    colors[pixel_key] = colors.get(pixel_key, 0) + 1

            print("顏色分布:")
            sorted_colors = sorted(colors.items(), key=lambda x: x[1], reverse=True)
            for color, count in sorted_colors[:10]:  # 顯示前10種顏色
                percentage = (count / (img.size[0] * img.size[1])) * 100
                print(f"  {color}: {count} 像素 ({percentage:.1f}%)")

        return img

    except Exception as e:
        print(f"分析 {file_path} 時發生錯誤: {e}")
        return None

def main():
    """
    分析生成的BMP檔案
    """
    print("電子紙 BMP 圖像分析工具")
    print("="*50)

    bmp_files = ['image1.bmp', 'image2.bmp', 'image3.bmp']

    images = []
    for bmp_file in bmp_files:
        img = analyze_bmp(bmp_file)
        if img:
            images.append((bmp_file, img))

    print(f"\n成功分析了 {len(images)} 個圖像檔案")

    # 檢查是否有非白色像素 (表示有實際內容)
    for file_name, img in images:
        img_array = np.array(img)
        white_pixels = np.sum(np.all(img_array == [255, 255, 255], axis=2))
        total_pixels = img_array.shape[0] * img_array.shape[1]
        content_pixels = total_pixels - white_pixels

        print(f"\n{file_name} 內容分析:")
        print(f"  總像素: {total_pixels}")
        print(f"  白色像素: {white_pixels}")
        print(f"  有內容像素: {content_pixels}")
        print(f"  內容比例: {(content_pixels/total_pixels)*100:.2f}%")

if __name__ == '__main__':
    main()