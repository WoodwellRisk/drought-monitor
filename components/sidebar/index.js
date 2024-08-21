import { useState } from 'react'
import { Box, Text } from 'theme-ui'
import { SidebarDivider } from '@carbonplan/layouts'

import SidebarHeader from './sidebar-header'
import Menu from './menu'
import Layers from './layers'
import SummaryStats from './summary-stats'
import Footer from './footer'

const Sidebar = ({ getters, setters, showAbout, toggleAbout }) => {
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
    hexmapBar,
    hexmapTime,
    showRegionPicker,
    crops,
    cropLayer,
    cropValues,
    showDrought,
    minDate,
    maxDate,
    showWarning
  } = getters

  const sx = {
    'sidebar-container': {
      maxWidth: [
        0,
        '350px',
        '350px',
        '400px',
      ],
      height: '100%',
      flexBasis: '100%',
      flexDirection: 'column',
      borderStyle: 'solid',
      borderWidth: '0px',
      borderRightWidth: '1px',
      borderColor: 'muted',
      zIndex: 900,
      backgroundColor: 'background',
      display: ['none', 'flex', 'flex'],
    },
    'expand-section': {
      mx: [3, 4, 5, 6],
      pt: [1],
      mt: ['12px'],
      fontSize: [2, 2, 2, 3],
      width: 'fit-content',
      fontFamily: 'heading',
      letterSpacing: 'smallcaps',
      textTransform: 'uppercase',
      cursor: 'pointer',
      '&:hover': {
        color: 'secondary',
      },
    },
    arrow: {
      display: 'inline-block',
      fontSize: [4],
      ml: [2],
      top: '3px',
      position: 'relative',
      transition: 'transform 0.2s',
      transform: showAbout ? 'scaleX(-1)' : 'scaleX(1)',
    },
    stats: {
      mb: [5],
      mx: 'auto',
      width: '100%',
      height: '275px',
    }
  }

  const [showMenu, setShowMenu] = useState(false)
  const [sliding, setSliding] = useState(false)

  return (
    <Box sx={sx['sidebar-container']}>
      <SidebarHeader showMenu={showMenu} toggleMenu={() => setShowMenu(!showMenu)} />

      <Box id='sidebar' sx={{ position: 'relative', flex: 1, overflowY: 'scroll', }} >
        <Menu visible={showMenu} />

        <Box onClick={toggleAbout} sx={sx['expand-section']} >
          HOW TO USE THIS SITE <Text sx={sx.arrow}>→</Text>
        </Box>
        <SidebarDivider sx={{ width: '100%', my: 4 }} />

        <Layers getters={getters} setters={setters} sliding={sliding} onSliding={setSliding} />
        <SidebarDivider sx={{ width: '100%', my: 4 }} />

        {showRegionPicker && new Date(time) <= new Date(maxDate) && (
          <Box sx={{ ...sx.stats }}>
            <SummaryStats
              variable={variable}
              time={time}
              year={year}
              monthDay={monthDay}
              minDate={minDate}
              regionData={regionData}
              showRegionPicker={showRegionPicker}
              colormap={colormap}
              hexmapBar={hexmapBar}
              hexmapTime={hexmapTime}
              sliding={sliding}
            />
          </Box>
        )}

        <Footer />
      </Box>

    </Box>
  )
}

export default Sidebar
