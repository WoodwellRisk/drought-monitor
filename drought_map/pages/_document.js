import Document, { Html, Main, NextScript, Head } from 'next/document'
import { InitializeColorMode } from 'theme-ui'

export default class MyDocument extends Document {  
  render() {
    const mountId = process.env.NEXT_PUBLIC_MOUNT_ID || '__next'

    return (
      <Html lang='en' className='no-focus-outline'>
        <Head>
        </Head>
        <body>
          <InitializeColorMode />
          {/* <Main /> */}
          {/* <div id={mountId}></div> */}
          {/* <div id="drought-map-container"></div> */}
          <div id="__next"></div>
          <NextScript />
        </body>
      </Html>
    )
  }
}
