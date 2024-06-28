import { useCallback, useState } from 'react'
import { useThemeUI, Box } from 'theme-ui'
import { colormaps, useThemedColormap } from '@carbonplan/colormaps'
import { Badge, Colorbar, Filter, Tag, Slider } from '@carbonplan/components'
import { SidebarDivider } from '@carbonplan/layouts'
import Info from './info'

import {
  variables, varTitles, varDescriptions, varLayers, climRanges,
  defaultColors, defaultColormaps, defaultLabels, defaultUnits,
} from './sidebar-options'

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
  }

  const {
    display,
    opacity,
    variable,
    band,
    month,
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
    setOpacity,
    setVariable,
    setBand,
    setMonth,
    setRegionData,
    setClim,
    setColormapName,
    setShowRegionPicker,
    setShowCountriesOutline,
    setShowStatesOutline,
    setShowDrought,
    setShowCoffee,
    setShowCocoa,
    setShowMaize,
  } = setters

  const [varTags, setVarTags] = useState({'Drought': true,})
  const [varDescription, setVarDescription] = useState(varDescriptions[variable])
  const [varTitle, setVarTitle] = useState(varTitles['Drought'])

  const handleBandChange = useCallback((event) => {
    if (variables.includes(event.target.innerHTML)) {
      let tempVar = event.target.innerHTML;
      setVarTitle(varTitles[tempVar])
      setVarDescription(varDescriptions[variable])
      setClim([climRanges[variable].min, climRanges[variable].max])
      setColormapName(defaultColormaps[variable])
    }
  })

  const handleDroughtChange = useCallback(() => {
    setShowDrought((prev) => !prev)
    setDisplay((prev) => !prev)
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
              color='blue' 
              value={showCoffee} 
              // onClick={() => setShowCoffee((prev))}
              sx={{mr:[2], mb:[2], borderColor:'purple', width: 'max-content',}}
            >
              Cocoa
            </Tag>
            <Tag 
              color='orange' 
              value={showCocoa} 
              // onClick={() => setShowCocoa((prev))}
              sx={{mr:[2], mb:[2], borderColor:'purple', width: 'max-content',}}
            >
              Cocoa
            </Tag>
            <Tag 
              color='green' 
              value={showMaize} 
              // onClick={() => setShowMaize((prev))}
              sx={{mr:[2], mb:[2], borderColor:'purple', width: 'max-content',}}
            >
              Maize
            </Tag>
          </Box>
        </Box>
      </Box>
      <SidebarDivider sx={{ width: '100%', my: 4 }} />

      <Box sx={sx.group}>
        <Box as='h2' variant='styles.h4' className='var-subtitle'>
          {varTitle} <Info>{varDescription}</Info>
        </Box>

        <Tag 
          color='purple' 
          value={showDrought} 
          onClick={handleDroughtChange}
          sx={{mr:[2], mb:[4], borderColor:'purple', width: 'max-content',}}>
          Drought
        </Tag>

        <Box sx={{ ...sx.label, }}>
          <Colorbar
            sx={{ width: '250px', display: 'inline-block', flexShrink: 1, }}
            sxClim={{ fontSize: [1, 1, 1, 2], pt: [1] }}
            width='100%'
            colormap={useThemedColormap(colormapName)}
            label={defaultLabels[variable]}
            units={defaultUnits[variable]}
            clim={[clim[0].toFixed(2), clim[1].toFixed(2)]}
            horizontal
            bottom
          />
        </Box>

        <Box sx={{ ...sx.label, }}>
          <Colorbar
            sx={{ width: '250px', display: 'inline-block', flexShrink: 1, }}
            sxClim={{ fontSize: [1, 1, 1, 2], pt: [1] }}
            width='100%'
            colormap={hexmap}
            label={defaultLabels[variable]}
            units={defaultUnits[variable]}
            clim={[clim[0].toFixed(2), clim[1].toFixed(2)]}
            horizontal
            bottom
            discrete
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