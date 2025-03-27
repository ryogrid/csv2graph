import argparse
import pandas as pd
import matplotlib.pyplot as plt

# Usage example:
# python csv2graph.py --data ./hoge.csv --range 2 --columns a,c,e --out mygraph.png

def parse_args():
    parser = argparse.ArgumentParser(description="CSVから散布図を生成する")
    parser.add_argument('--data', required=True, help="CSVファイルのパス")
    parser.add_argument('--range', type=float, required=True, help="X軸の最大値（この値以下をプロットする）")
    parser.add_argument('--columns', required=True, help="描画対象の系列をカンマ区切りで指定する")
    parser.add_argument('--size', default="768x512", help="出力画像のサイズをWIDTHxHEIGHTの形式で指定する（デフォルトは768x512）")
    parser.add_argument('--skip', type=int, default=1, help="データの間引き間隔（N個ごとの最初の要素のみを使用、デフォルトは1）")
    parser.add_argument('--xdata', type=lambda x: (str(x).lower() == 'true'), default=False,
                        help="X軸の値がCSVに含まれているかどうかを真理値で指定（trueまたはfalse、デフォルトはfalse）")
    parser.add_argument('--out', default="scatter_plot.png", help="出力画像ファイル名（デフォルトはscatter_plot.png）")
    return parser.parse_args()


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
    df_filtered = df[df[x_col] <= args.range]

    # データを間引き
    df_filtered = df_filtered.iloc[::args.skip, :]

    # 画像サイズを設定
    width, height = map(int, args.size.split('x'))
    plt.figure(figsize=(width / 100, height / 100), dpi=100)

    for col in columns_to_plot:
        if col in df_filtered.columns:
            plt.scatter(df_filtered[x_col], df_filtered[col], label=col)
        else:
            print(f"Warning: Column '{col}' not found in CSV.")

    plt.xlabel(x_col)
    plt.ylabel('Value')
    plt.title('Scatter Plot from CSV')
    plt.grid(True)
    plt.legend()

    # 出力画像ファイル名を生成
    output_image = args.out
    plt.savefig(output_image)
    print(f"Graph saved to {output_image}")


if __name__ == "__main__":
    main()
