import { Box, IconButton, useThemeUI } from 'theme-ui'
import { X } from '@carbonplan/icons'

const TimeWarning = ({ mobile, time, showWarning, setShowWarning }) => {

    const { theme } = useThemeUI()

    return (
        <Box sx={{ 
            position: 'relative', 
            height: '150px', 
            width: '250px', 
            top: mobile ? '30%' : '40%',
            left: mobile ? '30%' : '40%',
            display: showWarning ? 'inline-block' : 'hidden',
            // the left alignment needs work
            // left: [
            //   '0',
            //   'calc(...)
            //   'calc(...)',
            //   'calc(...)',
            // ],
            bg: theme.rawColors.primary == '#1B1E23' ? theme.rawColors.background : theme.rawColors.primary,
            color: theme.rawColors.primary == '#1B1E23' ? theme.rawColors.primary : theme.rawColors.background,
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