import { useCallback, useEffect, useState } from 'react'
import { Box } from 'theme-ui'
import { useThemedColormap } from '@carbonplan/colormaps'
import { Colorbar, Tag, Slider } from '@carbonplan/components'
import { SidebarDivider } from '@carbonplan/layouts'
import Info from './info'

import useStore from '../store/index'

function Layers() {
  const colormapName = useStore((state) => state.colormapName)
  const colormap = useThemedColormap(colormapName)

  const minDate = useStore((state) => state.minDate)
  const maxDate = useStore((state) => state.maxDate)
  const minYear = useStore((state) => state.minYear)()
  const maxYear = useStore((state) => state.maxYear)()
  const year = useStore((state) => state.year)
  const setYear = useStore((state) => state.setYear)
  const month = useStore((state) => state.month)
  const setMonth = useStore((state) => state.setMonth)
  const monthValues = useStore((state) => state.monthValues)
  const monthIdx = useStore((state) => state.monthIdx)
  const setMonthIdx = useStore((state) => state.setMonthIdx)
  const time = useStore((state) => state.time)
  const setTime = useStore((state) => state.setTime)

  const crops = useStore((state) => state.crops)
  const cropValues = useStore((state) => state.cropValues)
  const setCropValues = useStore((state) => state.setCropValues)
  const cropLayer = useStore((state) => state.cropLayer)
  const setCropLayer = useStore((state) => state.setCropLayer)
  const setShowCropLayer = useStore((state) => state.setShowCropLayer)

  const display = useStore((state) => state.display)
  const setDisplay = useStore((state) => state.setDisplay)
  const updatingData = useStore((state) => state.updatingData)
  const showDrought = useStore((state) => state.showDrought)
  const setShowDrought = useStore((state) => state.setShowDrought)
  const setShowRegionPicker = useStore((state) => state.setShowRegionPicker)
  const setShowWarning = useStore((state) => state.setShowWarning)
  const setSliding = useStore((state) => state.setSliding)

  const sx = {
    group: {
      my: [3],
      pl: [0, 4, 5, 6],
      pr: [0, 5, 5, 6],
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
    data_description: {
      fontSize: '14px',
      color: 'primary',
    },
    data_source: {
      mt: 2,
    }
  }

  const handleDroughtChange = useCallback(() => {
    setShowDrought(!showDrought)
    setDisplay(!display)
  })

  const handleCropClick = (event) => {
    let cropName = event.target.id.slice(4,); // example: tag-coffee -> coffee
    if (cropLayer == cropName) { // this would mean that a user is un-clicking a tag of the same name
      setCropLayer("")
      if (cropName != "") {
        setCropValues({ ...cropValues, [`${cropName}`]: false })
      }
      setShowCropLayer({})
    } else { // else change between tags
      if (cropLayer == "") {
        setCropValues({ ...cropValues, [`${cropName}`]: true })
      } else {
        setCropValues({ ...cropValues, [`${cropLayer}`]: false, [`${cropName}`]: true })
      }
      setCropLayer(cropName)
      setShowCropLayer({ show: cropLayer })
    }
  }

  const handleYearChange = (event) => {
    setYear(event.target.value)
  }

  const handleMonthChange = (event) => {
    setMonthIdx(event.target.value)
  }

  useEffect(() => {
    setMonth(monthValues[monthIdx])
  }, [monthIdx])

  useEffect(() => {
    setTime(`${year}-${month}-01`)
  }, [year, month])

  useEffect(() => {
    if (year == maxYear && (new Date(time + 'T00:00:00') > new Date(maxDate + 'T00:00:00'))) {
      setShowRegionPicker(false)
      setShowWarning(true)
    } else {
      setShowWarning(false)
    }
  }, [time])

  const handleMouseDown = useCallback(() => {
    setSliding(true)
  }, [year, month])

  const handleMouseUp = useCallback(() => {
    setSliding(false)
  }, [year, month])

  return (
    <>
      <Box sx={sx.group}>
        <Box sx={{ mt: -3 }} className='var-container'>
          <Box as='h2' variant='styles.h4' className='var-title'>
            Crops <Info>
              Select any of the crops below to see an overlay of where it is grown.
            </Info>
          </Box>

          <Box className='var-layers'>
            {crops.map((crop) => {
              return (
                <Tag
                  key={crop}
                  id={`tag-${crop}`}
                  color={'primary'}
                  value={cropValues[crop]}
                  onClick={handleCropClick}
                  sx={{ mr: [2], mb: [2], borderColor: 'primary', width: 'max-content', }}
                >
                  {crop}
                </Tag>
              )
            }
            )}
          </Box>
        </Box>
      </Box>
      <SidebarDivider sx={{ width: '100%', my: 4 }} />

      <Box sx={sx.group}>
        <Box as='h2' variant='styles.h4' className='var-subtitle'>
          {'Drought Monitor'} <Info>
            <Box className='layer-description' sx={sx.data_description}>
              <Box>
                Near real-time monitor of moisture anomalies. Anomalies are measured as water balance percentiles relative to levels from 1991 to 2020. Values close to 50 represent normal conditions.
                Values below and above that mid-value indicate dryer- and wetter-than-normal conditions, respectively. Moisture anomalies are monitored on a monthly basis, from 2001 to present.
              </Box>
            </Box>
          </Info>
        </Box>

        {updatingData && (
          <Box
            className='dataUpdateMessage'
            sx={{ mr: [2], mb: [4], width: 'max-extent', color: 'red', fontStyle: 'italic' }}
          >
            The data for this site is currently being updated.
          </Box>
        )}

        <Tag
          color={'red'}
          value={updatingData == true ? false : showDrought}
          onClick={handleDroughtChange}
          sx={{ mr: [2], mb: [4], borderColor: 'red', width: 'max-content' }}
          disabled={updatingData}
        >
          Water balance
        </Tag>

        <Box sx={{ ...sx.label, }}>
          <Colorbar
            sx={{ width: '250px', display: 'inline-block', flexShrink: 1, }}
            sxClim={{ fontSize: [1, 1, 1, 2], pt: [1] }}
            width='100%'
            colormap={colormap}
            label={'percentile'}
            clim={[0.0, 100.0]}
            horizontal
            bottom
          // discrete
          />
        </Box>

        <Box sx={{ ...sx.label, mt: [4] }}>
          <Box sx={sx.label}>Year</Box>
          <Slider
            sx={{ mt: [3], mb: [2] }}
            value={year}
            onChange={handleYearChange}
            onMouseDown={handleMouseDown}
            onMouseUp={handleMouseUp}
            min={minYear}
            max={maxYear}
            step={1}
          />

          <Box
            sx={{
              textAlign: 'center',
            }}
          >
            <Box
              sx={{
                fontFamily: 'mono',
                letterSpacing: 'mono',
                fontSize: [1],
                display: 'inline-block',
                float: 'left',
              }}
            >
              {minYear}
            </Box>

            <Box
              sx={{
                fontFamily: 'mono',
                letterSpacing: 'mono',
                display: 'inline-block',
                ml: 'auto',
                mr: 'auto',
                color: 'secondary',
                transition: '0.2s',
                fontSize: [1],
              }}
            >
              {year}
            </Box>

            <Box
              sx={{
                fontFamily: 'mono',
                letterSpacing: 'mono',
                fontSize: [1],
                float: 'right',
                display: 'inline-block',
              }}
            >
              {maxYear}
            </Box>
          </Box>
        </Box>

        <Box sx={{ ...sx.label, mt: [4] }}>
          <Box sx={sx.label}>Month</Box>
          <Slider
            sx={{ mt: [3], mb: [2] }}
            value={monthIdx}
            onChange={handleMonthChange}
            onMouseDown={handleMouseDown}
            onMouseUp={handleMouseUp}
            min={0}
            max={11}
            step={1}
          />

          <Box
            sx={{
              textAlign: 'center',
            }}
          >
            <Box
              sx={{
                fontFamily: 'mono',
                letterSpacing: 'mono',
                fontSize: [1],
                display: 'inline-block',
                float: 'left',
              }}
            >
              {'01'}
            </Box>

            <Box
              sx={{
                fontFamily: 'mono',
                letterSpacing: 'mono',
                display: 'inline-block',
                ml: 'auto',
                mr: 'auto',
                color: 'secondary',
                transition: '0.2s',
                fontSize: [1],
              }}
            >
              {monthValues[monthIdx]}
            </Box>

            <Box
              sx={{
                fontFamily: 'mono',
                letterSpacing: 'mono',
                fontSize: [1],
                float: 'right',
                display: 'inline-block',
              }}
            >
              {'12'}
            </Box>
          </Box>
        </Box>

      </Box>
    </>
  )
}

export default Layers