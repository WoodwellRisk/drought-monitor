const path = require('path')

module.exports = {
  output: 'export',
  trailingSlash: true,
  assetPrefix: './',
  basePath: '',

  // customize the root element
  // env: {
  //   NEXT_PUBLIC_MOUNT_ID: 'drought-map-container'
  // },

  webpack: (config, options) => {
    if (options.isServer) {
      config.externals = ['react', 'theme-ui', ...config.externals]
    }

    config.resolve.alias['react'] = path.resolve(
      __dirname,
      '.',
      'node_modules',
      'react'
    )

    config.resolve.alias['theme-ui'] = path.resolve(
      __dirname,
      '.',
      'node_modules',
      'theme-ui'
    )

      // disable code splitting to create a single JS bundle for Shiny
      if (!options.isServer) {
        config.optimization = {
          ...config.optimization,
          splitChunks: false,
        }
      }
    
    return config
  },
}