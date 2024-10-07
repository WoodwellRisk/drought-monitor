import { useCallback, useRef, useState } from 'react'
import { Box, useThemeUI } from 'theme-ui'
import { useThemedColormap } from '@carbonplan/colormaps'
import { Map as MapContainer, Raster, Fill, Line, RegionPicker } from '@carbonplan/maps'
import { Dimmer } from '@carbonplan/components'
import Ruler from './ruler'
import TimeWarning from './time-warning'
import Router from './router'

import useStore from '../store/index'

const Map = ({ mobile }) => {
  const { theme } = useThemeUI()
  const container = useRef(null)
  // const [map, setMap] = useState(null)
  const zoom = useStore((state) => state.zoom)
  const maxZoom = useStore((state) => state.maxZoom)
  const center = useStore((state) => state.center)
  const bounds = useStore((state) => state.bounds)

  const variable = useStore((state) => state.variable)
  const maxDate = useStore((state) => state.maxDate)
  const time = useStore((state) => state.time)
  const opacity = useStore((state) => state.opacity)
  const clim = useStore((state) => state.clim)
  const colormapName = useStore((state) => state.colormapName)
  const colormap = useThemedColormap(colormapName).slice(0,)
  
  const showRegionPicker = useStore((state) => state.showRegionPicker)
  const setRegionData = useStore((state) => state.setRegionData)
  const setRegionDataLoading = useStore((state) => state.setRegionDataLoading)
  const display = useStore((state) => state.display)
  const cropLayer = useStore((state) => state.cropLayer)
  const showCropLayer = useStore((state) => state.showCropLayer)
  const showCountriesOutline = useStore((state) => state.showCountriesOutline)
  const showStatesOutline = useStore((state) => state.showStatesOutline)
  const showWarning = useStore((state) => state.showWarning)

  const sx = {
    label: {
      fontFamily: 'mono',
      letterSpacing: 'mono',
      textTransform: 'uppercase',
      fontSize: [1, 1, 1, 2],
      mt: [3],
    },
  }

  // this callback was modified from its source: https://github.com/carbonplan/oae-web/blob/3eff3fb99a24a024f6f9a8278add9233a31e853b/components/map.js#L93
  const handleRegionData = useCallback(
    (data) => {
      if (data.value == null) {
        setRegionDataLoading(true)
      } else if (data.value[variable]) {
        setRegionData(data.value)
        setRegionDataLoading(false)
      }
    },
    [setRegionData, setRegionDataLoading]
  )

  return (
    <Box ref={container} sx={{ flexBasis: '100%', 'canvas.mapboxgl-canvas:focus': { outline: 'none', }, }} >
      <MapContainer zoom={zoom} maxZoom={maxZoom} center={center} maxBounds={bounds} >
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
          <TimeWarning mobile={mobile} />
        )}


        {!mobile && (<Ruler />)}

        <Router />

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