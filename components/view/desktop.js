import { useEffect, useState } from 'react'
import { Flex, useThemeUI} from 'theme-ui'
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
  const [year, setYear] = useState('2001')
  const [monthDay, setMonthDay] = useState('01-01')
  const [time, setTime] = useState(`${year}-${monthDay}`)
  const minDate = '2001-01-01'
  const maxDate = '2024-06-18'
  const [clim, setClim] = useState([0.0, 1.0])
  const [regionData, setRegionData] = useState({loading: true})
  const [showRegionPicker, setShowRegionPicker] = useState(false)
  const [colormapName, setColormapName] = useState('redteal')
  // freeze colormap so that it doesn't change with theme
  // red will always be > 0.5, blue will always be < 0.5
  const colormap = useThemedColormap(colormapName).slice(0,)
  const discreteColormapBar = useThemedColormap(colormapName, { count: 13 }).slice(1, 12)
  const hexmapBar = discreteColormapBar.map((rgb) => {
      let [r, g, b] = rgb
      return d3.color(`rgb(${r}, ${g}, ${b})`).formatHex()
  })
  const discreteColormapTime = useThemedColormap('redteal', { count: 547 }).slice(0,)
  const hexmapTime = discreteColormapTime.map((rgb) => {
      let [r, g, b] = rgb
      return d3.color(`rgb(${r}, ${g}, ${b})`).formatHex()
  })


  const crops = ["cocoa", "coffee", "cotton", "maize", "sugar", "wheat"]
  const defaultCropValues = {
    "cocoa": false, 
    "coffee": false, 
    "cotton": false, 
     "maize": false, 
     "sugar": false, 
     "wheat": false 
  }
  const [cropLayer, setCropLayer] = useState("")
  const [cropValues, setCropValues] = useState(defaultCropValues)
  const [showCropLayer, setShowCropLayer] = useState([{}])
  const [showDrought, setShowDrought] = useState(true)

  const [showCountriesOutline, setShowCountriesOutline] = useState(false)
  const [showStatesOutline, setShowStatesOutline] = useState(false)
  const [showWarning, setShowWarning] = useState(false)

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
    hexmapBar,
    hexmapTime,
    showRegionPicker,
    showDrought,
    crops,
    cropLayer,
    showCropLayer,
    cropValues,
    minDate,
    maxDate,
    showCountriesOutline,
    showStatesOutline,
    showWarning,
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
    setCropLayer,
    setShowCropLayer,
    setCropValues,
    setShowCountriesOutline,
    setShowStatesOutline,
    setShowWarning,
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
