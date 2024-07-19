import { Box } from 'theme-ui'
import { useMemo } from 'react'
import { SidebarDivider } from '@carbonplan/layouts'
import BarChart from './charts/bar-chart'
import TimeSeries from './charts/timeseries'

const StatsDisplay = ({ data, variable, time, colormap, hexmap, sliding }) => {
  if (!data || !data[variable]) { // ex: if(!'drought' or Object["drought"]) {...}
    return
  }

  let result;

  // https://github.com/carbonplan/forest-carbon-web/blob/9012c0fd99a952b68a08a6a25ba645af736bb8fb/components/regional-emissions.js
  let chartData = useMemo(() => {
    let lineData = {}
    if (!data) return {}
    data.coordinates.time.forEach((t) => {
      let filteredData = data[variable][t].filter((d) => d !== 9.969209968386869e36)
      const average = filteredData.reduce((a, b) => a + b, 0) / filteredData.length
      lineData[t] = average
    })
    return lineData
  }, [data])

  let avg = chartData[time]
  if (isNaN(avg)) {
    result = 'no data in region'
  } else {
      result = `Average: ${avg.toFixed(2)} percentile`
  }

  return (
    <>
      <Box
        sx={{
          ml: [2],
          pl: [6],
          mt: ['-1px'],
          fontFamily: 'mono',
          letterSpacing: 'mono',
          textTransform: 'uppercase',

        }}
      >
        {result}
      </Box>

      <BarChart data={data} variable={variable} time={time} colormap={hexmap} />

      {/* <TimeSeries data={chartData} time={time} colormap={colormap} sliding={sliding} /> */}
    </>
  )
}

const SummaryStats = (props) => {
  const {regionData, variable, time, showRegionPicker, colormap, hexmap, sliding} = props

  return (
    <Box
      sx={{
        mt: [4],
        mx: 'auto',
        pl: [0, 2, 2, 2],
        pr: [0, 1, 1, 1,],
      }}
    >
      {showRegionPicker && regionData[variable] && (
        <>
          <StatsDisplay data={regionData} variable={variable} time={time} colormap={colormap} hexmap={hexmap} sliding={sliding} />
          <SidebarDivider sx={{ width: '100%', my: 4 }} />
        </>
      )}
    </Box>
  )
}

export default SummaryStats