import React from 'react'
import { Box } from 'theme-ui'

const Square = ({ closed, ...props }) => {
  const style = { vectorEffect: 'non-scaling-stroke' }
  return (
    <Box
      as='svg'
      viewBox='0 0 20 20'
      fill='currentColor'
      width='10'
      height='10'
      stroke='currentColor'
      strokeWidth='1.5'
      {...props}
    >
      <rect width="100" height="100" x="10" y="10" style={style} />
    </Box>
  )
}

export default Square