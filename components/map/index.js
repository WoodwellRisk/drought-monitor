import { useCallback, useRef } from 'react';
import { Box, useThemeUI } from 'theme-ui';
import { useBreakpointIndex } from '@theme-ui/match-media';
import { useThemedColormap } from '@carbonplan/colormaps';

import MapProvider from './map-provider';
import Basemap from './basemap';
import Fill from './fill';
import Line from './line';
import Raster from './raster';
import PointQuery from './point-query';
import LayerOrder from './layer-order';
import Loading from '../view/loading';
// import Ruler from './ruler';
import ZoomReset from './zoom-reset';
import Router from './router';

import { useStore } from '../store/index';

const Map = ({ mobile }) => {
  const isWide = useBreakpointIndex() > 0;

  const { theme } = useThemeUI();
  const container = useRef(null);

  const zoom = useStore((state) => state.zoom);
  const maxZoom = useStore((state) => state.maxZoom);
  const center = useStore((state) => state.center);
  const bounds = useStore((state) => state.bounds);

  const timePeriod = useStore((state) => state.timePeriod);
  const window = useStore((state) => state.window);
  const maxHistoricalDate = useStore((state) => state.maxHistoricalDate);

  const setHistoricalRaster = useStore((state) => state.setHistoricalRaster);
  const setForecastRaster = useStore((state) => state.setForecastRaster);

  const showRegionPicker = useStore((state) => state.showRegionPicker);
  const cropLayer = useStore((state) => state.cropLayer);
  const showCropLayer = useStore((state) => state.showCropLayer);
  const showCountriesLayer = useStore((state) => state.showCountriesLayer);
  const showStatesLayer = useStore((state) => state.showStatesLayer);

  const sx = {
    label: {
      fontFamily: 'mono',
      letterSpacing: 'mono',
      textTransform: 'uppercase',
      fontSize: [1, 1, 1, 2],
      mt: [3],
    },
  };

  return (
    <Box key={isWide} sx={{ flex: '1 1 auto', position: 'relative', minWidth: 0 }}>
      <MapProvider>
        <Basemap />

        <Raster
          id={`historical-raster`}
          source={`https://storage.googleapis.com/water-balance/zarr/viz/wb-h${window}-${maxHistoricalDate}.zarr`}
          opacity={timePeriod == 'forecast' ? 0 : 1}
          setRaster={setHistoricalRaster}
        />

        <Raster
          id={`forecast-raster`}
          source={`https://storage.googleapis.com/water-balance/zarr/viz/wb-f${window}-${maxHistoricalDate}.zarr`}
          opacity={timePeriod == 'forecast' ? 1 : 0}
          setRaster={setForecastRaster}
        />

        {/* 
            as the list of crop layers gets longer, we want to automate how they are re-rendered on the map
            as opposed to mannually adding a {showX && (...)} for each one. the code below works
            even though the showCropLayer state re-renders to true when switching between layers
            (i.e., its state isn't updating). however, they key={} in the Line and Fill components force the components
            to re-render. so the showCropLayer prop controls whether any crop layer is shown and the change in the 
            cropLayer prop's state controls the actual re-render between crop layers.
          */}
        {showCropLayer && cropLayer != '' && (
          <>
            <Fill
              id={`${cropLayer}-extent-mask`}
              key={`${cropLayer}_mask`}
              source={`https://storage.googleapis.com/water-balance/vector/${cropLayer}_mask`}
              variable={`${cropLayer}_mask`}
              color={theme.rawColors.secondary}
              opacity={0.5}
            />

            <Line
              id={`${cropLayer}-extent`}
              key={`${cropLayer}`}
              source={`https://storage.googleapis.com/water-balance/vector/${cropLayer}`}
              variable={`${cropLayer}`}
              color={'black'}
              width={1}
            />
          </>
        )}

        <Fill
          id={'lakes-fill'}
          source={'https://storage.googleapis.com/water-balance/vector/lakes'}
          variable={'lakes'}
          color={theme.rawColors.background}
        />

        <Line
          id={'lakes'}
          source={'https://storage.googleapis.com/water-balance/vector/lakes'}
          variable={'lakes'}
          color={theme.rawColors.primary}
          width={1}
        />

        <Fill
          id="ocean"
          source={'https://storage.googleapis.com/water-balance/vector/ocean'}
          variable={'ocean'}
          color={theme.rawColors.background}
        />

        {showStatesLayer && (
          <Line
            id="states"
            source={'https://storage.googleapis.com/water-balance/vector/states'}
            variable={'states'}
            color={'gray'}
            width={zoom < 3.5 ? 0.5 : 1}
          />
        )}

        {showCountriesLayer && (
          <Line
            id={'countries'}
            source={'https://storage.googleapis.com/water-balance/vector/countries'}
            variable={'countries'}
            color={theme.rawColors.primary}
            width={showStatesLayer && zoom > 3.5 ? 1.5 : 1}
          />
        )}

        <Line
          id={'land'}
          source={'https://storage.googleapis.com/water-balance/vector/land'}
          variable={'land'}
          color={theme.rawColors.primary}
          width={1}
        />

        {/* {showRegionPicker && isWide && (
            <RegionPicker
              color={theme.colors.primary}
              backgroundColor={theme.rawColors.background}
              fontFamily={theme.fonts.mono}
              fontSize={'14px'}
              minRadius={1}
              maxRadius={1500}
            />
          )} */}

        {showRegionPicker && isWide && <PointQuery id={'point-query'} />}

        {/* {!mobile && <Ruler />} */}

        {!mobile && <ZoomReset />}

        <Router />

        <Loading />

        <LayerOrder />
      </MapProvider>
    </Box>
  );
};

export default Map;
