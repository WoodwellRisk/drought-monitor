import { Box } from 'theme-ui'
import { Area, AxisLabel, Chart, Circle, Grid, Line, Plot, Ticks, TickLabels } from '@carbonplan/charts'
import { SidebarDivider } from '@carbonplan/layouts'
import { useThemedColormap } from '@carbonplan/colormaps'
import { Colorbar } from '@carbonplan/components'
import Bar from './bar'
import * as d3 from 'd3'

const TimeBar = ({ data, time, colormap, sliding }) => {

    const sx = {
        chart: {
            mt: [0],
            mb: [0],
            mx: 'auto',
            // pl: [0, 1, 1, 0],
            // pr: [0, 1, 1, 1,],
            width: '100%',
            height: '200px',
        },
        label: {
            fontSize: [2, 2, 2, 3],
            fontFamily: 'heading',
            letterSpacing: 'smallcaps',
            textTransform: 'uppercase',
            mt: [4],
            ml: [2],
            pl: [6],
        },
    }

    const numberOfNaNs = Object.values(data).filter(x => isNaN(x)).length
    const lengthOfTime = Object.keys(data).length - numberOfNaNs
    // https://stackoverflow.com/questions/11258077/how-to-find-index-of-an-object-by-key-and-value-in-an-javascript-array#39810268
    const timeIndex = Object.keys(data).findIndex(date => date == time)

    const xData = Array.from(Array(lengthOfTime), (_, i) => i)
    const yData = Object.values(data)
    // https://stackoverflow.com/questions/22015684/zip-arrays-in-javascript
    // https://github.com/carbonplan/charts/issues/4
    // we have to skip the first five values that are nans because they are not supported
    const plotData = xData.map((x, idx) => [x, yData[idx]]).slice(numberOfNaNs,)
    
    // console.log(plotData.length)
    // console.log(plotData)
    // console.log(colormap)

    // console.log(discreteColormap)
    // console.log(hexmap)
    // console.log(plotData.map((val, idx) => val[1]))
    // console.log(plotData.map((val, idx) => colormap[idx]))
    // we need to move from [0,1] drought values to [0, 547] hexmap indices
    let scaledIndices = plotData.map(xy => Math.round(xy[1] * 547))
    let reOrderedColormap = scaledIndices.map((val, idx) => colormap[val])
    // let positiveNegativeColormap = plotData.map((val, idx) => val > 0.5 ? '#64bac5' : val == 0.5 ? '#0a0a0a' : '#ef7071')
    // let positiveNegativeColormap = plotData.map((val, idx) => {
    //     // console.log(val[1], val[1] > 0.5)
    //     return val[1] > 0.5 ? '#64bac5' : val[1] == 0.5 ? '#0a0a0a' : '#ef7071'
    // })
    // console.log(positiveNegativeColormap)
    // console.log(reOrderedColormap)
    // console.log(plotData.map((val, idx) => val > 0.5 ? '#E1F2F3' : val == 0.5 ? 'black' : '#FFE5E2' ))

    return (
        <>
            <Box sx={{ ...sx.label }}>
                <Colorbar
                    sx={{ width: '100%', display: 'inline-block', flexShrink: 1, }}
                    sxClim={{ fontSize: [1, 1, 1, 2], pt: [0] }}
                    width='100%'
                    colormap={reOrderedColormap}
                    label={'Change over time'}
                    clim={['2003', '2024']}
                    horizontal
                    bottom
                    discrete
                />
            </Box>
            <Box sx={{ ...sx.chart }} className='chart-container'>
                <Chart x={[0, lengthOfTime - 1]} y={[0, 1]} padding={{ left: 60, top: 20 }}>
                    <Grid vertical horizontal />
                    <Ticks left bottom />
                    <TickLabels left bottom />
                    <AxisLabel left>Percentile</AxisLabel>
                    <AxisLabel bottom>Time</AxisLabel>
                    <Plot>
                        <Line
                            data={[
                                [timeIndex, 0],
                                [timeIndex, 1],
                            ]}
                            color='secondary'
                            sx={{
                                opacity: sliding ? 1 : 0,
                                strokeDasharray: 4,
                                transition: 'opacity 0.15s',
                            }}
                        />

                        <Line data={plotData} width={1.5} color={'black'} />
                        
                        <Bar
                            data={plotData.map(([x, y]) => [x, 0.5, y])}
                            color={plotData.map((val, idx) => val[1] > 0.5 ? '#64bac5' : val[1] == 0.5 ? '#0a0a0a' : '#ef7071' )}
                            strokeWidth={0.0}
                        />

                        {/* https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/every */}
                        {!plotData.every((value) => isNaN(value[1])) && (
                            <Circle
                                x={timeIndex}
                                y={data[time]}
                                size={8}
                            />
                        )}

                    </Plot>
                </Chart>
            </Box>
        </>
    )
}

export default TimeBar