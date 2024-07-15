import { useState } from 'react'
import { Box, Flex, Grid, useThemeUI } from 'theme-ui'
import { alpha } from '@theme-ui/color'
import { Left } from '@carbonplan/icons'
import { useThemedColormap } from '@carbonplan/colormaps'
import { Button, Tray, FadeIn } from '@carbonplan/components'
import Map from '../map'
import Layers from '../sidebar/layers'
import About from '../sidebar/about'
import Content from '../sidebar/about/content'
import Loading from './loading'

import * as d3 from 'd3'

function Mobile({ expanded }) {
  const [section, setSection] = useState('map')
  const [showAbout, setShowAbout] = useState(true)
  const toggleAbout = () => setShowAbout(!showAbout)

  // if (showRegionPicker) {
  //   setShowRegionPicker(!showRegionPicker)
  // }

  const { theme } = useThemeUI()

  const [display, setDisplay] = useState(true)
  const [variable, setVariable] = useState('drought')
  const [year, setYear] = useState('2003')
  const [monthDay, setMonthDay] = useState('03-12')
  const [time, setTime] = useState(`${year}-${monthDay}`)
  const [clim, setClim] = useState([0.0, 1.0])

  const [colormapName, setColormapName] = useState('redteal')
  // freeze colormap so that it doesn't change with theme
  // red will always be > 0.5, blue will always be < 0.5
  const colormap = useThemedColormap(colormapName).slice(0,)
  const discreteColormap = useThemedColormap(colormapName, { count: 13 }).slice(1, 12)

  const hexmap = discreteColormap.map((rgb) => {
      let [r, g, b] = rgb
      return d3.color(`rgb(${r}, ${g}, ${b})`).formatHex()
  })

  const [regionData, setRegionData] = useState({loading: true})
  const [showRegionPicker, setShowRegionPicker] = useState(false)
  const [showDrought, setShowDrought] = useState(true)
  const [showCoffee, setShowCoffee] = useState(false)
  const [showCocoa, setShowCocoa] = useState(false)
  const [showMaize, setShowMaize] = useState(false)

  const getters = {
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
    showDrought,
    showCoffee,
    showCocoa,
    showMaize,
  };

  const setters = {
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
  };

  return (
    <>
      {section === 'map' && (
        <Box
          sx={{
            width: 'calc(100vw)',
            // height: 'calc(100vh - 120px)',
            height: 'calc(100vh)',
            display: 'flex',
            ml: [-3],
          }}
        >
          <Map getters={getters} setters={setters} mobile={true} />

          <Loading isWide mobile />
        </Box>
      )}

      <Tray
        expanded={expanded}
        sx={{
          pb: [4],
          pt: [5],
          transform: expanded ? 'translateY(0)' : 'translateY(-550px)',
        }}
      >
        <Layers getters={getters} setters={setters} />
      </Tray>

      {section === 'about' && (
        <>
          <FadeIn>
            <Box sx={{ mt: [3], }} className='spacer' />
            <Button
              size='xs'
              inverted
              prefix={<Left />}
              onClick={() => setSection('map')}
              sx={{ mt: [1], cursor: 'pointer' }}
            >
              Back
            </Button>

            <Box sx={{height:'100%'}}>
              <Content />
            </Box>
          </FadeIn>
        </>
      )}

      {/* This section defines the boxes at the bottom of the mobile view. */}
      <Box
        sx={{
          position: 'fixed',
          bottom: 0,
          width: '100%',
          bg: 'background',
          height: '64px',
          borderStyle: 'solid',
          borderWidth: '0px',
          borderTopWidth: '1px',
          borderColor: 'muted',
          fontSize: [3],
          ml: [-3],
          fontFamily: 'heading',
          letterSpacing: 'allcaps',
          textTransform: 'uppercase',
        }}
      >
        <Grid columns={[2]} gap={[0]}>
          <Flex
            onClick={() => setSection('map')}
            sx={{
              justifyContent: 'center',
              alignItems: 'center',
              height: '64px',
              borderStyle: 'solid',
              borderColor: 'muted',
              borderWidth: '0px',
              borderLeftWidth: '0px',
              borderRightWidth: '1px',
              cursor: 'pointer',
              bg: section === 'map' ? alpha('muted', 0.5) : 'background',
            }}
          >
            Map
          </Flex>

          <Flex
            onClick={() => setSection('about')}
            sx={{
              justifyContent: 'center',
              alignItems: 'center',
              height: '64px',
              // height: '100%',
              cursor: 'pointer',
              bg: section === 'about' ? alpha('muted', 0.5) : 'background',
            }}
          >
            About
          </Flex>
        </Grid>
      </Box>
    </>
  )
}

export default Mobile