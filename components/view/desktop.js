import { Flex } from 'theme-ui';
import Sidebar from '../sidebar/index';
import Map from '../map';

function Desktop() {
  return (
    <Flex
      sx={{
        position: 'absolute',
        left: 0,
        right: 0,
        top: 0,
        bottom: 0,
        flexDirection: ['column', 'row', 'row'],
        overflow: 'hidden',
        margin: 'auto',
      }}
    >
      <Sidebar />

      <Map mobile={false} />
    </Flex>
  );
}

export default Desktop;
