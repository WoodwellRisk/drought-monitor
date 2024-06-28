import { Box } from 'theme-ui'

const sx = {
    data_description: {
        fontSize: '14px',
        color: 'primary',
    },
    data_source: {
        mt: 2,
    }
}

const variables = ['Drought']

const varTitles = {
    'Drought': 'Extreme drought',
}

const defaultColors = {
    'Drought': 'purple',
}

const varDescriptions = {
    'drought':
        <Box className='layer-description' sx={sx.data_description}>
            <Box>
                Drought
            </Box>
        </Box>,
}

const climRanges = {
    drought: { min: 0, max: 0.5 },
}

const defaultColormaps = {
    drought: 'warm',
}

const defaultLabels = {
    drought: 'Drought',
}

const defaultUnits = {
    drought: '',
}

export {
    variables, varTitles, varDescriptions, climRanges,
    defaultColors, defaultColormaps, defaultLabels, defaultUnits,
};