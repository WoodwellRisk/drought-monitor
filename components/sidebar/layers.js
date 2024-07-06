import { useCallback, useEffect, useState } from 'react'
import { useThemeUI, Box } from 'theme-ui'
import { useThemedColormap } from '@carbonplan/colormaps'
import { Colorbar, Tag, Slider } from '@carbonplan/components'
import { SidebarDivider } from '@carbonplan/layouts'
import Info from './info'

function Layers({ getters, setters }) {
  const sx = {
    group: {
      my: [3],
      pl: [0, 4, 5, 6],
      pr: [0, 5, 5, 6],
      width: '100%',
    },
    label: {
      fontSize: [2, 2, 2, 3],
      fontFamily: 'heading',
      letterSpacing: 'smallcaps',
      textTransform: 'uppercase',
      mb: [2],
    },
    sublabel: {
      display: 'inline-block',
      color: 'primary',
      fontFamily: 'faux',
      letterSpacing: 'faux',
    },
    data_description: {
      fontSize: '14px',
      color: 'primary',
  },
    data_source: {
        mt: 2,
    }
  }

  const {
    display,
    variable,
    year,
    monthDay,
    time,
    regionData,
    clim,
    colormapName,
    colormap,
    hexmap,
    showRegionPicker,
    showCountriesOutline,
    showStatesOutline,
    showDrought,
    showCoffee,
    showCocoa,
    showMaize,
  } = getters

  const {
    setDisplay,
    setVariable,
    setYear,
    setMonthDay,
    setTime,
    setRegionData,
    setClim,
    setColormapName,
    setShowRegionPicker,
    setShowDrought,
    setShowCoffee,
    setShowCocoa,
    setShowMaize,
  } = setters

  const monthDayValues = [
    '01-01', '01-15', '01-29', '02-12', '02-26', '03-12', '03-26', '04-09',
    '04-23', '05-07', '05-21', '06-04','06-18', '07-02', '07-16', '07-30',
    '08-13', '08-27', '09-10', '09-24', '10-08', '10-22', '11-05', '11-19', '12-03', '12-17'
  ]

  // https://javascript.info/date
  console.log(" '2017-01-26' < '2017-01-26' ")
  console.log(new Date("2017-01-26") < new Date("2017-12-26"))
  const [monthDayArray, setMonthDayArray] = useState(monthDayValues)
  const [monthDayIdx, setMonthDayIdx] = useState(0)

  useEffect(() => {
    setMonthDay(monthDayValues[monthDayIdx])
  }, [monthDayIdx])

  useEffect(() => {
    if(year == '2003') {
      setMonthDayArray(monthDayValues.slice(5,))
    } else if (year == '2024') {
      setMonthDayArray(monthDayValues.slice(0,11))
    } else {
      setMonthDayArray(monthDayValues)
    }
  }, [year])

  // useEffect(() => {
  //   if(year == '2024') {
  //     if(monthDayMax)
  //   } else {
  //     setTime(`${year}-${monthDay}`)
  //   }
  // }, [year, monthDay])

  const handleDroughtChange = useCallback(() => {
    setShowDrought((prev) => !prev)
    setDisplay((prev) => !prev)
  })

  const handleCoffeeChange = useCallback(() => {
    if(showCocoa) {
      setShowCocoa(false)
    }
    if(showMaize) {
      setShowMaize(false)
    }
    setShowCoffee((prev) => !prev)
  })

  const handleCocoaChange = useCallback(() => {
    if(showCoffee) {
      setShowCoffee(false)
    }
    if(showMaize) {
      setShowMaize(false)
    }
    setShowCocoa((prev) => !prev)
  })

  const handleMaizeChange = useCallback(() => {
    if(showCoffee) {
      setShowCoffee(false)
    }
    if(showCocoa) {
      setShowCocoa(false)
    }
    setShowMaize((prev) => !prev)
  })

  return (
    <>
      <Box sx={sx.group}>
        <Box sx={{ mt: -3 }} className='var-container'>
          <Box as='h2' variant='styles.h4' className='var-title'>
            Crops <Info>
              Select any combination of coffee, cocoa, and maize.
            </Info>
          </Box>

          <Box className='var-layers'>
              <Tag 
                color={'blue'} 
                value={showCoffee} 
                onClick={handleCoffeeChange}
                sx={{mr:[2], mb:[2], borderColor: 'blue', width: 'max-content',}}
              >
                Coffee 
              </Tag>

              <Tag 
                color={'orange'} 
                value={showCocoa} 
                onClick={handleCocoaChange}
                sx={{mr:[2], mb:[2], borderColor: 'orange', width: 'max-content',}}
              >
                Cocoa
              </Tag>

              <Tag 
                color={'green'}
                value={showMaize} 
                onClick={handleMaizeChange}
                sx={{mr:[2], mb:[2], borderColor: 'green', width: 'max-content',}}
              >
                Maize
              </Tag>

          </Box>
        </Box>
      </Box>
      <SidebarDivider sx={{ width: '100%', my: 4 }} />

      <Box sx={sx.group}>
        <Box as='h2' variant='styles.h4' className='var-subtitle'>
          {'Drought'} <Info>
            <Box className='layer-description' sx={sx.data_description}>
              <Box>
                  Drought
              </Box>
            </Box>
          </Info>
        </Box>

        <Tag 
          color={'red'} 
          value={showDrought} 
          onClick={handleDroughtChange}
          sx={{mr:[2], mb:[4], borderColor: 'red', width: 'max-content',}}>
          Drought
        </Tag>

        <Box sx={{ ...sx.label, }}>
          <Colorbar
            sx={{ width: '250px', display: 'inline-block', flexShrink: 1, }}
            sxClim={{ fontSize: [1, 1, 1, 2], pt: [1] }}
            width='100%'
            colormap={useThemedColormap(colormapName)}
            label={'Drought'}
            // units={''}
            clim={[clim[0].toFixed(2), clim[1].toFixed(2)]}
            horizontal
            bottom
          />
        </Box>

        {/* <Box sx={{ ...sx.label, mt: [4] }}>
          <Box sx={sx.label}>Year</Box>
          <Slider
            sx={{ mt: [3], mb: [3] }}
            value={year}
            onChange={(e) => setYear(e.target.value)}
            min={2003}
            max={2024}
            step={1}
          />

          <Box
            sx={{
              textAlign: 'center',
            }}
          >
            <Box
              sx={{
                fontFamily: 'mono',
                letterSpacing: 'mono',
                fontSize: [1],
                display: 'inline-block',
                float: 'left',
              }}
            >
              2003
            </Box>

            <Box
              sx={{
                fontFamily: 'mono',
                letterSpacing: 'mono',
                display: 'inline-block',
                ml: 'auto',
                mr: 'auto',
                color: 'secondary',
                transition: '0.2s',
                fontSize: [1],
              }}
            >
              {year}
            </Box>

            <Box
              sx={{
                fontFamily: 'mono',
                letterSpacing: 'mono',
                fontSize: [1],
                float: 'right',
                display: 'inline-block',
              }}
            >
              2024
            </Box>
          </Box>
        </Box>

        <Box sx={{ ...sx.label, mt: [4] }}>
          <Box sx={sx.label}>Month and day</Box>
          <Slider
            sx={{ mt: [3], mb: [3] }}
            value={monthDayIdx}
            onChange={(e) => setMonthDayIdx(e.target.value)}
            min={0}
            max={monthDayArray.length - 1}
            step={1}
          />

          <Box
            sx={{
              textAlign: 'center',
            }}
          >
            <Box
              sx={{
                fontFamily: 'mono',
                letterSpacing: 'mono',
                fontSize: [1],
                display: 'inline-block',
                float: 'left',
              }}
            >
              {monthDayArray[0]}
            </Box>

            <Box
              sx={{
                fontFamily: 'mono',
                letterSpacing: 'mono',
                display: 'inline-block',
                ml: 'auto',
                mr: 'auto',
                color: 'secondary',
                transition: '0.2s',
                fontSize: [1],
              }}
            >
              {monthDayArray[monthDayIdx]}
            </Box>

            <Box
              sx={{
                fontFamily: 'mono',
                letterSpacing: 'mono',
                fontSize: [1],
                float: 'right',
                display: 'inline-block',
              }}
            >
              {monthDayArray[monthDayArray.length - 1]}
            </Box>
          </Box>
        </Box> */}

      </Box>
    </>
  )
}

export default Layers