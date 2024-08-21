import { Box, IconButton } from 'theme-ui'
import { AxisLabel, Chart, Grid, Plot, Ticks, TickLabels } from '@carbonplan/charts'
import { SidebarDivider } from '@carbonplan/layouts'
import { Area, Line } from '@carbonplan/charts'
import Bar from './bar'
import * as d3 from 'd3'

const DensityPlot = ({ data, variable, time, year, monthDay, minDate, colormap }) => {
    const sx = {
        chart: {
            mt: [4],
            mx: 'auto',
            pl: [0, 1, 1, 1],
            pr: [0, 1, 1, 1,],
            width: '100%',
            height: '200px',
        }
    }

    const min = 0.0
    const max = 1.0
    const variableRange = [min, max]

    const nBins = 10;
    const range = max - min;
    const binWidth = range / nBins;
    let binEdges = Array(nBins + 1).fill(0).map((_, i) => Number((i * binWidth).toFixed(2)))
    const bin = d3.bin().domain(variableRange).thresholds(binEdges)

    const xMin = (min - binWidth) * 100;
    const xMax = (max + binWidth) * 100;

    if (!data || !data[variable]) { // ex: if(!'drought' or Object["drought"]) {...}
        return
    }

    let plotPreviousData = null 

    let previousTime = `${parseInt(year) - 1}-${monthDay}`
    console.log(`Times: ${time} ${previousTime}`)
    console.log("Less? ", new Date(previousTime) < new Date(minDate))
    console.log("Data, current time: ", data[variable][time])
    if(new Date(previousTime) >= new Date(minDate)) {
        console.log("Data, previous time: ", data[variable][previousTime])
    }
    console.log()

    let binData = (d, bin) => {
        let graphData = []

        d.forEach(function (element, idx) {
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
        let binnedData = zip(binEdges.map((edge) => edge * 100), percentages);
        return binnedData
    }

    let plotData = binData(data[variable][time], bin)
    if (new Date(previousTime) >= new Date(minDate)) {
        plotPreviousData = binData(data[variable][previousTime], bin)
    }
    // console.log(plotData)

    return (
        <Box sx={{ ...sx.chart }} className='chart-container'>
            <Chart x={[xMin, xMax]} y={[0, 100]} padding={{ left: 50, top: 0 }} >
                <Grid vertical horizontal />
                <Ticks left bottom />
                <TickLabels left bottom />
                <AxisLabel left >Percent</AxisLabel>
                <AxisLabel bottom>Percentile</AxisLabel>
                <Plot>
                    {/* <Area 
                        data={plotData.slice(0, 6)} 
                        width={1.5} 
                        opacity={0.3}
                        color={'blue'}
                        curve={d3.curveMonotoneX} // d3.curveBumpX is another good option
                    />
                    <Area 
                        data={plotData.slice(5)} 
                        width={1.5} 
                        opacity={0.3}
                        color={'red'}
                        curve={d3.curveMonotoneX} // d3.curveBumpX is another good option
                    />

                    <Line 
                        data={plotData.slice(0, 6)} 
                        width={1.5} 
                        color={'blue'}
                        curve={d3.curveMonotoneX} // d3.curveBumpX is another good option
                    />
                    <Line 
                        data={plotData.slice(5)} 
                        width={1.5} 
                        color={'red'}
                        curve={d3.curveMonotoneX} // d3.curveBumpX is another good option
                    /> */}
                    {plotPreviousData && (
                        <>
                            {/* <Area
                                data={plotPreviousData}
                                width={1.5}
                                opacity={0.3}
                                color={'gray'}
                                curve={d3.curveMonotoneX} // d3.curveBumpX is another good option
                            /> */}
                            <Line
                                data={plotPreviousData}
                                width={1.5}
                                color={'gray'}
                                curve={d3.curveMonotoneX}
                            />
                        </>
                    )}

                    {/* <Bar
                        data={plotData}
                        color={plotData.map((_, i) => colormap[i])}
                        strokeWidth={0.5}
                    /> */}

                    <Area
                        data={plotData}
                        width={1.5}
                        opacity={0.3}
                        color={'black'}
                        curve={d3.curveMonotoneX} // d3.curveBumpX is another good option
                    />
                    <Line
                        data={plotData}
                        width={1.5}
                        color={'black'}
                        curve={d3.curveMonotoneX}
                    />
                </Plot>

            </Chart>

            <SidebarDivider sx={{ width: '100%', my: 4 }} />

        </Box>
    )
}

export default DensityPlot