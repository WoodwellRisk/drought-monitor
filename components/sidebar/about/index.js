import { Box, Text } from 'theme-ui'
import Content from './content.js'

import useStore from '../../store/index'

function About({ mobile }) {
  const showAbout = useStore((state) => state.showAbout)
  const setShowAbout = useStore((state) => state.setShowAbout)
  const toggleAbout = () => setShowAbout(!showAbout)

  return (
    <Box
      sx={{
        position: 'absolute',
        zIndex: 200,
        borderStyle: 'solid',
        borderWidth: 0,
        borderRightWidth: showAbout ? 1 : 0,
        borderColor: 'muted',
        height: '100%',
        left: [
          0,
          '320px',
          '350px',
          '400px',
        ],
        backgroundColor: 'background',
        width: [
          0,
          'calc(4 * 100vw / 8 - 8px)',
          'calc(5 * 100vw / 12 - 12px)',
          'calc(5 * 100vw / 12 - 20px)',
        ],
        transition: 'transform 0.2s',
        transform: showAbout ? 'translateX(0px)' : 'translateX(-100%)',
        overflowY: 'scroll',
        display: ['none', 'initial', 'initial'],
      }}
    >
      <Box
        sx={{
          pl: [5, 5, 5, 6],
          pr: [0, 1, 5, 6],          
          opacity: 1,
          pt: ['12px'],
          mb: [4],
        }}
      >
      {!mobile && (
        <Box
          onClick={toggleAbout}
          sx={{
            cursor: 'pointer',
            '&:hover > #arrow': {
              color: 'primary',
            },
            '&:hover > #label': {
              color: 'primary',
            },
          }}
        >
          <Text
            id='arrow'
            sx={{
              display: 'inline-block',
              fontSize: ['20px'],
              color: 'secondary',
              top: '1px',
              mr: [2],
              position: 'relative',
              transition: 'color 0.15s',
            }}
          >
            ←
          </Text>
          <Box
            as='span'
            id='label'
            sx={{
              transition: 'color 0.15s',
              fontSize: [2, 2, 2, 3],
              color: 'secondary',
            }}
          >
            Back
          </Box>
        </Box>
        )}

        <Box
          sx={{
            position: 'relative',
            top: '-3px',
          }}
        >
          <Content />
        </Box>
      </Box>
    </Box>
  )
}

export default About
