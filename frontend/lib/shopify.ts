import Client from 'shopify-buy';

const domain = process.env.NEXT_PUBLIC_SHOPIFY_STORE_DOMAIN;
const storefrontAccessToken = process.env.NEXT_PUBLIC_SHOPIFY_STOREFRONT_ACCESS_TOKEN;

if (!domain || !storefrontAccessToken) {
    console.warn('⚠️  AKIRA SYSTEM: Missing Shopify credentials in .env.local');
}

export const client = Client.buildClient({
    domain: domain || '',
    storefrontAccessToken: storefrontAccessToken || '',
    apiVersion: '2024-01',
});
