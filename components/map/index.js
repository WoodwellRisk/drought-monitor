import { useCallback, useRef, useState } from 'react'
import { Box, useThemeUI } from 'theme-ui'
import { Map as MapContainer, Raster, Fill, Line, RegionPicker } from '@carbonplan/maps'
import { Dimmer } from '@carbonplan/components'
import RegionControls from './region-controls'
import Ruler from './ruler'
import Overlays from './overlays'
import TimeWarning from './time-warning'

const Map = ({ getters, setters, mobile }) => {
  const container = useRef(null)
  const [map, setMap] = useState(null)
  const { theme } = useThemeUI()

  const [opacity, setOpacity] = useState(1)
  const [showCountriesOutline, setShowCountriesOutline] = useState(false)
  const [showStatesOutline, setShowStatesOutline] = useState(false)
  const [regionLoadingData, setRegionDataLoading] = useState(true)

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
    hexmap,
    showRegionPicker,
    crops,
    cropLayer,
    showCropLayer,
    cropValues,
    maxDate,
    showWarning,
  } = getters

  const {
    setDisplay,
    setVariable,
    setYear,
    setMonthDay,
    setTime,
    setRegionData,
    setClim,
    setColormapName,
    setShowRegionPicker,
    setCropLayer,
    setShowCropLayer,
    setCropValues,
    setShowWarning,
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

  // https://github.com/mapbox/mapbox-gl-js/blob/2b6915c8004a5b759338f3a7d92fb2882db9dd5c/src/geo/lng_lat.js#L192-L201
  // https://docs.mapbox.com/mapbox-gl-js/example/restrict-bounds/
  const bounds = [
    [-360, -60.5], // southwest
    [360, 85] // northeast
  ]

  // this callback was modified from its source: https://github.com/carbonplan/oae-web/blob/3eff3fb99a24a024f6f9a8278add9233a31e853b/components/map.js#L93
  const handleRegionData = useCallback(
    (data) => {
      // console.log(data)
      if (data.value == null) {
        setRegionDataLoading(true)
      } else if (data.value) {
        setRegionData(data.value)
        setRegionDataLoading(false)
      }
    },
    [setRegionData, setRegionDataLoading]
  )

  return (
    <Box ref={container} sx={{ flexBasis: '100%', 'canvas.mapboxgl-canvas:focus': { outline: 'none', }, }} >
      <MapContainer zoom={1} maxZoom={8} center={[-40, 40]} maxBounds={bounds} >
        <Fill
          color={theme.rawColors.background}
          source={'https://storage.googleapis.com/drought-monitor/vector/ocean'}
          variable={'ocean'}
        />

        {showStatesOutline && (
          <Line
            color={theme.rawColors.primary}
            source={'https://storage.googleapis.com/drought-monitor/vector/states'}
            variable={'states'}
            width={1}
          />
        )}

        {showCountriesOutline && (
          <Line
            color={theme.rawColors.primary}
            source={'https://storage.googleapis.com/drought-monitor/vector/countries'}
            variable={'countries'}
            width={1}
          />
        )}

        <Fill
          color={theme.rawColors.background}
          source={'https://storage.googleapis.com/drought-monitor/vector/lakes'}
          variable={'lakes'}
        />

        <Line
          color={theme.rawColors.primary}
          source={'https://storage.googleapis.com/drought-monitor/vector/lakes'}
          variable={'lakes'}
          width={1}
        />

        <Line
          color={theme.rawColors.primary}
          source={'https://storage.googleapis.com/drought-monitor/vector/land'}
          variable={'land'}
          width={1}
        />

        {/* 
          as the list of crop layers gets longer, we want to automate how they are re-rendered on the map
          as opposed to mannually adding a {showX && (...)} for each one. the code below works
          even though the showCropLayer state re-renders to true when switching between layers
          (i.e., its state isn't updating). however, they key={} in the Line and Fill components force the components
          to re-render. so the showCropLayer prop controls whether any crop layer is shown and the change in the 
          cropLayer prop's state controls the actual re-render between crop layers.
        */}
        {showCropLayer != {} && cropLayer != "" && (
          <>
            <Fill
              key={`${cropLayer}_mask`}
              source={`https://storage.googleapis.com/drought-monitor/vector/${cropLayer}_mask`}
              variable={`${cropLayer}_mask`}
              color={theme.rawColors.secondary}
              opacity={0.5}
            />

            <Line
              key={`${cropLayer}`}
              source={`https://storage.googleapis.com/drought-monitor/vector/${cropLayer}`}
              variable={`${cropLayer}`}
              color={'black'}
              width={1}
            />
          </>
        )}

        {showRegionPicker && new Date(time) <= new Date(maxDate) && (
          <RegionPicker
            color={theme.colors.primary}
            backgroundColor={theme.rawColors.background}
            fontFamily={theme.fonts.mono}
            fontSize={'14px'}
            minRadius={1}
            maxRadius={1500}
          />
        )}

        {new Date(time) <= new Date(maxDate) && (
          <Raster
            key={variable}
            colormap={colormap}
            clim={clim}
            display={display}
            opacity={opacity}
            mode={'texture'}
            source={`https://storage.googleapis.com/drought-monitor/zarr/${variable}.zarr`}
            variable={variable}
            selector={{ time }}
            regionOptions={{ setData: handleRegionData, selector: {} }}
          />
        )}

        {showWarning && (
          <TimeWarning
            mobile={mobile}
            time={time}
            showWarning={showWarning}
            setShowWarning={setShowWarning} 
          />
        )}


        {!mobile && (<Ruler />)}

        {!showWarning && new Date(time) <= new Date(maxDate) && (
          <RegionControls showRegionPicker={showRegionPicker} setShowRegionPicker={setShowRegionPicker} />
        )}

        <Overlays
          getters={{ showStatesOutline, showCountriesOutline }}
          setters={{ setShowStatesOutline, setShowCountriesOutline }}
        />

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