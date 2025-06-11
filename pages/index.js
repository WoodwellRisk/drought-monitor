import { useEffect, useState } from 'react'
import { Box, useColorMode } from 'theme-ui'
import { useBreakpointIndex } from '@theme-ui/match-media'

import Layout from '../components/view/layout'
import Desktop from '../components/view/desktop'
import Mobile from '../components/view/mobile'

function Index() {
  const isWide = useBreakpointIndex() > 0
  const [expanded, setExpanded] = useState(false)
  const [colorMode, setColorMode] = useColorMode()
  const description = 'Woodwell Climate Research Center drought / crop monitor'
  const title = 'Woodwell Risk drought / crop monitor'
  const logoURL = 'https://storage.googleapis.com/risk-maps/media/woodwell-risk.png'
  
  useEffect(() => {
    setColorMode('light')
  }, [])

  return (
    <>
      {isWide && (
        <Layout
          description={description}
          title={title}
          dimmer={false}
          metadata={false}
        >
          <Desktop />
        </Layout> 
      )}
      {!isWide && (
        <Box sx={{ display: ['initial', 'none', 'none', 'none'], overflow: "hidden",}}>
          <Layout
            description={description}
            title={title}
            card={logoURL}
            dimmer={false}
            metadata={false}
            settings={{
              value: expanded,
              onClick: () => setExpanded(!expanded),
            }}
          >
            <Mobile expanded={expanded} />
          </Layout>
        </Box>
      )}
    </>
  )
}

export default Index