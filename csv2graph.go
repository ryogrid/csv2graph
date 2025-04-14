package main

import (
	"encoding/csv"
	"flag"
	"fmt"
	"image/color"
	"math"
	"os"
	"strconv"
	"strings"

	"github.com/fogleman/gg"
)

func main() {
	// Parse command line arguments
	dataPath := flag.String("data", "", "Path to CSV file")
	maxRange := flag.Float64("range", -1, "Max X value, plot points <= this (optional)")
	columns := flag.String("columns", "", "Comma-separated columns to plot")
	size := flag.String("size", "768x512", "Output image size (e.g. 768x512)")
	skip := flag.Int("skip", 1, "Data thinning (plot every Nth point, default=1)")
	xdata := flag.Bool("xdata", false, "When specified, CSV has X-axis values in first column")
	out := flag.String("out", "scatter_plot.png", "Output image filename")
	xscale := flag.String("xscale", "", "Map X values to range START,END")
	title := flag.String("title", "Scatter Plot from CSV", "Graph title")
	flag.Parse()

	if *dataPath == "" || *columns == "" {
		fmt.Println("Usage: csv2graph --data <FILE> --columns <COLS> [options]")
		return
	}

	colsToPlot := strings.Split(*columns, ",")

	// Open CSV file
	f, err := os.Open(*dataPath)
	if err != nil {
		fmt.Println("CSV open error:", err)
		return
	}
	defer f.Close()

	csvReader := csv.NewReader(f)
	records, err := csvReader.ReadAll()
	if err != nil {
		fmt.Println("CSV read error:", err)
		return
	}
	if len(records) < 2 {
		fmt.Println("No data to plot")
		return
	}

	// Parse header and data rows
	header := records[0]
	dataRows := records[1:]

	// Generate X column if xdata=false
	var xIndex int
	if !*xdata {
		// Insert X column
		header = append([]string{"_"}, header...)
		for i := 0; i < len(dataRows); i++ {
			dataRows[i] = append([]string{strconv.Itoa(i + 1)}, dataRows[i]...)
		}
	}
	xIndex = 0

	// Map column names to indexes
	colIndexMap := make(map[string]int)
	for i, h := range header {
		colIndexMap[h] = i
	}

	// Filter data by range
	var filtered [][]string
	if *maxRange > 0 {
		for _, row := range dataRows {
			xVal, err := strconv.ParseFloat(row[xIndex], 64)
			if err == nil && xVal <= *maxRange {
				filtered = append(filtered, row)
			}
		}
	} else {
		filtered = dataRows
	}

	// Get original data range
	origXMin, origXMax := math.Inf(1), math.Inf(-1)
	if len(filtered) > 0 {
		for _, row := range filtered {
			xVal, err := strconv.ParseFloat(row[xIndex], 64)
			if err == nil {
				if xVal < origXMin {
					origXMin = xVal
				}
				if xVal > origXMax {
					origXMax = xVal
				}
			}
		}
	}

	// Determine plot display range
	plotXMin, plotXMax := origXMin, origXMax
	if *xscale != "" {
		parts := strings.Split(*xscale, ",")
		if len(parts) == 2 {
			s, errS := strconv.ParseFloat(parts[0], 64)
			e, errE := strconv.ParseFloat(parts[1], 64)
			if errS == nil && errE == nil && e > s {
				plotXMin, plotXMax = s, e
			}
		}
	}

	// Data thinning
	thinned := [][]string{}
	for i := 0; i < len(filtered); i += *skip {
		thinned = append(thinned, filtered[i])
	}

	// Parse image size
	wh := strings.Split(*size, "x")
	w, _ := strconv.Atoi(wh[0])
	h, _ := strconv.Atoi(wh[1])

	// Prepare drawing context
	dc := gg.NewContext(w, h)
	dc.SetColor(color.White)
	dc.Clear()

	// Find Y-axis min, max values
	yMin, yMax := math.Inf(1), math.Inf(-1)
	for _, c := range colsToPlot {
		idx, ok := colIndexMap[c]
		if !ok {
			continue
		}
		for _, row := range thinned {
			val, err := strconv.ParseFloat(row[idx], 64)
			if err == nil {
				if val < yMin {
					yMin = val
				}
				if val > yMax {
					yMax = val
				}
			}
		}
	}
	if yMin == math.Inf(1) || yMax == math.Inf(-1) {
		fmt.Println("No valid data for plotting")
		return
	}

	// Margin and usable area
	margin := 60.0
	usableW := float64(w) - 2*margin
	usableH := float64(h) - 2*margin

	// Draw axes
	dc.SetColor(color.Black)
	dc.SetLineWidth(2)
	// X-axis
	dc.DrawLine(margin, float64(h)-margin, float64(w)-margin, float64(h)-margin)
	dc.Stroke()
	// Y-axis
	dc.DrawLine(margin, margin, margin, float64(h)-margin)
	dc.Stroke()

	// X-axis numeric labels
	xTickSteps := 5
	for i := 0; i <= xTickSteps; i++ {
		// Calculate label value
		labelVal := plotXMin + (float64(i)/float64(xTickSteps))*(plotXMax-plotXMin)
		// Calculate label position
		tx := margin + (float64(i)/float64(xTickSteps))*usableW
		dc.SetColor(color.Black)
		dc.DrawStringAnchored(fmt.Sprintf("%.1f", labelVal), tx, float64(h)-margin+15, 0.5, 0)
	}

	// Y-axis numeric labels
	yTickSteps := 5
	for i := 0; i <= yTickSteps; i++ {
		labelVal := yMin + (float64(i)/float64(yTickSteps))*(yMax-yMin)
		ty := float64(h) - margin - (float64(i)/float64(yTickSteps))*usableH
		dc.SetColor(color.Black)
		dc.DrawStringAnchored(fmt.Sprintf("%.1f", labelVal), margin-10, ty, 1, 0.5)
	}

	// Draw grid
	for i := 0; i <= xTickSteps; i++ {
		// X-axis grid
		tx := margin + (float64(i)/float64(xTickSteps))*usableW
		dc.SetColor(color.RGBA{200, 200, 200, 255})
		dc.DrawLine(tx, margin, tx, float64(h)-margin)
		dc.Stroke()
	}

	for i := 0; i <= yTickSteps; i++ {
		// Y-axis grid
		ty := float64(h) - margin - (float64(i)/float64(yTickSteps))*usableH
		dc.SetColor(color.RGBA{200, 200, 200, 255})
		dc.DrawLine(margin, ty, float64(w)-margin, ty)
		dc.Stroke()
	}

	// Plot each column
	colors := generateColors(len(colsToPlot))
	for cidx, c := range colsToPlot {
		idx, ok := colIndexMap[c]
		if !ok {
			continue
		}
		points := make([][2]float64, 0)
		for _, row := range thinned {
			xval, err1 := strconv.ParseFloat(row[xIndex], 64)
			yval, err2 := strconv.ParseFloat(row[idx], 64)
			if err1 == nil && err2 == nil {
				// Normalize X value if xscale is specified
				normalizedX := xval
				if *xscale != "" {
					// Scale the original X value to match the specified range
					// Original: [origXMin, origXMax] -> Target: [plotXMin, plotXMax]
					normalizedX = plotXMin + ((xval-origXMin)/(origXMax-origXMin))*(plotXMax-plotXMin)
				}

				// Calculate screen coordinates using normalized X
				xx := margin + ((normalizedX-plotXMin)/(plotXMax-plotXMin))*usableW

				// Y value mapping: data range -> screen coordinates
				yy := float64(h) - margin - ((yval-yMin)/(yMax-yMin))*usableH

				// Plot only data within display area
				if xx >= margin && xx <= float64(w)-margin {
					points = append(points, [2]float64{xx, yy})
				}
			}
		}

		dc.SetColor(colors[cidx])
		dc.SetLineWidth(1) // Set thin line width
		for i, p := range points {
			// Draw point
			dc.DrawCircle(p[0], p[1], 2)
			dc.Fill()
			// Draw line (from second point)
			if i > 0 {
				dc.DrawLine(points[i-1][0], points[i-1][1], p[0], p[1])
				dc.Stroke()
			}
		}
	}

	// Draw legend
	legendX := float64(w) - margin + 10
	legendY := margin
	boxSize := 10.0
	spacing := 20.0
	dc.SetColor(color.White)
	lw := 100.0
	lh := float64(len(colsToPlot))*spacing + 20
	dc.DrawRectangle(legendX, legendY, lw, lh)
	dc.Fill()
	dc.SetColor(color.Black)
	dc.DrawRectangle(legendX, legendY, lw, lh)
	dc.Stroke()

	yy := legendY + 10
	for i, c := range colsToPlot {
		dc.SetColor(colors[i])
		dc.DrawRectangle(legendX+10, yy, boxSize, boxSize)
		dc.Fill()
		dc.SetColor(color.Black)
		dc.DrawStringAnchored(c, legendX+30, yy+boxSize/2, 0, 0.5)
		yy += spacing
	}

	// Title
	dc.SetColor(color.Black)
	dc.DrawStringAnchored(*title, float64(w)/2, 20, 0.5, 0.5)

	// Save
	outF, err := os.Create(*out)
	if err != nil {
		fmt.Println("Create file error:", err)
		return
	}
	defer outF.Close()
	dc.EncodePNG(outF)
	fmt.Println("Saved:", *out)
}

func generateColors(n int) []color.Color {
	var cols []color.Color
	for i := 0; i < n; i++ {
		// HSV -> RGB
		h := float64(i) / float64(n)
		s := 0.7
		v := 0.9
		r, g, b := hsv2rgb(h, s, v)
		cols = append(cols, color.RGBA{uint8(r * 255), uint8(g * 255), uint8(b * 255), 255})
	}
	return cols
}

func hsv2rgb(h, s, v float64) (float64, float64, float64) {
	var r, g, b float64
	i := math.Floor(h * 6)
	f := h*6 - i
	p := v * (1 - s)
	q := v * (1 - f*s)
	t := v * (1 - (1-f)*s)
	switch int(i) % 6 {
	case 0:
		r, g, b = v, t, p
	case 1:
		r, g, b = q, v, p
	case 2:
		r, g, b = p, v, t
	case 3:
		r, g, b = p, q, v
	case 4:
		r, g, b = t, p, v
	case 5:
		r, g, b = v, p, q
	}
	return r, g, b
}
