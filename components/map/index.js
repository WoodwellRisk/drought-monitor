import { useState, useRef } from 'react'
import { useThemeUI, Box } from 'theme-ui'
import { Map as MapContainer, Raster, Fill, Line, RegionPicker } from '@carbonplan/maps'
// import DashedLine from './dashed-line'
// import DottedLine from './dotted-line'
import { Dimmer } from '@carbonplan/components'
import RegionControls from './region-controls'
import Ruler from './ruler'
import Overlays from './overlays'

const Map = ({ getters, setters, mobile }) => {
  const container = useRef(null)
  const [map, setMap] = useState(null)
  const { theme } = useThemeUI()

  const [opacity, setOpacity] = useState(1)
  const [showCountriesOutline, setShowCountriesOutline] = useState(false)
  const [showStatesOutline, setShowStatesOutline] = useState(false)

  // https://github.com/mapbox/mapbox-gl-js/blob/2b6915c8004a5b759338f3a7d92fb2882db9dd5c/src/geo/lng_lat.js#L192-L201
  // https://docs.mapbox.com/mapbox-gl-js/example/restrict-bounds/
  const bounds = [
    [-360, -60.5], // southwest
    [360, 85] // northeast
  ]

  const {
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
    showCoffee,
    showCocoa,
    showMaize,
  } = getters

  const {
    setDisplay,
    setVariable,
    setYear,
    setMonthday,
    setTime,
    setRegionData,
    setClim,
    setColormapName,
    setShowRegionPicker,
    setShowCoffee,
    setShowCocoa,
    setShowMaize,
  } = setters

  const sx = {
    label: {
      fontFamily: 'mono',
      letterSpacing: 'mono',
      textTransform: 'uppercase',
      fontSize: [1, 1, 1, 2],
      mt: [3],
    },
  }

  return (
    <Box ref={container} sx={{flexBasis: '100%', 'canvas.mapboxgl-canvas:focus': {outline: 'none', },}} >
      <MapContainer zoom={1} maxZoom={8} center={[-40, 40]} maxBounds={bounds} >
            <Fill
              color={theme.rawColors.background}
              source={'https://storage.googleapis.com/risk-maps/vector_layers/ocean'}
              variable={'ocean'}
            />

          {showStatesOutline && (
            <Line
              color={theme.colors.primary}
              source={'https://storage.googleapis.com/risk-maps/vector_layers/states'}
              variable={'states'}
              width={1}
            />
          )}

          {showCountriesOutline && (
            <Line
              color={theme.colors.primary}
              source={'https://storage.googleapis.com/risk-maps/vector_layers/countries'}
              variable={'countries'}
              width={1}
            />
          )}

            <Fill
              color={theme.rawColors.background}
              source={'https://storage.googleapis.com/risk-maps/vector_layers/lakes'}
              variable={'lakes'}
            />

            <Line
              color={theme.rawColors.primary}
              source={'https://storage.googleapis.com/risk-maps/vector_layers/lakes'}
              variable={'lakes'}
              width={1}
            />

            <Line
              color={theme.rawColors.primary}
              source={'https://storage.googleapis.com/risk-maps/vector_layers/land'}
              variable={'land'}
              width={1}
            />

          {showCoffee && (
            <>
              <Fill
                source={'https://storage.googleapis.com/risk-maps/drought-monitor/vector/coffee_mask'}
                variable={'coffee_mask'}
                color={theme.rawColors.background}
                opacity={0.7}
              />

              <Line
                source={'https://storage.googleapis.com/risk-maps/drought-monitor/vector/coffee'}
                variable={'coffee'}
                color={'black'}
                width={1}
              />
            </>
          )}

          {showCocoa && (
            <>
              <Fill
                source={'https://storage.googleapis.com/risk-maps/drought-monitor/vector/cocoa_mask'}
                variable={'cocoa_mask'}
                color={theme.rawColors.background}
                opacity={0.7}
              />

              <Line
                source={'https://storage.googleapis.com/risk-maps/drought-monitor/vector/cocoa'}
                variable={'cocoa'}
                color={'black'}
                width={1}

              />
            </>
          )}

          {showMaize && (
            <>
              <Fill
                source={'https://storage.googleapis.com/risk-maps/drought-monitor/vector/maize_mask'}
                variable={'maize_mask'}
                color={theme.rawColors.background}
                opacity={0.7}
              />

              <Line
                source={'https://storage.googleapis.com/risk-maps/drought-monitor/vector/maize'}
                variable={'maize'}
                color={'black'}
                width={1}
              />
            </>
          )}

          {showRegionPicker && (
            <RegionPicker
              color={theme.colors.primary}
              backgroundColor={theme.rawColors.background}
              fontFamily={theme.fonts.mono}
              fontSize={'14px'}
              minRadius={1}
              maxRadius={1500}
            />
          )}

          <Raster
            key={variable}
            colormap={colormap}
            clim={clim}
            display={display}
            opacity={opacity}
            mode={'texture'}
            source={`https://storage.googleapis.com/risk-maps/drought-monitor/zarr/${variable}.zarr`}
            variable={variable}
            selector={{ time }}
            regionOptions={{ setData: setRegionData }}
          />

          {!mobile && (<Ruler />)}
          <RegionControls showRegionPicker={showRegionPicker} setShowRegionPicker={setShowRegionPicker} />
          <Overlays getters={getters} setters={setters} />

      </MapContainer>

      {!mobile && (<Dimmer 
        sx={{
          display: ['initial', 'initial', 'initial', 'initial'],
          position: 'absolute',
          color: 'primary',
          right: [70],
          bottom: [20, 20, 20, 20],
        }}
      />
      )}

    </Box>
  )
}

export default Map
