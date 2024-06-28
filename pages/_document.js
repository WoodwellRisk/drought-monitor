import Document, { Html, Main, NextScript, Head } from 'next/document'
import { InitializeColorMode } from 'theme-ui'

export default class MyDocument extends Document {
  render() {
    return (
      <Html lang='en' className='no-focus-outline'>
        <Head>
        </Head>
        <body>
          <InitializeColorMode />
          <Main />
          <NextScript />
        </body>
      </Html>
    )
  }
}
