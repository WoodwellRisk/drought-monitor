import { useState } from 'react'
import { useThemeUI, Box } from 'theme-ui'
import { useBreakpointIndex } from '@theme-ui/match-media'
import { useThemedColormap } from '@carbonplan/colormaps'
import * as d3 from 'd3'

import Layout from '../components/view/layout'
import Desktop from '../components/view/desktop'
import Mobile from '../components/view/mobile'

function Index() {
  const isWide = useBreakpointIndex() > 0
  const [expanded, setExpanded] = useState(false)

  const { theme } = useThemeUI()

  const [display, setDisplay] = useState(true)
  const [variable, setVariable] = useState('drought')
  const [year, setYear] = useState('2003')
  const [monthday, setMonthday] = useState('03-12')
  const [time, setTime] = useState(`${year}-${monthday}`)
  const [clim, setClim] = useState([0.0, 1.0])

  const [colormapName, setColormapName] = useState('redteal')
  // freeze colormap so that it doesn't change with theme
  // red will always be > 0.5, blue will always be < 0.5
  const colormap = useThemedColormap(colormapName).slice(0,).reverse()
  const discreteColormap = useThemedColormap(colormapName, { count: 13 }).slice(1, 12).reverse()

  const hexmap = discreteColormap.map((rgb) => {
      let [r, g, b] = rgb
      return d3.color(`rgb(${r}, ${g}, ${b})`).formatHex()
  })

  const [regionData, setRegionData] = useState({loading: true})
  const [showRegionPicker, setShowRegionPicker] = useState(false)
  const [showCountriesOutline, setShowCountriesOutline] = useState(false)
  const [showStatesOutline, setShowStatesOutline] = useState(false)

  const [showDrought, setShowDrought] = useState(true)
  const [showCoffee, setShowCoffee] = useState(false)
  const [showCocoa, setShowCocoa] = useState(false)
  const [showMaize, setShowMaize] = useState(false)

  const description = 'Woodwell Climate Research Center drought / crop monitor'
  const title = 'Woodwell Risk drought / crop monitor'
  const logoURL = 'https://storage.googleapis.com/risk-maps/media/woodwell-risk.png'

  const getters = {
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
  };

  const setters = {
    setDisplay, 
    setVariable,
    setYear,
    setMonthday,
    setTime,
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
  };
  
  return (
    <>
      {isWide && (
        <Layout
          description={description}
          title={title}
          header={false}
          dimmer={false}
          footer={false}
          metadata={false}
          guide={'teal'}
        >
          <Desktop getters={getters} setters={setters} />
        </Layout> 
      )}
      {!isWide && (
        <Box sx={{ display: ['initial', 'none', 'none', 'none'], overflow: "hidden",}}>
          <Layout
            description={description}
            title={title}
            card={logoURL}
            header={true}
            dimmer={true}
            metadata={false}
            footer={false}
            guide={'teal'}
            settings={{
              value: expanded,
              onClick: () => setExpanded(!expanded),
            }}
          >
            <Mobile getters={getters} setters={setters} expanded={expanded} />
          </Layout>
        </Box>
      )}
    </>
  )
}

export default Index