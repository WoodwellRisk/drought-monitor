import { useEffect } from 'react';
import { Box } from 'theme-ui';
import {
  Area,
  AxisLabel,
  Chart,
  Circle,
  Grid,
  Line,
  Plot,
  Ticks,
  TickLabels,
} from '@carbonplan/charts';
import { SidebarDivider } from '@carbonplan/layouts';
import { useThemedColormap } from '@carbonplan/colormaps';
import { Colorbar } from '@carbonplan/components';
import Bar from './bar';

import { useStore } from '../../store/index';
import * as d3 from 'd3';

const TimeBar = ({ data, colormap }) => {
  const sliding = useStore((state) => state.sliding);
  const time = useStore((state) => state.time);

  const sx = {
    chart: {
      mt: [4],
      mb: [0],
      mx: 'auto',
      width: '100%',
      height: '200px',
    },
    label: {
      fontSize: [2, 2, 2, 3],
      fontFamily: 'heading',
      letterSpacing: 'smallcaps',
      textTransform: 'uppercase',
      mt: [4],
      ml: [2],
      pl: [6],
    },
  };

  let mean = data['avg'];

  // https://stackoverflow.com/questions/11258077/how-to-find-index-of-an-object-by-key-and-value-in-an-javascript-array#39810268
  const timeIndex = Object.keys(mean).findIndex((date) => date == time);

  const lengthOfTime = Object.keys(mean).length;
  const xData = Array.from(Array(lengthOfTime), (_, i) => i);
  const yMean = Object.values(mean);
  // https://stackoverflow.com/questions/22015684/zip-arrays-in-javascript
  const plotMean = xData.map((x, idx) => [x, yMean[idx]]);

  return (
    <>
      <Box sx={{ ...sx.chart }} className="chart-container">
        <Chart x={[0, lengthOfTime - 1]} y={[0, 1]} padding={{ left: 60, top: 20 }}>
          <Grid vertical horizontal />
          <Ticks left bottom />
          <TickLabels left bottom />
          <AxisLabel left>Percentile</AxisLabel>
          <AxisLabel bottom>Time</AxisLabel>
          <Plot>
            <Line
              data={[
                [timeIndex, 0],
                [timeIndex, 1],
              ]}
              color="secondary"
              sx={{
                opacity: sliding ? 1 : 0,
                strokeDasharray: 4,
                transition: 'opacity 0.15s',
              }}
            />

            <Line data={plotMean} width={1.5} color={'black'} />

            <Bar
              data={plotMean.map(([x, y]) => [x, 0.5, y])}
              color={plotMean.map((val, idx) =>
                val[1] > 0.5 ? '#64bac5' : val[1] == 0.5 ? '#0a0a0a' : '#ef7071'
              )}
              strokeWidth={0.0}
            />

            <Circle
              x={timeIndex}
              y={mean[time]}
              size={8}
              sx={{
                opacity: sliding ? 1 : 0,
                transition: 'opacity 0.15s',
              }}
            />
          </Plot>
        </Chart>
      </Box>
    </>
  );
};

export default TimeBar;
