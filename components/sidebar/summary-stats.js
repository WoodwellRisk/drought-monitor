import { Box } from 'theme-ui'

const AverageDisplay = ({ variable, data }) => {

    if (!data.value || !data.value[variable]) { // ex: if(!'drought' or Object["drought"]) {...}
      return
    }
  
    let result
    const filteredData = data.value[variable].filter((d) => d !== 9.969209968386869e36)

    if (filteredData.length === 0) {
      result = 'no data in region'
    } else {
      const average =
        filteredData.reduce((a, b) => a + b, 0) / filteredData.length
        result = `Average: ${average.toFixed(2)}`
    }
  
    return (
      <Box
        sx={{
          ml: [2],
          mt: [0],
          fontFamily: 'mono',
          letterSpacing: 'mono',
          textTransform: 'uppercase',

        }}
      >
        {result}
      </Box>
    )
  }
  
  const SummaryStats = ({variable, regionData}) => {    

    return (
      <Box
        sx={{
            mt: [4],
            mb: [0],
            mx: 'auto',
            pl: [0, 4, 5, 6],
            pr: [0, 1, 1, 1,],
        }}
      > 
        {regionData?.value && (
          <AverageDisplay variable={variable} data={regionData} />
        )}
      </Box>
    )
  }
  
  export default SummaryStats