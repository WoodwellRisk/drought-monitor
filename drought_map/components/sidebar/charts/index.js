import { useMemo } from 'react'
import { Box } from 'theme-ui'
import { useThemedColormap } from '@carbonplan/colormaps'
import BarChart from './bar-chart'
import DensityPlot from './density-plot'
import TimeSeries from './timeseries'

import useStore from '../../store/index'
import * as d3 from 'd3'

const StatsDisplay = (props) => {
  const { data, variable, colormap, hexmapBar, hexmapTime } = props

  const time = useStore((state) => state.time)

  if (!data || !data[variable]) { // ex: if(!'drought' or Object["drought"]) {...}
    return
  }

  let result;

  // https://github.com/carbonplan/forest-carbon-web/blob/9012c0fd99a952b68a08a6a25ba645af736bb8fb/components/regional-emissions.js
  let chartData = useMemo(() => {
    let avgData = {}
    // let top95 = {}
    // let bottom95 = {}

    if (!data) return {}
    data.coordinates.time.forEach((t) => {
      let filteredData = data[variable][t].filter((d) => d !== 9.969209968386869e36)
      const average = filteredData.reduce((a, b) => a + b, 0) / filteredData.length
      avgData[t] = average
      // top95[t] = d3.quantile(filteredData, 0.95)
      // bottom95[t] = d3.quantile(filteredData, 0.05)
    })
    // return {'avg': avgData, 'top95': top95, 'bottom95': bottom95}
    return { 'avg': avgData }

  }, [data])

  if (!chartData['avg']) return

  let avg = chartData['avg'][time]
  if (isNaN(avg)) {
    result = 'no data in region'
  } else {
    let displayAvg = avg * 100
    result = `Average percentile: ${displayAvg.toFixed(0)}`
  }

  return (
    <>
      <Box
        sx={{
          fontFamily: 'mono',
          letterSpacing: 'mono',
          textTransform: 'uppercase',

        }}
      >
        {result}
      </Box>

      <BarChart data={data} variable={variable} time={time} colormap={hexmapBar} />

      {/* <TimeSeries data={chartData} time={time} colormap={hexmapTime} /> */}

      {/* <DensityPlot data={data} variable={variable} time={time} colormap={hexmapBar} /> */}

    </>
  )
}

const Charts = () => {
  const variable = useStore((state) => state.variable)
  const regionData = useStore((state) => state.regionData)
  const showRegionPicker = useStore((state) => state.showRegionPicker)

  const colormapName = useStore((state) => state.colormapName)
  const colormap = useThemedColormap(colormapName)
  const discreteColormapBar = useThemedColormap(colormapName, { count: 13 }).slice(1, 12)
  const hexmapBar = discreteColormapBar.map((rgb) => {
    let [r, g, b] = rgb
    return d3.color(`rgb(${r}, ${g}, ${b})`).formatHex()
  })
  const discreteColormapTime = useThemedColormap(colormapName, { count: 547 }).slice(0,)
  const hexmapTime = discreteColormapTime.map((rgb) => {
    let [r, g, b] = rgb
    return d3.color(`rgb(${r}, ${g}, ${b})`).formatHex()
  })

  return (
    <Box>
      {showRegionPicker && regionData[variable] && (
        <>
          <StatsDisplay
            data={regionData}
            variable={variable}
            colormap={colormap}
            hexmapBar={hexmapBar}
            hexmapTime={hexmapTime}
          />
        </>
      )}
    </Box>
  )

}

export default Charts