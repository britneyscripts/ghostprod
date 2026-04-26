'use strict';
require('dotenv').config();

/**
 * Configuração do New Relic Node.js agent.
 * Todas as chaves secretas são lidas das variáveis de ambiente (.env),
 * mantendo seu projeto 100% seguro!
 */
exports.config = {
  app_name: ['Ghostprod-Frontend'],
  // Aqui dizemos para o New Relic pegar a chave de licença segura do sistema (.env)
  license_key: process.env.NEW_RELIC_LICENSE_KEY,
  logging: {
    level: 'info'
  },
  allow_all_headers: true,
  attributes: {
    exclude: [
      'request.headers.cookie',
      'request.headers.authorization',
      'request.headers.proxyAuthorization',
      'request.headers.setCookie*',
      'request.headers.x*',
      'response.headers.cookie',
      'response.headers.authorization',
      'response.headers.proxyAuthorization',
      'response.headers.setCookie*',
      'response.headers.x*'
    ]
  }
};
