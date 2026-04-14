import { useCallback, useEffect, useState } from 'react';
import { Box, Button, Select, Slider, Text } from 'theme-ui';
import { useBreakpointIndex } from '@theme-ui/match-media';
import { alpha } from '@theme-ui/color';
import { useThemedColormap } from '@carbonplan/colormaps';
import { Colorbar, Filter, Tag } from '@carbonplan/components';
import SidebarDivider from './sidebar-divider';
import Info from './info';

import { useStore } from '../store/index';

function Layers() {
  const isWide = useBreakpointIndex() > 0;

  const colormapName = useStore((state) => state.colormapName);
  const colormap = useThemedColormap(colormapName);

  const windowOptions = useStore((state) => state.windowOptions);
  const setWindowOptions = useStore((state) => state.setWindowOptions);
  const setWindow = useStore((state) => state.setWindow);

  const crops = useStore((state) => state.crops);
  const cropValues = useStore((state) => state.cropValues);
  const setCropValues = useStore((state) => state.setCropValues);
  const cropLayer = useStore((state) => state.cropLayer);
  const setCropLayer = useStore((state) => state.setCropLayer);
  const setShowCropLayer = useStore((state) => state.setShowCropLayer);

  const display = useStore((state) => state.display);
  const setDisplay = useStore((state) => state.setDisplay);
  const showDrought = useStore((state) => state.showDrought);
  const setShowDrought = useStore((state) => state.setShowDrought);
  const setSliding = useStore((state) => state.setSliding);

  const validMonths = useStore((state) => state.validMonths);
  const validYears = useStore((state) => state.validYears);
  const maxHistoricalDate = useStore((state) => state.maxHistoricalDate);
  const historicalDates = useStore((state) => state.historicalDates);
  const setHistoricalDate = useStore((state) => state.setHistoricalDate);
  const historicalSliderIndex = useStore((state) => state.historicalSliderIndex);
  const setHistoricalSliderIndex = useStore((state) => state.setHistoricalSliderIndex);
  const time = useStore((state) => state.time);
  const setTime = useStore((state) => state.setTime);
  const showTimeError = useStore((state) => state.showTimeError);
  const setShowTimeError = useStore((state) => state.setShowTimeError);

  const [defaultSkipYear, defaultSkipMonth, _] = maxHistoricalDate.split('-');
  const [skipMonth, setSkipMonth] = useState(defaultSkipMonth);
  const [skipYear, setSkipYear] = useState(defaultSkipYear);

  const sx = {
    'layers-container': {
      width: '100%',
      py: 2,
      mb: [2],
    },
    group: {
      mt: [2, 2, 3],
      mb: [3],
      px: [0, 4, 5, 6],
      fontSize: [4, 4, 4, 5],
      fontFamily: 'heading',
      fontWeight: 'heading',
      lineHeight: 'h3',
      width: '100%',
    },
    label: {
      fontSize: [2, 2, 2, 3],
      fontFamily: 'heading',
      letterSpacing: 'smallcaps',
      textTransform: 'uppercase',
      mb: [2],
    },
    sublabel: {
      display: 'inline-block',
      color: 'primary',
      fontFamily: 'faux',
      letterSpacing: 'faux',
    },
    title: {
      width: '100%',
      mt: [4],
      mb: [1],
      // justifyContent: isWide ? 'space-between' : 'flex-start',
      justifyContent: 'flex-start',
      gap: isWide ? 2 : 4,
      alignItems: 'center',
      alignText: 'center',
      fontSize: isWide ? 2 : 1,
      letterSpacing: 'smallcaps',
      textTransform: 'uppercase',
    },
    subtitle: {
      color: 'gray',
      fontSize: isWide ? '0.9rem' : '0.75rem',
      mt: 1,
      mb: 1,
    },
    data_description: {
      fontSize: '14px',
      color: 'primary',
    },
    data_source: {
      mt: 2,
    },
    button: {
      alignContent: 'center',
      justifyContent: 'center',
      textAlign: 'center',
      borderRightWidth: '1px',
      borderRightStyle: 'solid',
      borderRightColor: 'primary',
      '&:last-child': {
        borderRightWidth: '0px',
      },
    },
    'time-slider': {
      width: '100%',
      mt: 3,
      mb: 3,
    },
    'slider-labels-container': {
      fontSize: 2,
      textAlign: 'center',
      pb: isWide ? 3 : 2,
    },
  };

  const handleDroughtChange = useCallback(() => {
    setShowDrought(!showDrought);
    setDisplay(!display);
  });

  const handleCropClick = (event) => {
    let cropName = event.target.id.slice(4); // example: tag-coffee -> coffee
    if (cropLayer == cropName) {
      // this would mean that a user is un-clicking a tag of the same name
      setCropLayer('');
      if (cropName != '') {
        setCropValues({ ...cropValues, [`${cropName}`]: false });
      }
      setShowCropLayer({});
    } else {
      // else change between tags
      if (cropLayer == '') {
        setCropValues({ ...cropValues, [`${cropName}`]: true });
      } else {
        setCropValues({ ...cropValues, [`${cropLayer}`]: false, [`${cropName}`]: true });
      }
      setCropLayer(cropName);
      setShowCropLayer({ show: cropLayer });
    }
  };

  const handleWindowClick = (event) => {
    let windowLabel = event.target.innerText;
    setWindow(windowLabel.substring(0, windowLabel.indexOf('-')));
  };

  const handleMouseDown = useCallback(() => {
    setSliding(true);
  }, [time]);

  const handleMouseUp = useCallback(() => {
    setSliding(false);
  }, [time]);

  useEffect(() => {
    setHistoricalDate(historicalDates[historicalSliderIndex]);
    setTime(historicalDates[historicalSliderIndex]);
  }, [historicalSliderIndex]);

  const handleSkipClick = useCallback(() => {
    let tempSliderIndex = historicalDates.indexOf(`${skipYear}-${skipMonth}-01`);
    if (tempSliderIndex != -1) {
      setShowTimeError(false);
      setHistoricalSliderIndex(tempSliderIndex);
    } else {
      setShowTimeError(true);
    }
  });

  return (
    <Box sx={sx['layers-container']}>
      <Box sx={{ ...sx.group, mt: 0 }}>
        <Box className="var-container">
          <Box sx={{ mb: [2] }} className="var-title">
            {'Crops'}{' '}
            <Info>
              <Box className="crop-description" sx={sx.data_description}>
                <Box>Select any of the crops below to see an overlay of where it is grown.</Box>
              </Box>
            </Info>
          </Box>

          <Box className="var-layers">
            {crops.map((crop) => {
              return (
                <Tag
                  key={crop}
                  id={`tag-${crop}`}
                  color={'primary'}
                  value={cropValues[crop]}
                  onClick={handleCropClick}
                  sx={{ mr: [2], mb: [2], borderColor: 'primary', width: 'max-content' }}
                >
                  {crop}
                </Tag>
              );
            })}
          </Box>
        </Box>
      </Box>
      <SidebarDivider sx={{ width: '100%', ml: 0, my: 4 }} />

      <Box sx={sx.group}>
        <Box sx={{ mb: [2] }} className="var-subtitle">
          {'Water balance'}{' '}
          <Info>
            <Box className="layer-description" sx={sx.data_description}>
              <Box>
                Near real-time monitor of moisture anomalies. Anomalies are measured as water
                balance percentiles relative to levels from 1991 to 2020. Values close to 50
                represent normal conditions. Values below and above that mid-value indicate dryer-
                and wetter-than-normal conditions, respectively. Moisture anomalies are monitored on
                a monthly basis, from 2001 to present.
              </Box>
            </Box>
          </Info>
        </Box>

        <Tag
          color={'red'}
          value={showDrought}
          onClick={handleDroughtChange}
          sx={{ mr: [2], mb: [4], borderColor: 'red', width: 'max-content' }}
        >
          Water balance
        </Tag>

        <Box sx={{ ...sx.label, mb: [4] }}>
          <Colorbar
            sx={{ width: '100%', display: 'inline-block', flexShrink: 1 }}
            sxClim={{ fontSize: [1, 1, 1, 2], pt: [1] }}
            width="100%"
            colormap={colormap}
            label={'percentile'}
            clim={[0.0, 100.0]}
            horizontal
            bottom
            // discrete
          />
        </Box>

        {/* <Box className='var-layers'>
            {['Historical', 'Forecast'].map((waterBalance) => {
              return (
                <Tag
                  key={waterBalance}
                  id={`tag-${waterBalance}`}
                  color={'primary'}
                  value={waterBalance}
                  // onClick={handleCropClick}
                  sx={{ mr: [2], mb: [2], borderColor: 'primary', width: 'max-content', }}
                >
                  {waterBalance}
                </Tag>
              )
            }
            )}
          </Box> */}

        <Box sx={{ mt: [2], mb: [2] }} className="var-subtitle">
          {'Integration window'}{' '}
          <Info>
            <Box className="layer-description" sx={sx.data_description}>
              <Box>
                The number of months taken into account when calculating water balance anomalies.
              </Box>
            </Box>
          </Info>
        </Box>

        <Filter
          values={windowOptions}
          setValues={setWindowOptions}
          labels={{ 3: '3-month', 12: '12-month' }}
          multiSelect={false}
          onClick={handleWindowClick}
          sx={{ mr: [2], mb: [4], borderColor: 'primary', width: 'max-content' }}
        />

        <Box id="time-slider-container">
          <Box sx={{ ...sx.title, mb: [2] }}>
            {`Date: ${historicalDates[historicalSliderIndex]}`}
          </Box>

          <Slider
            key={'historical-time-slider'}
            id={'time-slider'}
            sx={sx['time-slider']}
            value={historicalSliderIndex}
            onChange={(e) => setHistoricalSliderIndex(e.target.value)}
            onMouseDown={handleMouseDown}
            onMouseUp={handleMouseUp}
            min={0}
            max={historicalDates.length - 1}
            step={1}
          />

          <Box sx={sx['slider-labels-container']}>
            <Box
              sx={{
                display: 'inline-block',
                float: 'left',
              }}
            >
              {new Date(historicalDates.at(0) + 'T00:00:00').getFullYear()}
            </Box>

            <Box
              sx={{
                float: 'right',
                display: 'inline-block',
              }}
            >
              {new Date(historicalDates.at(-1) + 'T00:00:00').getFullYear()}
            </Box>
          </Box>
        </Box>

        <Box
          id={'skip-container'}
          sx={{
            ...sx.title,
            display: 'flex',
            flexWrap: 'wrap',
            height: '2rem',
            mb: 4,
          }}
        >
          <Text sx={{ fontSize: 1, flexBasis: isWide ? '100%' : 'auto', mb: 1 }}>Jump to:</Text>

          <Select
            id={'month-skip-select'}
            className={'skip-select'}
            sx={{ height: '100%', px: 3 }}
            onChange={(e) => setSkipMonth(e.target.value)}
          >
            {validMonths.map((month, idx) => {
              if (month == defaultSkipMonth) {
                return (
                  <option key={idx} value={month} selected>
                    {month}
                  </option>
                );
              } else {
                return (
                  <option key={idx} value={month}>
                    {month}
                  </option>
                );
              }
            })}
          </Select>

          <Select
            id={'year-skip-select'}
            className={'skip-select'}
            sx={{ height: '100%', px: 3 }}
            onChange={(e) => setSkipYear(e.target.value)}
          >
            {validYears.map((year, idx) => {
              if (year == defaultSkipYear) {
                return (
                  <option key={idx} value={year} selected>
                    {year}
                  </option>
                );
              } else {
                return (
                  <option key={idx} value={year}>
                    {year}
                  </option>
                );
              }
            })}
          </Select>

          <Button
            onClick={handleSkipClick}
            sx={{
              color: 'secondary',
              bg: 'background',
              outlineWidth: '1px',
              outlineStyle: 'solid',
              outlineColor: 'secondary',
              letterSpacing: 'smallcaps',
              textTransform: 'uppercase',
              '&:hover': {
                color: 'primary',
                bg: alpha('muted', 0.5),
                outlineWidth: '1px',
                outlineStyle: 'solid',
                outlineColor: 'primary',
              },
              '&:active': {
                color: 'background',
                bg: 'primary',
                outlineWidth: '1px',
                outlineStyle: 'solid',
                outlineColor: 'primary',
              },
              '&:focus:not(:active)': {
                color: 'primary',
                bg: alpha('muted', 0.5),
                outlineWidth: '1px',
                outlineStyle: 'solid',
                outlineColor: 'primary',
              },
              '&:focus:not(:hover)': {
                color: 'secondary',
                bg: 'background',
                outlineWidth: '1px',
                outlineStyle: 'solid',
                outlineColor: 'secondary',
              },
            }}
          >
            <Text>go</Text>
          </Button>
        </Box>

        {showTimeError && (
          <Box
            sx={{
              color: 'red',
              outlineWidth: '1px',
              outlineStyle: 'solid',
              outlineColor: 'red',
              mt: 4,
              py: 2,
              mx: 2,
              textAlign: 'center',
            }}
          >
            <Text sx={{ fontSize: '15px', mx: 2 }}>
              Select a time less than: {maxHistoricalDate}
            </Text>
          </Box>
        )}
      </Box>
    </Box>
  );
}

export default Layers;
