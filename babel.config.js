module.exports = (api) => {
  // Cache the configuration based on the NODE_ENV
  api.cache.using(() => process.env.NODE_ENV);

  const isDev = process.env.NODE_ENV === 'development';
  const isProd = process.env.NODE_ENV === 'production';
  const isTest = process.env.NODE_ENV === 'test';

  const presets = [
    [
      '@babel/preset-env',
      {
        bugfixes: true,
        useBuiltIns: 'usage',
        corejs: { version: '3.30', proposals: true },
        modules: false,
        // Exclude transforms that make all code slower
        exclude: ['transform-typeof-symbol'],
      },
    ],
    ['@babel/preset-react', { runtime: 'automatic' }],
    '@babel/preset-typescript',
  ];

  const plugins = [
    // Stage 2
    ['@babel/plugin-proposal-decorators', { legacy: true }],
    '@babel/plugin-proposal-function-sent',
    '@babel/plugin-proposal-export-namespace-from',
    '@babel/plugin-proposal-numeric-separator',
    '@babel/plugin-proposal-throw-expressions',

    // Stage 3
    '@babel/plugin-syntax-dynamic-import',
    '@babel/plugin-syntax-import-assertions',
    ['@babel/plugin-proposal-class-properties', { loose: true }],
    ['@babel/plugin-proposal-private-methods', { loose: true }],
    ['@babel/plugin-proposal-private-property-in-object', { loose: true }],

    // Runtime
    [
      '@babel/plugin-transform-runtime',
      {
        corejs: 3,
        helpers: true,
        regenerator: true,
        useESModules: true,
      },
    ],
  ];

  if (isDev) {
    plugins.push('react-refresh/babel');
  }

  if (isProd) {
    plugins.push(['transform-react-remove-prop-types', { removeImport: true }]);
  }

  return {
    presets,
    plugins,
    // Apply conditions based on the environment
    env: {
      development: {
        presets: [['@babel/preset-react', { development: true, runtime: 'automatic' }]],
      },
      test: {
        presets: [
          ['@babel/preset-env', { targets: { node: 'current' } }],
          ['@babel/preset-react', { runtime: 'automatic' }],
        ],
      },
      production: {
        presets: [['@babel/preset-react', { runtime: 'automatic' }]],
      },
    },
  };
};
