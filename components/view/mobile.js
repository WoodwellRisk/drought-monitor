import { useState } from 'react'
import { Box, Flex, Grid } from 'theme-ui'
import { alpha } from '@theme-ui/color'
import { Tray } from '@carbonplan/components'
import Map from '../map'
import Layers from '../sidebar/layers'
import Loading from './loading'

function Mobile({ expanded }) {
  const [section, setSection] = useState('map')

  return (
    <>
      {section === 'map' && (
        <Box
          sx={{
            width: 'calc(100vw)',
            height: 'calc(100vh)',
            display: 'flex',
            ml: [-3],
          }}
        >
          <Map mobile={true} />

          <Loading isWide mobile />
        </Box>
      )}

      {/* this logic will need to be a display: none call */}
      {/* <Tray
        expanded={expanded}
        sx={{
          pb: expanded ? [4] : [0],
          pt: expanded ? [5] : [0],
          // transform: expanded ? 'translateY(-64px)' : 'translateY(0)',
          transform: expanded ? 'translateY(0px)' : 'translateY(-64px)',
        }}
      >
        <Layers />
      </Tray> */}

      {/* This section defines the boxes at the bottom of the mobile view. */}
      <Box
        sx={{
          position: 'fixed',
          bottom: 0,
          width: '100%',
          bg: 'background',
          height: '64px',
          borderStyle: 'solid',
          borderWidth: '0px',
          borderTopWidth: '1px',
          borderColor: 'muted',
          fontSize: [3],
          ml: [-3],
          fontFamily: 'heading',
          letterSpacing: 'allcaps',
          textTransform: 'uppercase',
        }}
      >
        <Grid columns={[2]} gap={[0]}>
          <Flex
            onClick={() => setSection('map')}
            sx={{
              justifyContent: 'center',
              alignItems: 'center',
              height: '64px',
              borderStyle: 'solid',
              borderColor: 'muted',
              borderWidth: '0px',
              borderLeftWidth: '0px',
              borderRightWidth: '1px',
              cursor: 'pointer',
              bg: section === 'map' ? alpha('muted', 0.5) : 'background',
            }}
          >
            Map
          </Flex>

        </Grid>
      </Box>
    </>
  )
}

export default Mobile