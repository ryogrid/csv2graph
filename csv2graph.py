import argparse
import pandas as pd
from PIL import Image, ImageDraw
import colorsys
import math

# Usage example:
# python csv2graph.py --data ./hoge.csv --range 2 --columns a,c,e --out mygraph.png

def parse_args():
    parser = argparse.ArgumentParser(description="CSVから散布図を生成する")
    parser.add_argument('--data', required=True, help="CSVファイルのパス")
    parser.add_argument('--range', type=float, help="X軸の最大値（この値以下をプロットする）。指定しない場合は全データをプロット")
    parser.add_argument('--columns', required=True, help="描画対象の系列をカンマ区切りで指定する")
    parser.add_argument('--size', default="768x512", help="出力画像のサイズをWIDTHxHEIGHTの形式で指定する（デフォルトは768x512）")
    parser.add_argument('--skip', type=int, default=1, help="データの間引き間隔（N個ごとの最初の要素のみを使用、デフォルトは1）")
    parser.add_argument('--xdata', type=lambda x: (str(x).lower() == 'true'), default=False,
                        help="X軸の値がCSVに含まれているかどうかを真理値で指定（trueまたはfalse、デフォルトはfalse）")
    parser.add_argument('--out', default="scatter_plot.png", help="出力画像ファイル名（デフォルトはscatter_plot.png）")
    return parser.parse_args()

def generate_colors(n):
    colors = []
    for i in range(n):
        hue = i / n
        saturation = 0.7
        value = 0.9
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        colors.append(tuple(int(x * 255) for x in rgb))
    return colors

def draw_grid(draw, width, height, margin):
    # グリッド線の描画
    grid_color = (200, 200, 200)
    for x in range(margin, width - margin, 50):
        draw.line([(x, margin), (x, height - margin)], fill=grid_color, width=1)
    for y in range(margin, height - margin, 50):
        draw.line([(margin, y), (width - margin, y)], fill=grid_color, width=1)

def draw_axes(draw, width, height, margin, x_max, y_min, y_max):
    # 軸の描画
    axis_color = (0, 0, 0)
    # X軸
    draw.line([(margin, height - margin), (width - margin, height - margin)], fill=axis_color, width=2)
    # Y軸
    draw.line([(margin, margin), (margin, height - margin)], fill=axis_color, width=2)
    
    # X軸の目盛り間隔を計算
    # 利用可能な幅を計算（ピクセル単位）
    available_width = width - 2 * margin
    # 1つの数字の表示に必要な幅（ピクセル単位）
    digit_width = 20  # 数字1文字あたりの推定幅
    # 目盛り間の最小間隔（ピクセル単位）
    min_tick_spacing = 50  # 目盛り間の最小間隔
    # 利用可能な目盛りの数を計算
    max_ticks = min(
        int(available_width / min_tick_spacing),  # 最小間隔に基づく最大数
        int(available_width / (digit_width * 3))  # 数字の表示幅に基づく最大数
    )
    # 目盛りの間隔を計算
    x_step = max(1, int(x_max / max_ticks))
    
    # 目盛りの描画
    for x in range(0, int(x_max) + 1, x_step):
        x_pos = margin + (x / x_max) * (width - 2 * margin)
        draw.line([(x_pos, height - margin - 5), (x_pos, height - margin + 5)], fill=axis_color, width=1)
        draw.text((x_pos - 10, height - margin + 10), str(x), fill=axis_color)
    
    y_step = (y_max - y_min) / 5
    for i in range(6):
        y = y_min + i * y_step
        y_pos = height - margin - (i / 5) * (height - 2 * margin)
        draw.line([(margin - 5, y_pos), (margin + 5, y_pos)], fill=axis_color, width=1)
        draw.text((margin - 30, y_pos - 5), f"{y:.1f}", fill=axis_color)

def main():
    args = parse_args()

    # CSVファイル読み込み
    df = pd.read_csv(args.data)

    # X軸データが存在しない場合の処理
    if not args.xdata:
        df.insert(0, '_', range(1, len(df) + 1))

    # プロットする系列を取得
    columns_to_plot = args.columns.split(',')

    # X軸の列を特定（CSVの1列目）
    x_col = df.columns[0]

    # X軸の範囲でデータをフィルタリング
    if args.range is not None:
        df_filtered = df[df[x_col] <= args.range]
        x_max = args.range
    else:
        df_filtered = df
        x_max = df_filtered[x_col].max()

    # データを間引き
    df_filtered = df_filtered.iloc[::args.skip, :]

    # 画像サイズを設定
    width, height = map(int, args.size.split('x'))
    margin = 60  # グラフの余白

    # 新しい画像を作成
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    # グリッドの描画
    draw_grid(draw, width, height, margin)

    # Y軸の範囲を計算
    y_min = float('inf')
    y_max = float('-inf')
    for col in columns_to_plot:
        if col in df_filtered.columns:
            y_min = min(y_min, df_filtered[col].min())
            y_max = max(y_max, df_filtered[col].max())

    # 軸の描画
    draw_axes(draw, width, height, margin, x_max, y_min, y_max)

    # 散布図の描画
    colors = generate_colors(len(columns_to_plot))
    for i, col in enumerate(columns_to_plot):
        if col in df_filtered.columns:
            color = colors[i]
            # データをx軸の値でソート
            sorted_data = df_filtered.sort_values(by=x_col)
            points = []
            
            # 点の描画と直線のための点の座標を収集
            for _, row in sorted_data.iterrows():
                x = row[x_col]
                y = row[col]
                x_pos = margin + (x / x_max) * (width - 2 * margin)
                y_pos = height - margin - ((y - y_min) / (y_max - y_min)) * (height - 2 * margin)
                points.append((x_pos, y_pos))
                draw.ellipse([(x_pos - 2, y_pos - 2), (x_pos + 2, y_pos + 2)], fill=color)
            
            # 点を直線で結ぶ
            if len(points) > 1:
                for j in range(len(points) - 1):
                    draw.line([points[j], points[j + 1]], fill=color, width=1)

    # 凡例の描画
    legend_y = margin
    for i, col in enumerate(columns_to_plot):
        if col in df_filtered.columns:
            color = colors[i]
            draw.rectangle([(width - 150, legend_y), (width - 140, legend_y + 10)], fill=color)
            draw.text((width - 130, legend_y), col, fill=(0, 0, 0))
            legend_y += 20

    # タイトルの描画
    draw.text((width // 2 - 100, 20), 'Scatter Plot from CSV', fill=(0, 0, 0))

    # 出力画像ファイル名を生成
    output_image = args.out
    image.save(output_image)
    print(f"Graph saved to {output_image}")

if __name__ == "__main__":
    main()
