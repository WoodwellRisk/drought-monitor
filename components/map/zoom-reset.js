import { useCallback, useState } from 'react';
import { keyframes } from '@emotion/react';
import { IconButton } from 'theme-ui';
import { useBreakpointIndex } from '@theme-ui/match-media';
import { Reset } from '@carbonplan/icons';

import { useMap } from './map-provider';
import { useMapView } from './use-map-view';
import { useStore } from '../store/index';

const ZoomReset = () => {
  const isWide = useBreakpointIndex() > 0;
  const { map } = useMap();

  const initialZoom = useStore((state) => state.initialZoom);
  const initialCenter = useStore((state) => state.initialCenter);
  const { zoom, center } = useMapView();
  const atInitialConditions =
    zoom === initialZoom && center[0] === initialCenter[0] && center[1] === initialCenter[1];
  const [spinning, setSpinning] = useState(false);

  const spin = keyframes({
    from: {
      transform: 'rotate(0turn)',
    },
    to: {
      transform: 'rotate(1turn)',
    },
  });

  const handleResetClick = useCallback(() => {
    if (atInitialConditions) return;

    setSpinning(true);
    map.flyTo({
      center: initialCenter,
      zoom: initialZoom,
    });
    [map, atInitialConditions, initialCenter, initialZoom];
  });

  if (!map) return null;

  return (
    <IconButton
      aria-label="Reset map extent"
      onClick={handleResetClick}
      onAnimationEnd={() => setSpinning(false)}
      disabled={atInitialConditions}
      sx={{
        display: isWide ? 'initial' : 'none',
        svg: spinning ? { animation: `${spin.toString()} 1s` } : {},
        stroke: 'primary',
        color: atInitialConditions ? 'muted' : 'primary',
        cursor: 'pointer',
        position: 'absolute',
        right: '0.5rem',
        bottom: '0.5rem',
        borderWidth: '1px',
        borderStyle: 'solid',
        borderColor: atInitialConditions ? 'muted' : 'primary',
        bg: 'background',
      }}
    >
      <Reset sx={{ strokeWidth: 1.75, width: 20, height: 20 }} />
    </IconButton>
  );
};

export default ZoomReset;
