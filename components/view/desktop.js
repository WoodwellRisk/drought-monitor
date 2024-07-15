import { useState } from 'react'
import { Box, Flex, useThemeUI} from 'theme-ui'
import { useThemedColormap } from '@carbonplan/colormaps'
import Sidebar from '../sidebar'
import About from '../sidebar/about'
import Map from '../map'
import Loading from './loading'

import * as d3 from 'd3'

function Desktop() {
  const [showAbout, setShowAbout] = useState(false)
  const toggleAbout = () => setShowAbout(!showAbout)

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
    <Flex
      sx={{
        position: 'absolute',
        left: 0,
        right: 0,
        top: 0,
        bottom: 0,
        flexDirection: ['column', 'row', 'row'],
        overflow: 'hidden',
        margin: 'auto',
      }}
    >
      <Sidebar getters={getters} setters={setters} showAbout={showAbout} toggleAbout={toggleAbout} />

      <About showAbout={showAbout} toggleAbout={toggleAbout} mobile={false}/>

      <Map getters={getters} setters={setters} mobile={false} />
      
      <Loading />
    </Flex>
  )
}

export default Desktop
