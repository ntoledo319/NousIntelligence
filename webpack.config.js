const { merge } = require('webpack-merge');
const common = require('./webpack.common.js');
const dev = require('./webpack.dev.js');
const prod = require('./webpack.prod.js');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production' || process.env.NODE_ENV === 'production';

  // Set environment for Babel and other tools
  process.env.NODE_ENV = isProduction ? 'production' : 'development';

  const config = isProduction
    ? merge(common(env, argv), prod(env, argv))
    : merge(common(env, argv), dev(env, argv));

  return config;
};
