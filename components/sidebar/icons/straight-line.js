import React from 'react'
import { Box } from 'theme-ui'

const StraightLine = ({ closed, ...props }) => {
  const style = { vectorEffect: 'non-scaling-stroke' }
  return (
    <Box
      as='svg'
      viewBox='0 0 24 24'
      fill='currentColor'
      width='30'
      height='10'
      stroke='currentColor'
      strokeWidth='1.5'
      {...props}
    >
      <line x1='-30' y1='13' x2='50' y2='13' style={style} />
    </Box>
  )
}

export default StraightLine