import { IconButton } from 'theme-ui'
import { keyframes } from '@emotion/react'
import { useCallback, useRef } from 'react'
import { useMapbox } from '@carbonplan/maps'
import { Reset } from '@carbonplan/icons'

import useStore from '../store/index'

const ZoomReset = () => {
  const { map } = useMapbox()
  const zoom = useStore((state) => state.zoom)
  const initialZoom = 1.3;
  const center = useStore((state) => state.center)
  const resetButton = useRef(null)

  const spin = keyframes({
    from: {
      transform: 'rotate(0turn)'
    },
    to: {
      transform: 'rotate(1turn)'
    }
  })

  const handleResetClick = useCallback((event) => {
    // reset map
    resetButton.current = event.target
    resetButton.current.classList.add('spin')
    
    if (zoom != initialZoom) {
      // map.flyTo() is having trouble going to the right lat / lon center because the map has maxBounds
      // so we need to instead fit the map to the original zoom, but we can't do the same for the center
      map.flyTo({
        // center: [-40, 40],
        zoom: initialZoom,
      })
    }
  })

  const handleAnimationEnd = useCallback(() => {
    resetButton.current.classList.remove('spin')
  })

  return (
    <IconButton
      aria-label='Reset map extent'
      onClick={handleResetClick}
      onAnimationEnd={handleAnimationEnd}
      disabled={zoom == initialZoom}
      sx={{
        stroke: 'primary', cursor: 'pointer', ml: [2],
        display: ['initial', 'initial', 'initial', 'initial'],
        position: 'absolute',
        color: (zoom == initialZoom) ? 'muted' : 'primary',
        left: [2],
        bottom: [20, 20, 20, 20],
        '.spin': {
          animation: `${spin.toString()} 1s`,
        },
      }}
    >
      <Reset sx={{ strokeWidth: 1.75, width: 20, height: 20 }} />
    </IconButton>
  )
}

export default ZoomReset