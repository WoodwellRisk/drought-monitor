import { Box } from 'theme-ui'
import SidebarDivider from './sidebar-divider'

import Layers from './layers'
import ExpandingSection from './expanding-section'
import Overlays from './overlays'
import Charts from './charts/index'

import useStore from '../store/index'

const Sidebar = () => {
  const maxDate = useStore((state) => state.maxDate)
  const time = useStore((state) => state.time)
  const showRegionPicker = useStore((state) => state.showRegionPicker)
  const setShowRegionPicker = useStore((state) => state.setShowRegionPicker)
  const showOverlays = useStore((state) => state.showOverlays)
  const setShowOverlays = useStore((state) => state.setShowOverlays)

  const sx = {
    'sidebar-container': {
      maxWidth: [
        0,
        '300px',
        '350px',
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
      <Box id='sidebar' sx={{ position: 'relative', flex: 1, overflowY: 'scroll', }} >
        <Layers />
        <SidebarDivider sx={{ width: '100%', ml: 0, my: 4 }} />

        <ExpandingSection 
          label='Charts' 
          expanded={showRegionPicker} 
          setExpanded={setShowRegionPicker}
          disabled={new Date(time) > new Date(maxDate)}
        >
          {showRegionPicker && new Date(time) <= new Date(maxDate) && (
            <Box sx={{ ...sx.stats }}>
              <Charts />
            </Box>
          )}
        </ExpandingSection>
        <SidebarDivider sx={{ width: '100%', ml: 0, my: 4 }} /> 

        <ExpandingSection label='Overlays' expanded={showOverlays} setExpanded={setShowOverlays}>
          <Overlays />
        </ExpandingSection>
        <SidebarDivider sx={{ width: '100%', ml: 0, mt: 4 }} />

      </Box>

    </Box>
  )
}

export default Sidebar
