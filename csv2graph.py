import argparse
import pandas as pd
from PIL import Image, ImageDraw
import colorsys
import math

# Usage example:
# python csv2graph.py --data ./hoge.csv --range 2 --columns a,c,e --out mygraph.png

def parse_args():
    parser = argparse.ArgumentParser(description="Generate scatter plot from CSV")
    parser.add_argument('--data', required=True, help="Path to CSV file")
    parser.add_argument('--range', type=float, help="Maximum value for X-axis (plot values less than or equal to this). If not specified, all data will be plotted")
    parser.add_argument('--columns', required=True, help="Comma-separated list of columns to plot")
    parser.add_argument('--size', default="768x512", help="Output image size in WIDTHxHEIGHT format (default is 768x512)")
    parser.add_argument('--skip', type=int, default=1, help="Data thinning interval (use only every Nth element, default is 1)")
    parser.add_argument('--xdata', type=lambda x: (str(x).lower() == 'true'), default=False,
                        help="Boolean indicating whether X-axis values are included in CSV (true or false, default is false)")
    parser.add_argument('--out', default="scatter_plot.png", help="Output image filename (default is scatter_plot.png)")
    parser.add_argument('--xscale', help="Map X-axis values to specified range (START,END format)")
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

def draw_grid(draw, width, height, margin, x_ticks, y_ticks):
    # Draw grid lines
    grid_color = (200, 200, 200)
    
    # X-axis grid lines (vertical lines)
    for x_pos in x_ticks:
        draw.line([(x_pos, margin), (x_pos, height - margin)], fill=grid_color, width=1)
    
    # Y-axis grid lines (horizontal lines)
    for y_pos in y_ticks:
        draw.line([(margin, y_pos), (width - margin, y_pos)], fill=grid_color, width=1)

def draw_axes(draw, width, height, margin, x_max, y_min, y_max, start):
    # Draw axes
    axis_color = (0, 0, 0)
    # X-axis
    draw.line([(margin, height - margin), (width - margin, height - margin)], fill=axis_color, width=2)
    # Y-axis
    draw.line([(margin, margin), (margin, height - margin)], fill=axis_color, width=2)
    
    # Calculate X-axis tick intervals
    available_width = width - 2 * margin
    digit_width = 20  # Estimated width per digit in pixels
    min_tick_spacing = 50  # Minimum spacing between ticks
    max_ticks = min(
        int(available_width / min_tick_spacing),
        int(available_width / (digit_width * 3))
    )
    x_step = max(1, int((x_max - start) / max_ticks))  # Calculate step considering start value
    
    # Calculate X-axis tick positions
    x_tick_positions = []
    x_tick_values = []
    
    for x in range(int(start), int(x_max) + 1, x_step):
        x_pos = margin + ((x - start) / (x_max - start)) * (width - 2 * margin)
        x_tick_positions.append(x_pos)
        x_tick_values.append(x)
    
    # Draw X-axis ticks
    for i, x_pos in enumerate(x_tick_positions):
        x = x_tick_values[i]
        draw.line([(x_pos, height - margin - 5), (x_pos, height - margin + 5)], fill=axis_color, width=1)
        draw.text((x_pos - 10, height - margin + 10), str(x), fill=axis_color)
    
    # Calculate Y-axis tick intervals and positions
    y_step = (y_max - y_min) / 5
    y_tick_positions = []
    
    for i in range(6):
        y = y_min + i * y_step
        y_pos = height - margin - (i / 5) * (height - 2 * margin)
        y_tick_positions.append(y_pos)
        draw.line([(margin - 5, y_pos), (margin + 5, y_pos)], fill=axis_color, width=1)
        draw.text((margin - 30, y_pos - 5), f"{y:.1f}", fill=axis_color)
    
    return x_tick_positions, y_tick_positions

def main():
    args = parse_args()

    # Load CSV file
    df = pd.read_csv(args.data)

    # Handle case where X-axis data doesn't exist
    if not args.xdata:
        df.insert(0, '_', range(1, len(df) + 1))

    # Get columns to plot
    columns_to_plot = args.columns.split(',')

    # Identify X-axis column (first column in CSV)
    x_col = df.columns[0]

    # Filter data by X-axis range
    if args.range is not None:
        df_filtered = df[df[x_col] <= args.range]
        x_max = args.range
    else:
        df_filtered = df
        x_max = df_filtered[x_col].max()

    # X-axis value range mapping
    start = 0
    end = x_max
    if args.xscale:
        start, end = map(float, args.xscale.split(','))
        # Set X-axis maximum to end
        x_max = end
        # Map values from start to end
        df_filtered[x_col] = start + (df_filtered[x_col] / df_filtered[x_col].max()) * (end - start)

    # Thin out data
    df_filtered = df_filtered.iloc[::args.skip, :]

    # Set image size
    width, height = map(int, args.size.split('x'))
    margin = 60  # Graph margin

    # Create new image
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    # Calculate Y-axis range
    y_min = float('inf')
    y_max = float('-inf')
    for col in columns_to_plot:
        if col in df_filtered.columns:
            y_min = min(y_min, df_filtered[col].min())
            y_max = max(y_max, df_filtered[col].max())

    # Draw axes and get tick positions
    x_ticks, y_ticks = draw_axes(draw, width, height, margin, x_max, y_min, y_max, start)

    # Draw grid - aligned with X-axis ticks
    draw_grid(draw, width, height, margin, x_ticks, y_ticks)

    # Draw scatter plot
    colors = generate_colors(len(columns_to_plot))
    for i, col in enumerate(columns_to_plot):
        if col in df_filtered.columns:
            color = colors[i]
            # Sort data by X-axis value
            sorted_data = df_filtered.sort_values(by=x_col)
            points = []
            
            # Draw points and collect coordinates for lines
            for _, row in sorted_data.iterrows():
                x = row[x_col]
                y = row[col]
                # Map X-axis values
                x_pos = margin + (x - start) / (end - start) * (width - 2 * margin)
                y_pos = height - margin - ((y - y_min) / (y_max - y_min)) * (height - 2 * margin)
                points.append((x_pos, y_pos))
                draw.ellipse([(x_pos - 2, y_pos - 2), (x_pos + 2, y_pos + 2)], fill=color)
            
            # Connect points with lines
            if len(points) > 1:
                for j in range(len(points) - 1):
                    draw.line([points[j], points[j + 1]], fill=color, width=1)

    # Position legend outside the graph area (top-right)
    legend_padding = 10  # Internal padding for legend
    legend_box_size = 10
    legend_text_offset = 15
    legend_spacing = 20
    
    # Calculate legend width dynamically (based on column name length)
    valid_columns = [col for col in columns_to_plot if col in df_filtered.columns]
    max_column_length = max([len(col) for col in valid_columns], default=0)
    char_width = 7  # Estimated width per character (pixels)
    text_width = max_column_length * char_width
    legend_width = legend_box_size + legend_text_offset + text_width + 2 * legend_padding
    
    # Calculate legend height
    legend_height = len(valid_columns) * legend_spacing + 2 * legend_padding
    
    # Position legend outside graph area (top-right)
    legend_left = width - margin + 10  # Right edge of graph area + 10px margin
    legend_top = margin  # Same height as top of graph area
    
    # Adjust to prevent exceeding right edge of image
    if legend_left + legend_width > width:
        legend_left = width - legend_width - 5  # 5px margin from edge
    
    # Draw legend background
    draw.rectangle(
        [(legend_left, legend_top), (legend_left + legend_width, legend_top + legend_height)],
        fill=(255, 255, 255),  # Background color
        outline=(100, 100, 100)
    )
    
    # Draw legend items
    legend_y_current = legend_top + legend_padding
    for i, col in enumerate(valid_columns):
        color = colors[i]
        draw.rectangle(
            [(legend_left + legend_padding, legend_y_current), 
             (legend_left + legend_padding + legend_box_size, legend_y_current + legend_box_size)],
            fill=color
        )
        draw.text(
            (legend_left + legend_padding + legend_text_offset, legend_y_current), 
            col, 
            fill=(0, 0, 0)
        )
        legend_y_current += legend_spacing

    # Draw title
    draw.text((width // 2 - 100, 20), 'Scatter Plot from CSV', fill=(0, 0, 0))

    # Generate output image file
    output_image = args.out
    image.save(output_image)
    print(f"Graph saved to {output_image}")

if __name__ == "__main__":
    main()