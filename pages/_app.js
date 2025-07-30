import { ThemeUIProvider } from 'theme-ui'
import '@carbonplan/components/globals.css'
import '@carbonplan/components/fonts.css'
import '@carbonplan/maps/mapbox.css'
import './stylesheet.css'
import theme from '@carbonplan/theme'

const App = ({ Component, pageProps }) => {
  theme.fonts = {
    body: "ginto-normal",
    faux: "ginto-normal",
    heading: "ginto-normal",
    mono: "ginto-normal",
  }
  
  return (
    <ThemeUIProvider theme={theme}>
      <Component {...pageProps} />
    </ThemeUIProvider>
  )
}

export default App
