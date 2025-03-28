# csv2graph

CSVファイルから簡単に散布図を生成するPython製のコマンドラインツールです。

## 機能

- CSVファイルから指定した列を用いて散布図を作成します。
- X軸の範囲指定、画像サイズの指定、データの間引きが可能です。
- X軸の値がCSV内に存在しない場合でも、自動で番号を振って対応します。

## 必要な環境

- Python 3.x

## 必要なライブラリ

以下のコマンドで必要なライブラリをインストールできます。

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python csv2graph.py --data CSVファイルパス --range X軸最大値 --columns 系列1,系列2 [オプション]
```

### オプション

| オプション  | 説明                             | デフォルト値   | 指定例          |
|-------------|---------------------------------|---------------|-----------------|
| --data      | CSVファイルのパス                | 必須          | ./data.csv     |
| --range     | X軸の最大値                      | 必須          | 100             |
| --columns   | 描画対象の系列をカンマ区切りで指定 | 必須          | a,b,c           |
| --size      | 出力画像サイズ（WIDTHxHEIGHT）   | 768x512       | 800x600         |
| --skip      | データの間引き間隔（N個ごと）     | 1             | 2               |
| --xdata     | CSVにX軸データが含まれるか（true/false） | false | true            |
| --out       | 出力画像ファイル名               | scatter_plot.png | mygraph.png |

## 使用例

```bash
python csv2graph.py --data ./sample.csv --range 50 --columns a,c,e --size 800x600 --skip 2 --xdata true --out output.png
```

## ライセンス

Unilicense

