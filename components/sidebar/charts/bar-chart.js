import { Box } from 'theme-ui'
import { AxisLabel, Chart, Grid, Plot, Ticks, TickLabels } from '@carbonplan/charts'
import Bar from './bar'
import * as d3 from 'd3'

const BarChart = ({ variable, regionData, colormap, showRegionPicker }) => {

    const sx = {
        chart: {
            mt: [4],
            mx: 'auto',
            pl: [0, 4, 5, 6],
            pr: [0, 1, 1, 1,],
            width: '100%',
            height: '200px',
        }
    }

    const min = 0.0
    const max = 1.0
    const variableRange = [min, max]
    let graphData = []
    const placeHolderData = [
        [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    if (!regionData.value || !regionData.value[variable]) { // ex: if(!'drought' or Object["drought"]) {...}
        return
    }

    regionData.value[variable].forEach(function (element, idx) {
        if (element !== 9.969209968386869e36) {
            if (element > max) {
                graphData.push(max);
            } else if (element < min) {
                graphData.push(min);
            } else {
                graphData.push(element);
            }
        }
    });
    let dataCount = graphData.length

    // bin the data
    const nBins = 10;
    const range = max - min;
    const binWidth = range / nBins;
    let binEdges = Array(nBins + 1).fill(0).map((_, i) => Number((i * binWidth).toFixed(2)))
    const bin = d3.bin().domain(variableRange).thresholds(binEdges)
    const bins = bin(graphData)

    let percentages;
    const initialValue = 0;
    // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/reduce
    let checkEmptyArrays = bins.reduce((total, arr) => total + arr.length, initialValue);
    if (checkEmptyArrays == 0) { // then there is no data to display
        percentages = Array(nBins + 1).fill(0)
    } else {
        percentages = bins.map(arr => {
            return Number(((arr.length / dataCount) * 100).toFixed(0))
        })
    }

    // https://stackoverflow.com/questions/22015684/zip-arrays-in-javascript
    const zip = (x, y) => Array.from(Array(x.length), (_, i) => [x[i], y[i]]);
    let plotData = zip(binEdges.map((edge) => edge * 100), percentages);
    const xMin = (min - binWidth) * 100;
    const xMax = (max + binWidth) * 100;

    return (
        <Box sx={{ ...sx.chart }} className='chart-container'>
            <Chart x={[xMin, xMax]} y={[0, 100]} padding={{ left: 50, top: 0 }} >
                <Grid vertical horizontal />
                <Ticks left bottom />
                <TickLabels left bottom />
                <AxisLabel left >Percent</AxisLabel>
                <AxisLabel bottom>Percentile</AxisLabel>
                <Plot>
                    <Bar
                        data={plotData}
                        color={plotData.map((_, i) => colormap[i])}
                        strokeWidth={0.5}
                    />
                </Plot>
            </Chart>
        </Box>
    )
}

export default BarChart