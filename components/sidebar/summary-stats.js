import { Box } from 'theme-ui'
import { useMemo } from 'react'
import * as d3 from 'd3'
import BarChart from './charts/bar-chart'
import DensityPlot from './charts/density-plot'
// import TimeSeries from './charts/timeseries'

const StatsDisplay = (props) => {
  const { 
    data, 
    variable, 
    time,
    minDate, 
    year,
    monthDay,
    colormap, 
    hexmapBar, 
    hexmapTime, 
    sliding 
  } = props

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
    return {'avg': avgData}

  }, [data])

  if(!chartData['avg']) return

  let avg = chartData['avg'][time]
  if (isNaN(avg)) {
    result = 'no data in region'
  } else {
      result = `Average: ${avg.toFixed(2)} percentile`
  }

  return (
    <>
      <Box
        sx={{
          // ml: [2],
          // pl: [5],
          // mt: ['-1px'],
          fontFamily: 'mono',
          letterSpacing: 'mono',
          textTransform: 'uppercase',

        }}
      >
        {result}
      </Box>

      <BarChart data={data} variable={variable} time={time} colormap={hexmapBar} />

      {/* <TimeSeries data={chartData} time={time} colormap={hexmapTime} sliding={sliding} /> */}

      {/* <DensityPlot 
        data={data} 
        variable={variable} 
        time={time} 
        year={year}
        monthDay={monthDay}
        minDate={minDate}
        colormap={hexmapBar} 
      /> */}

    </>
  )
}

const SummaryStats = (props) => {
  const {
    regionData, 
    variable, 
    time, 
    year,
    monthDay,
    minDate,
    maxDate, 
    showRegionPicker, 
    colormap, 
    hexmapBar, 
    hexmapTime, 
    sliding
  } = props
  
    return (
      <Box
        sx={{
          // mt: [4],
          // mx: 'auto',
          // pl: [0, 2, 2, 2],
          // pr: [0, 1, 1, 1,],
        }}
      >
        {showRegionPicker && regionData[variable] && (
          <>
            <StatsDisplay 
              data={regionData} 
              variable={variable}
               time={time} 
               year={year}
               monthDay={monthDay}
               minDate={minDate}
               colormap={colormap} 
               hexmapBar={hexmapBar} 
               hexmapTime={hexmapTime}
               sliding={sliding} 
            />
            </>
        )}
      </Box>
    )

}

export default SummaryStats