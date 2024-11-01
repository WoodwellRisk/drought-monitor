import {useEffect} from 'react'
import { Box } from 'theme-ui'
import { Area, AxisLabel, Chart, Circle, Grid, Line, Plot, Ticks, TickLabels } from '@carbonplan/charts'
import { SidebarDivider } from '@carbonplan/layouts'
import { useThemedColormap } from '@carbonplan/colormaps'
import { Colorbar } from '@carbonplan/components'
import Bar from './bar'

import useStore from '../../store/index'
import * as d3 from 'd3'

const TimeBar = ({ data, time, colormap }) => {

    const sliding = useStore((state) => state.sliding)

    const sx = {
        chart: {
            mt: [4],
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

    let mean = data['avg']
    // let top = data['top95']
    // let bottom = data['bottom95']

    // const numberOfNaNs = Object.values(data).filter(x => isNaN(x)).length
    // const lengthOfTime = Object.keys(data).length - numberOfNaNs

    // https://stackoverflow.com/questions/11258077/how-to-find-index-of-an-object-by-key-and-value-in-an-javascript-array#39810268
    const timeIndex = Object.keys(mean).findIndex(date => date == time)

    const lengthOfTime = Object.keys(mean).length
    const xData = Array.from(Array(lengthOfTime), (_, i) => i)
    const yMean = Object.values(mean)
    // const yTop = Object.values(top)
    // const yBottom = Object.values(bottom)
    // https://stackoverflow.com/questions/22015684/zip-arrays-in-javascript
    const plotMean = xData.map((x, idx) => [x, yMean[idx]])
    // const plotTop = xData.map((x, idx) => [x, yTop[idx]])
    // const plotBottom = xData.map((x, idx) => [x, yBottom[idx]])

    // we need to move from [0,1] drought values to [0, 547] hexmap indices
    // let scaledIndices = plotMean.map(xy => Math.round(xy[1] * lengthOfTime))
    // let reOrderedColormap = scaledIndices.map((val, idx) => colormap[val])

    return (
        <>
            {/* <Box sx={{ ...sx.label }}>
                <Colorbar
                    sx={{ width: '100%', display: 'inline-block', flexShrink: 1, }}
                    sxClim={{ fontSize: [1, 1, 1, 2], pt: [0] }}
                    width='100%'
                    colormap={reOrderedColormap}
                    label={'Change over time'}
                    clim={['2001', '2024']}
                    horizontal
                    bottom
                    discrete
                />
            </Box> */}

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

                        {/* <Bar
                            data={plotTop.map(([x, y]) => [x, 0.5, y])}
                            color={'gray'}
                            strokeWidth={0.0}
                            alpha={0.5}
                        />

                        <Bar
                            data={plotBottom.map(([x, y]) => [x, 0.5, y])}
                            color={'gray'}
                            strokeWidth={0.0}
                        /> */}

                        <Line data={plotMean} width={1.5} color={'black'} />

                        <Bar
                            data={plotMean.map(([x, y]) => [x, 0.5, y])}
                            color={plotMean.map((val, idx) => val[1] > 0.5 ? '#64bac5' : val[1] == 0.5 ? '#0a0a0a' : '#ef7071')}
                            strokeWidth={0.0}
                        />

                        <Circle
                            x={timeIndex}
                            y={mean[time]}

                            size={8}
                            sx={{
                                opacity: sliding ? 1 : 0,
                                transition: 'opacity 0.15s',
                            }}
                        />

                    </Plot>
                </Chart>
            </Box>
        </>
    )
}

export default TimeBar