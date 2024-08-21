import { useCallback, useEffect, useState } from 'react'
import { useThemeUI, Box } from 'theme-ui'
import { useThemedColormap } from '@carbonplan/colormaps'
import { Colorbar, Tag, Slider } from '@carbonplan/components'
import { SidebarDivider } from '@carbonplan/layouts'
import Info from './info'

function Layers({ getters, setters, sliding, onSliding }) {
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
    showDrought,
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
    setShowDrought,
    setCropLayer,
    setShowCropLayer,
    setCropValues,
    setShowWarning,
  } = setters

  // https://javascript.info/date
  // console.log(" '01-01' < '03-12' ")
  // console.log(new Date("2003-01-01") < new Date("2003-03-12"))
  const monthDayValues = [
    '01-01', '01-15', '01-29', '02-12', '02-26', '03-12', '03-26', '04-09', '04-23',
    '05-07', '05-21', '06-04', '06-18', '07-02', '07-16', '07-30', '08-13', '08-27',
    '09-10', '09-24', '10-08', '10-22', '11-05', '11-19', '12-03', '12-17'
  ]

  const [monthDayIdx, setMonthDayIdx] = useState(0)
  const [monthDayMin, setMonthDayMin] = useState(0)
  const [monthDayMax, setMonthDayMax] = useState(monthDayValues.length - 1)

  const handleDroughtChange = useCallback(() => {
    setShowDrought((prev) => !prev)
    setDisplay((prev) => !prev)
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
      setShowCropLayer({show: cropLayer})
    }
  }

  const handleYearChange = (event) => {
    setYear(event.target.value)
  }

  const handleMonthDayChange = (event) => {
    setMonthDayIdx(event.target.value)
  }

  useEffect(() => {
    setMonthDay(monthDayValues[monthDayIdx])
  }, [monthDayIdx])

  useEffect(() => {
    setTime(`${year}-${monthDay}`)
  }, [year, monthDay])

  useEffect(() => {
    if (year == '2024' && (new Date(time) > new Date(maxDate))) {
      setShowRegionPicker(false)
      setShowWarning(true)
    } else {
      setShowWarning(false)
    }
  }, [time])

  const handleMouseDown = useCallback(() => {
    onSliding(true)
  }, [year, monthDay])

  const handleMouseUp = useCallback(() => {
    onSliding(false)
  }, [year, monthDay])

  return (
    <>
      <Box sx={sx.group}>
        <Box sx={{ mt: -3 }} className='var-container'>
          <Box as='h2' variant='styles.h4' className='var-title'>
            Crops <Info>
              Select any either coffee, cocoa, or maize to see an overlay of where it is grown.
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
                Near real-time monitor of moisture anomalies. Anomalies are measured as water balance percentiles relative to levels from 2001 to 2020. Values close to 50 represent normal conditions. 
                Values below and above that mid-value indicate dryer- and wetter-than-normal conditions, respectively. Moisture anomalies are monitored on a biweekly basis, from 2001 to present.
              </Box>
            </Box>
          </Info>
        </Box>

        <Tag
          color={'red'}
          value={showDrought}
          onClick={handleDroughtChange}
          sx={{ mr: [2], mb: [4], borderColor: 'red', width: 'max-content', }}>
          Water balance
        </Tag>

        <Box sx={{ ...sx.label, }}>
          <Colorbar
            sx={{ width: '250px', display: 'inline-block', flexShrink: 1, }}
            sxClim={{ fontSize: [1, 1, 1, 2], pt: [1] }}
            width='100%'
            colormap={useThemedColormap('redteal')}
            // colormap={hexmap}
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
            min={2001}
            max={2024}
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
              2001
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
              2024
            </Box>
          </Box>
        </Box>

        <Box sx={{ ...sx.label, mt: [4] }}>
          <Box sx={sx.label}>Biweekly period</Box>
          <Slider
            sx={{ mt: [3], mb: [2] }}
            value={monthDayIdx}
            onChange={handleMonthDayChange}
            onMouseDown={handleMouseDown}
            onMouseUp={handleMouseUp}
            min={monthDayMin}
            max={monthDayMax}
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
              {monthDayValues[monthDayMin]}
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
              {monthDayValues[monthDayIdx]}
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
              {monthDayValues[monthDayMax]}
            </Box>
          </Box>
        </Box>

      </Box>
    </>
  )
}

export default Layers