import { Box, Flex } from 'theme-ui';
import { Toggle } from '@carbonplan/components';

import { useStore } from '../store/index';

const sx = {
  'overlays-container': {
    mb: [0],
    mx: 'auto',
    width: '100%',
    height: '75px',
  },
  label: {
    fontFamily: 'mono',
    letterSpacing: 'mono',
    textTransform: 'uppercase',
    fontSize: [1, 1, 1, 2],
    mt: '10px',
    display: 'flex',
  },
  toggle: {
    mt: '8px',
  },
};

const Overlays = () => {
  const showStatesLayer = useStore((state) => state.showStatesLayer);
  const setShowStatesLayer = useStore((state) => state.setShowStatesLayer);
  const showCountriesLayer = useStore((state) => state.showCountriesLayer);
  const setShowCountriesLayer = useStore((state) => state.setShowCountriesLayer);

  return (
    <Box sx={sx['overlays-container']}>
      <Flex sx={{ justifyContent: 'space-between', flexDirection: 'row' }}>
        <Box sx={sx.label}>Countries</Box>
        <Toggle
          sx={sx['toggle']}
          value={showCountriesLayer}
          onClick={() => setShowCountriesLayer(!showCountriesLayer)}
        />
      </Flex>

      <Flex sx={{ justifyContent: 'space-between' }}>
        <Box sx={sx.label}>States</Box>
        <Toggle
          sx={sx['toggle']}
          value={showStatesLayer}
          onClick={() => setShowStatesLayer(!showStatesLayer)}
        />
      </Flex>
    </Box>
  );
};

export default Overlays;
