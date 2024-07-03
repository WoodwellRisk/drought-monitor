import { useCallback, useState } from 'react'
import { useThemeUI, Box, Text } from 'theme-ui'
import { colormaps, useThemedColormap } from '@carbonplan/colormaps'
import { Badge, Colorbar, Filter, Tag, Slider } from '@carbonplan/components'
import { SidebarDivider } from '@carbonplan/layouts'
import StraightLine from './icons/straight-line'
import Square from './icons/square'
import Info from './info'

// import {
//   variables, varTitles, varDescriptions, varLayers, climRanges,
//   defaultColors, defaultColormaps, defaultLabels, defaultUnits,
// } from './sidebar-options'

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
    monthday,
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
    setMonthday,
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

  const [coffeeLegend, setCoffeeLegend] = useState(showCoffee)
  const [cocoaLegend, setCocoaLegend] = useState(showCocoa)
  const [maizeLegend, setMaizeLegend] = useState(showMaize)

  const droughtColor = 'red'
  const coffeeColor = 'blue'
  const cocoaColor = 'orange'
  const maizeColor = 'green'

  const handleDroughtChange = useCallback(() => {
    setShowDrought((prev) => !prev)
    setDisplay((prev) => !prev)
  })

  const handleCoffeeChange = useCallback(() => {
    setShowCoffee((prev) => !prev)
    setCoffeeLegend((prev) => !prev)
  })

  const handleCocoaChange = useCallback(() => {
    setShowCocoa((prev) => !prev)
    setCocoaLegend((prev) => !prev)
  })

  const handleMaizeChange = useCallback(() => {
    setShowMaize((prev) => !prev)
    setMaizeLegend((prev) => !prev)
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
            <Box>
              <Tag 
                color={coffeeColor} 
                value={showCoffee} 
                onClick={handleCoffeeChange}
                sx={{mr:[2], mb:[2], borderColor: coffeeColor, width: 'max-content',}}
              >
                Coffee 
              </Tag>
              <Text 
                color={coffeeColor} 
                sx={{
                  mr: 2,
                  opacity: coffeeLegend == true ? 1.0 : 0.24,
                }}
              >
                <StraightLine />
              </Text>
            </Box>

            <Box>
              <Tag 
                color={cocoaColor} 
                value={showCocoa} 
                onClick={handleCocoaChange}
                sx={{mr:[2], mb:[2], borderColor: cocoaColor, width: 'max-content',}}
              >
                Cocoa
              </Tag>
              <Text 
                color={cocoaColor} 
                sx={{
                  mr: 2,
                  opacity: cocoaLegend == true ? 1.0 : 0.24,
                }}
              >
                -----
              </Text>
            </Box>

            <Box>
              <Tag 
                color={maizeColor}
                value={showMaize} 
                onClick={handleMaizeChange}
                sx={{mr:[2], mb:[2], borderColor: maizeColor, width: 'max-content',}}
              >
                Maize
              </Tag>
              <Text 
                color={maizeColor} 
                sx={{
                  ml: -1, 
                  mr: 2, 
                  fontSize: 1,
                  opacity: maizeLegend == true ? 1.0 : 0.24,
                }}
              >
                <Square />
                <Square />
                <Square />
                <Square />
              </Text>
            </Box>
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
          color={droughtColor} 
          value={showDrought} 
          onClick={handleDroughtChange}
          sx={{mr:[2], mb:[4], borderColor: droughtColor, width: 'max-content',}}>
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
          <Box sx={sx.label}>Month</Box>
          <Slider
            min={1}
            max={12}
            step={1}
            sx={{ width: '175px', display: 'inline-block' }}
            value={month}
            onChange={(e) => setMonth(parseFloat(e.target.value))}
          />
          <Badge
            sx={{
              bg: 'primary',
              color: 'background',
              display: 'inline-block',
              position: 'relative',
              left: [3],
              top: [1],
            }}
          >
            {month.toFixed(0)}
          </Badge>
        </Box> */}

        {/* <Box sx={{ ...sx.label, mt: [4] }}>
          <Box sx={sx.label}>Month</Box>
          <Slider
            sx={{ mt: [3], mb: [3] }}
            value={month}
            onChange={(e) => setMonth(parseFloat(e.target.value))}
            min={1}
            max={12}
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
              1
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
              {month}
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
              12
            </Box>
          </Box>
        </Box> */}

      </Box>
    </>
  )
}

export default Layers