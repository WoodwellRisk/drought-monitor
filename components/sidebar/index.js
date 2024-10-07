import { useState } from 'react'
import { Box, Text } from 'theme-ui'
import { SidebarDivider } from '@carbonplan/layouts'

import SidebarHeader from './sidebar-header'
import Menu from './menu'
import Layers from './layers'
import ExpandingSection from './expanding-section'
import Overlays from './overlays'
import SummaryStats from './charts/summary-stats'
import Footer from './footer'

import useStore from '../store/index'

const Sidebar = () => {
  const maxDate = useStore((state) => state.maxDate)
  const time = useStore((state) => state.time)
  const showRegionPicker = useStore((state) => state.showRegionPicker)
  const setShowRegionPicker = useStore((state) => state.setShowRegionPicker)
  const showAbout = useStore((state) => state.showAbout)
  const setShowAbout = useStore((state) => state.setShowAbout)
  const showMenu = useStore((state) => state.showMenu)
  const setShowMenu = useStore((state) => state.setShowMenu)
  const showOverlays = useStore((state) => state.showOverlays)
  const setShowOverlays = useStore((state) => state.setShowOverlays)

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
    'click-section': {
      mx: [3, 4, 5, 5],
      pt: [1],
      mt: ['12px'],
      fontSize: [2, 2, 2, 3],
      width: 'fit-content',
      fontFamily: 'heading',
      letterSpacing: 'smallcaps',
      textTransform: 'uppercase',
      cursor: 'pointer',
      transition: '0.25s all',
      '&:hover': {
        color: 'secondary',
      },
    },
    'arrow': {
      display: 'inline-block',
      fontSize: [4],
      ml: [2],
      top: '3px',
      position: 'relative',
      transition: 'transform 0.2s',
      transform: showAbout ? 'scaleX(-1)' : 'scaleX(1)',
    },
    'expander': {
      '&:hover > #charts-expander, &:hover > #overlays-expander': {
        fill: 'secondary',
        stroke: 'secondary'
      }
    },
    'stats': {
      mb: [5],
      mx: 'auto',
      width: '100%',
      height: '225px',
    },
  }

  return (
    <Box sx={sx['sidebar-container']}>
      <SidebarHeader showMenu={showMenu} toggleMenu={() => setShowMenu(!showMenu)} />

      <Box id='sidebar' sx={{ position: 'relative', flex: 1, overflowY: 'scroll', }} >
        <Menu visible={showMenu} />

        <Box onClick={() => setShowAbout(!showAbout)} sx={sx['click-section']} >
          How to use this site <Text sx={sx.arrow}>→</Text>
        </Box>
        <SidebarDivider sx={{ width: '100%', my: 4 }} />

        <Layers />
        <SidebarDivider sx={{ width: '100%', my: 4 }} />

        <ExpandingSection 
          label='Charts' 
          expanded={showRegionPicker} 
          setExpanded={setShowRegionPicker}
          disabled={new Date(time) > new Date(maxDate)}
        >
          {showRegionPicker && new Date(time) <= new Date(maxDate) && (
            <Box sx={{ ...sx.stats }}>
              <SummaryStats />
            </Box>
          )}
        </ExpandingSection>
        <SidebarDivider sx={{ width: '100%', my: 4 }} /> 

        <ExpandingSection label='Overlays' expanded={showOverlays} setExpanded={setShowOverlays}>
          <Overlays />
        </ExpandingSection>
        <SidebarDivider sx={{ width: '100%', mt: 4 }} />

        <Footer />
      </Box>

    </Box>
  )
}

export default Sidebar
