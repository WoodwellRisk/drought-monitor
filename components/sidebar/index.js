import { Box } from 'theme-ui';
import { useBreakpointIndex } from '@theme-ui/match-media';
import SidebarDivider from './sidebar-divider';

import Layers from './layers';
import ExpandingSection from './expanding-section';
import Overlays from './overlays';
import Charts from './charts/index';

import { useStore } from '../store/index';

const Sidebar = () => {
  const isWide = useBreakpointIndex() > 0;

  const showRegionPicker = useStore((state) => state.showRegionPicker);
  const setShowRegionPicker = useStore((state) => state.setShowRegionPicker);
  const showOverlays = useStore((state) => state.showOverlays);
  const setShowOverlays = useStore((state) => state.setShowOverlays);

  const sx = {
    'sidebar-container': {
      display: ['none', 'flex', 'flex'],
      flexBasis: '100%',
      flexDirection: 'column',
      maxWidth: [0, '300px', '350px'],
      height: '100%',
      borderStyle: 'solid',
      borderWidth: '0px',
      borderRightWidth: '1px',
      borderColor: 'muted',
      zIndex: 900,
      backgroundColor: 'background',
    },
    expander: {
      '&:hover > #charts-expander, &:hover > #overlays-expander': {
        fill: 'secondary',
        stroke: 'secondary',
      },
    },
    stats: {
      mb: [5],
      mx: 'auto',
      width: '100%',
      height: '225px',
    },
  };

  return (
    <Box sx={sx['sidebar-container']}>
      <Box
        id="sidebar"
        sx={{ position: 'relative', flex: 1, overflowY: 'scroll', overflowX: 'hidden' }}
      >
        <Layers />
        <SidebarDivider sx={{ width: '100%', ml: 0, my: 4 }} />

        <ExpandingSection
          label="Charts"
          expanded={showRegionPicker}
          setExpanded={setShowRegionPicker}
        >
          {showRegionPicker && isWide && (
            <Box sx={{ ...sx.stats }}>
              <Charts />
            </Box>
          )}
        </ExpandingSection>
        <SidebarDivider sx={{ width: '100%', ml: 0, my: 4 }} />

        <ExpandingSection label="Overlays" expanded={showOverlays} setExpanded={setShowOverlays}>
          <Overlays />
        </ExpandingSection>
        <SidebarDivider sx={{ width: '100%', ml: 0, mt: 4 }} />
      </Box>
    </Box>
  );
};

export default Sidebar;
