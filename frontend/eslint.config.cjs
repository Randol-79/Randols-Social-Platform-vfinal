// Bridge config for ESLint to work under Node 20+ ESM loader
// CommonJS wrapper that reuses existing .eslintrc.json
module.exports = require('./.eslintrc.json');
