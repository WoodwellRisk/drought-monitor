import { useState, useRef } from 'react'
import { useThemeUI, Box } from 'theme-ui'
import { Map as MapContainer, Raster, Fill, Line, RegionPicker } from '@carbonplan/maps'
import { Dimmer } from '@carbonplan/components'
import RegionControls from './region-controls'
import Ruler from './ruler'
import Overlays from './overlays'

const Map = ({ getters, setters, mobile }) => {
  const container = useRef(null)
  const [map, setMap] = useState(null)
  const { theme } = useThemeUI()

  // https://github.com/mapbox/mapbox-gl-js/blob/2b6915c8004a5b759338f3a7d92fb2882db9dd5c/src/geo/lng_lat.js#L192-L201
  // https://docs.mapbox.com/mapbox-gl-js/example/restrict-bounds/
  const bounds = [
    [-360, -60.5], // southwest
    [360, 85] // northeast
  ]

  const {
    display, 
    opacity,
    variable,
    band,
    month,
    regionData,
    clim,
    colormapName,
    colormap,
    hexmap,
    showRegionPicker,
    showCountriesOutline,
    showStatesOutline,
    showCoffee,
    showCocoa,
    showMaize,
  } = getters

  const {
    setDisplay,
    setOpacity,
    setVariable,
    setBand,
    setMonth,
    setRegionData,
    setClim,
    setColormapName,
    setShowRegionPicker,
    setShowCountriesOutline,
    setShowStatesOutline,
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
              color={theme.rawColors.primary}
              source={'https://storage.googleapis.com/risk-maps/vector_layers/states'}
              variable={'states'}
              width={1}
            />
          )}

          {showCountriesOutline && (
            <Line
              color={theme.rawColors.primary}
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
                source={'https://storage.googleapis.com/drought-monitor/vector/coffee'}
                variable={'coffee'}
                color={theme.rawColors.background}
                // opacity={}
              />

              <Line
                source={'https://storage.googleapis.com/drought-monitor/vector/coffee'}
                variable={'coffee'}
                // color={theme.rawColors.background}
              />
            </>
          )}

          {showCocoa && (
            <>
              <Fill
                source={'https://storage.googleapis.com/drought-monitor/vector/cocoa'}
                variable={'cocoa'}
                color={theme.rawColors.background}
                // opacity={}
              />
              <Line
                source={'https://storage.googleapis.com/drought-monitor/vector/cocoa'}
                variable={'cocoa'}
                // color={theme.rawColors.background}
              />
            </>
          )}

          {showMaize && (
            <>
              <Fill
                source={'https://storage.googleapis.com/drought-monitor/vector/maize'}
                variable={'maize'}
                color={theme.rawColors.background}
                // opacity={}
              />
              <Line
                source={'https://storage.googleapis.com/drought-monitor/vector/maize'}
                variable={'maize'}
                // color={theme.rawColors.background}
              />
            </>
          )}

          {showRegionPicker && (
            <RegionPicker
              color={theme.colors.primary}
              backgroundColor={theme.colors.background}
              fontFamily={theme.fonts.mono}
              fontSize={'14px'}
              minRadius={1}
              maxRadius={1500}
            />
          )}

          <Raster
            colormap={colormap}
            clim={clim}
            display={display}
            opacity={opacity}
            mode={'texture'}
            source={
              `https://storage.googleapis.com/risk-maps/zarr_layers/${variable}.zarr`
            }
            variable={variable}
            selector={{band}}
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
