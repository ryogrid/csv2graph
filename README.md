# csv2graph (Go Version)

A Go command-line tool that generates scatter plots from CSV files

![example.png](./example.png)

## Features

- Draw scatter plots from specified columns in CSV files
- Support for X-axis range specification, image size adjustment, and data thinning
- Automatic handling when CSV doesn't have X-axis values

## Requirements

- Go 1.16 or later
- External dependency: github.com/fogleman/gg

## Installation

```bash
# Install dependencies
go get github.com/fogleman/gg

# Build
go build -o csv2graph csv2graph.go

# Or run directly
go run csv2graph.go --data CSV_FILE_PATH --columns SERIES1,SERIES2 [options]
```

## Usage

```bash
csv2graph --data CSV_FILE_PATH --columns SERIES1,SERIES2 [options]
```

### Options

| Option     | Description                            | Default     | Example      |
|------------|----------------------------------------|-------------|--------------|
| --data     | Path to CSV file                       | Required    | ./data.csv   |
| --range    | Maximum X-axis value                   | Optional    | 100          |
| --columns  | Columns to plot (comma-separated)      | Required    | a,b,c        |
| --size     | Output image size (width x height)     | 768x512     | 800x600      |
| --skip     | Data thinning interval (plot every Nth)| 1           | 2            |
| --xdata    | When specified, CSV has X-axis values in first column | false (omitted) | --xdata |
| --out      | Output filename                        | scatter_plot.png | mygraph.png |
| --xscale   | Map X values to specified range        | Optional    | 0,100        |
| --title    | Graph title                            | "Scatter Plot from CSV" | "Temperature Data" |

## Examples

```bash
# Plot all data
csv2graph --data ./sample.csv --columns a,c,e --size 800x600 --skip 2 --xdata --out output.png

# Plot data up to a specific range
csv2graph --data ./sample.csv --range 50 --columns a,c,e --out output.png

# Map X-axis values to a specific range
csv2graph --data ./sample.csv --columns a,c,e --xscale 0,100 --out output.png

# Specify a custom title for the graph
csv2graph --data ./sample.csv --columns a,c,e --title "Monthly Temperature Data" --out temp_graph.png
```

## CSV File Example

This tool supports CSV files in the following format:

```csv
_,a,b,c,d
1,10,15,20,25
2,12,18,22,28
3,14,20,25,30
4,16,22,28,32
5,18,25,30,35
```

In this CSV file:
- The first column contains X-axis values (when `--xdata` is specified)
- Subsequent columns contain data series
- Values are comma-separated
- A header row is required

### CSV File Example Without X-axis Data

For files without X-axis data, you can use a CSV file in this format:

```csv
a,b,c,d
10,15,20,25
12,18,22,28
14,20,25,30
16,22,28,32
18,25,30,35
```

In this case, X-axis values will be automatically assigned as sequential numbers starting from 1 (when `--xdata` is not specified)

## License

Unilicense
