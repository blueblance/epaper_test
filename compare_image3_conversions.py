#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比較 image3 兩種轉換方式的結果
"""

from PIL import Image
import numpy as np

def analyze_image(file_path):
    """
    分析圖像的基本資訊
    """
    try:
        img = Image.open(file_path)

        print(f"\n檔案: {file_path}")
        print(f"尺寸: {img.size[0]} x {img.size[1]} 像素")

        # 統計顏色分布
        img_array = np.array(img)
        colors = {}

        for y in range(img.size[1]):
            for x in range(img.size[0]):
                pixel = img.getpixel((x, y))
                pixel_key = pixel
                colors[pixel_key] = colors.get(pixel_key, 0) + 1

        total_pixels = img.size[0] * img.size[1]
        print(f"總像素數: {total_pixels}")

        print("顏色分布:")
        sorted_colors = sorted(colors.items(), key=lambda x: x[1], reverse=True)
        for color, count in sorted_colors:
            percentage = (count / total_pixels) * 100
            color_name = "未知"
            if color == (0, 0, 0): color_name = "黑色"
            elif color == (255, 255, 255): color_name = "白色"
            elif color == (255, 255, 0): color_name = "黃色"
            elif color == (255, 0, 0): color_name = "紅色"
            print(f"  {color_name}: {count} 像素 ({percentage:.1f}%)")

        return img, colors

    except Exception as e:
        print(f"分析 {file_path} 時發生錯誤: {e}")
        return None, None

def create_comparison_image(img1, img2, output_path):
    """
    創建比較圖像，左右並排顯示兩個圖像
    """
    try:
        # 調整尺寸使其相同高度
        height = min(img1.size[1], img2.size[1])

        # 按比例調整寬度
        width1 = int(img1.size[0] * height / img1.size[1])
        width2 = int(img2.size[0] * height / img2.size[1])

        img1_resized = img1.resize((width1, height), Image.NEAREST)
        img2_resized = img2.resize((width2, height), Image.NEAREST)

        # 創建新的合併圖像
        combined_width = width1 + width2 + 10  # 中間留10像素間隔
        combined_img = Image.new('RGB', (combined_width, height), (128, 128, 128))

        # 貼上兩個圖像
        combined_img.paste(img1_resized, (0, 0))
        combined_img.paste(img2_resized, (width1 + 10, 0))

        # 儲存比較圖像
        combined_img.save(output_path, 'BMP')
        print(f"已儲存比較圖像: {output_path}")

        return combined_img

    except Exception as e:
        print(f"創建比較圖像時發生錯誤: {e}")
        return None

def main():
    """
    主程式：比較 image3 的不同轉換結果
    """
    print("Image3 轉換結果比較工具")
    print("="*60)

    # 分析三個版本的 image3
    files_to_compare = [
        ('image3.bmp', '原始水平掃描轉換'),
        ('image3_vertical.bmp', '垂直排列轉換'),
        ('image3_vertical_rotated.bmp', '垂直排列轉換（旋轉90度）')
    ]

    images = []

    for file_path, description in files_to_compare:
        print(f"\n{'='*20} {description} {'='*20}")
        img, colors = analyze_image(file_path)
        if img:
            images.append((file_path, description, img, colors))

    print(f"\n{'='*60}")
    print("總結比較:")

    if len(images) >= 2:
        # 比較色彩分布的差異
        original_colors = images[0][3] if len(images) > 0 else {}
        vertical_colors = images[1][3] if len(images) > 1 else {}

        print(f"\n色彩分布比較:")
        print(f"{'顏色':<8} {'原始轉換':<12} {'垂直轉換':<12} {'差異':<10}")
        print("-" * 50)

        all_colors = set(original_colors.keys()) | set(vertical_colors.keys())
        for color in sorted(all_colors):
            color_name = "未知"
            if color == (0, 0, 0): color_name = "黑色"
            elif color == (255, 255, 255): color_name = "白色"
            elif color == (255, 255, 0): color_name = "黃色"
            elif color == (255, 0, 0): color_name = "紅色"

            orig_count = original_colors.get(color, 0)
            vert_count = vertical_colors.get(color, 0)
            diff = abs(orig_count - vert_count)

            print(f"{color_name:<8} {orig_count:<12} {vert_count:<12} {diff:<10}")

        # 創建比較圖像
        if len(images) >= 2:
            create_comparison_image(
                images[0][2], images[1][2],
                'image3_comparison_horizontal_vs_vertical.bmp'
            )

        if len(images) >= 3:
            create_comparison_image(
                images[0][2], images[2][2],
                'image3_comparison_horizontal_vs_rotated.bmp'
            )

    print(f"\n分析完成！")
    print(f"根據顏色分布和視覺檢查，您可以判斷哪種轉換方式更正確。")

if __name__ == '__main__':
    main()