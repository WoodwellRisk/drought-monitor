import { Box, IconButton, useThemeUI } from 'theme-ui'
import { X } from '@carbonplan/icons'

const TimeWarning = ({ mobile, time, showWarning, setShowWarning }) => {

    const { theme, colorMode } = useThemeUI()

    return (
        <Box sx={{ 
            position: 'relative', 
            height: '150px', 
            width: '250px', 
            top: mobile ? '30%' : '40%',
            left: mobile ? '30%' : '40%',
            display: showWarning ? 'inline-block' : 'hidden',
            bg: colorMode == 'dark' ? '#ebebec' : '#1b1e23',
            color: colorMode == 'dark' ? '#1b1e23' : '#ebebec',
            border: '3px solid',
            borderColor: 'red',
            borderRadius: '10px',
          }}>
              <IconButton
                aria-label='error warning box exit'
                onClick={() => setShowWarning(false)}
                sx={{ 
                  stroke: 'primary', 
                  cursor: 'pointer', 
                  width: 24, 
                  height: 24, 
                  float: 'right' }}
              >
                <X />
              </IconButton>
            <Box sx={{
              textAlign: 'center',
              pt: [6]
            }}>
              Data is not available for {time}
            </Box>
          </Box>
    )
}

export default TimeWarning