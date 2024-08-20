const endpoint = 'http://localhost:7071/demo/v0.1/';
const deployedEndpoint =
    'https://ebla-ai-demo-002.azurewebsites.net/demo/v0.1/';

export const environment = {
    production: false,
    endpoint: deployedEndpoint,
    functionDefaultKey: process.env['FUNCTION_DEFAULT_KEY'],
};
