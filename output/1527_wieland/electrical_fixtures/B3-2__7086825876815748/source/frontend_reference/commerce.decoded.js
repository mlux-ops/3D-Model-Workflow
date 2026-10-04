import { FetchGraphQL } from '@dropins/tools/fetch-graphql.js';
import {
  initializeConfig,
  getHeaders,
  getRootPath,
} from '@dropins/tools/lib/aem/configs.js';
import {
  getMetadata,
} from './aem.js';
import initializeDropins from './initializers/index.js';
import { getConfigValue, getLocale } from './configs.js';
import { getMagentoCache } from '../scripts/storage/util.js';
import { getCustomerType } from './storage/util.js';

/**
 * Sanitizes the given string by:
 * - convert to lower case
 * - normalize all unicode characters
 * - replace all non-alphanumeric characters with a dash
 * - remove all consecutive dashes
 * - remove all leading and trailing dashes
 *
 * @param {string} name
 * @returns {string} sanitized name
 */
function sanitizeName(name) {
  return name
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

/**
 * Fetch GraphQL Instances
 */

// Core Fetch GraphQL Instance
export const CORE_FETCH_GRAPHQL = new FetchGraphQL();

// Catalog Service Fetch GraphQL Instance
export const CS_FETCH_GRAPHQL = new FetchGraphQL();

/**
 * Constants
 */

// PATHS
export const SUPPORT_PATH = '/support';
export const CONTACT_PATH = '/contact/';
export const PRIVACY_POLICY_PATH = '/privacy-policy';
export const TERMS_CONDITIONS_PATH = '/terms-conditions';
export const RETURNS_POLICY_PATH = '/returns';

// GUEST PATHS
export const ORDER_STATUS_PATH = '/order-status';
export const ORDER_DETAILS_PATH = '/order-details';
export const RETURN_DETAILS_PATH = '/return-details';
export const INVOICE_DETAILS_PATH = '/invoice-details';
export const CREATE_RETURN_PATH = '/create-return';
export const SALES_GUEST_VIEW_PATH = '/sales/guest/view/';
export const PROJECTS_DETAILS_PATH = '/project-details';
export const PROJECTS_PATH = '/projects';
export const QUOTE_DETAILS_PATH = '/quote-details';

// CUSTOMER PATHS
export const CUSTOMER_PATH = '/customer';
export const CUSTOMER_CREATE_RETURN_PATH = `${CUSTOMER_PATH}${CREATE_RETURN_PATH}`;
export const CUSTOMER_ORDERS_PATH = `${CUSTOMER_PATH}/orders`;
export const CUSTOMER_INVOICES_PATH = `${CUSTOMER_PATH}/invoices`;
export const CUSTOMER_RETURNS_PATH = `${CUSTOMER_PATH}/returns`;
export const CUSTOMER_ORDER_DETAILS_PATH = `${CUSTOMER_PATH}${ORDER_DETAILS_PATH}`;
export const CUSTOMER_INVOICE_DETAILS_PATH = `${CUSTOMER_PATH}${INVOICE_DETAILS_PATH}`;
export const CUSTOMER_QUOTES_PATH = `${CUSTOMER_PATH}/quotes`;
export const CUSTOMER_QUOTE_DETAILS_PATH = `${CUSTOMER_PATH}${QUOTE_DETAILS_PATH}`;
export const CUSTOMER_ACCOUNT_DOWNLOADS = `${CUSTOMER_PATH}/downloads`;
export const CUSTOMER_RETURN_DETAILS_PATH = `${CUSTOMER_PATH}${RETURN_DETAILS_PATH}`;
export const CUSTOMER_ADDRESS_PATH = `${CUSTOMER_PATH}/address`;
export const CUSTOMER_ADDRESS_EDIT = `${CUSTOMER_ADDRESS_PATH}/edit`;
export const CUSTOMER_ADDRESS_NEW = `${CUSTOMER_ADDRESS_PATH}/new`;
export const CUSTOMER_LOGIN_PATH = `${CUSTOMER_PATH}/account/login`;
export const CUSTOMER_ACCOUNT_PATH = `${CUSTOMER_PATH}/account`;
export const CUSTOMER_ACCOUNT_EDIT = `${CUSTOMER_ACCOUNT_PATH}/edit`;
export const CUSTOMER_FORGOTPASSWORD_PATH = `${CUSTOMER_PATH}/account/forgotpassword`;
export const SALES_ORDER_VIEW_PATH = '/sales/order/view/';
export const CUSTOMER_CREATE_PATH = `${CUSTOMER_PATH}/account/create`;
export const CUSTOMER_REQUEST_PATH = '/company/account/create';
export const CUSTOMER_REQUISITION_LISTS_PATH = `${CUSTOMER_PATH}/requisition-lists`;
export const CUSTOMER_REQUISITION_LIST_DETAILS_PATH = `${CUSTOMER_PATH}/requisition-list-view`;
export const CUSTOMER_NEGOTIABLE_QUOTE_PATH = `${CUSTOMER_PATH}/negotiable-quote`;
export const CUSTOMER_NEGOTIABLE_QUOTE_TEMPLATE_PATH = `${CUSTOMER_PATH}/negotiable-quote-template`;
export const CUSTOMER_PROJECTS_DETAIL_PATH = `${CUSTOMER_PATH}${PROJECTS_DETAILS_PATH}`;
export const CUSTOMER_PROJECTS_PATH = `${CUSTOMER_PATH}${PROJECTS_PATH}`;
export const CUSTOMER_LOGOUT_PATH = `${CUSTOMER_PATH}/account/logout`;
export const CUSTOMER_WALLET_PATH = `${CUSTOMER_PATH}/wallet`;
export const CUSTOMER_INVENTORY_PATH = `${CUSTOMER_PATH}/inventory`;
export const CUSTOMER_PAYMENT_METHODS_PATH = `${CUSTOMER_PATH}/payment-methods`;
export const CUSTOMER_CREDITMEMOS_PATH = `${CUSTOMER_PATH}/credit-memos`;
export const COMPANY_PROFILE = '/company/profile';
export const COMPANY_PROFILE_EDIT = '/company/profile/edit';
export const COMPANY_USERS = '/company/users';
export const CUSTOMER_PAYMENTS_PATH = `${CUSTOMER_PATH}/payments`;
export const REQUEST_TO_ORDER_PATH = `${CUSTOMER_PATH}/request-to-order`;

// TRACKING URL
export const UPS_TRACKING_URL = 'https://www.ups.com/track';

// CUSTOMER B2B PATHS
export const CUSTOMER_PO_RULES_PATH = `${CUSTOMER_PATH}/approval-rules`;
export const CUSTOMER_PO_RULE_FORM_PATH = `${CUSTOMER_PATH}/approval-rule`;
export const CUSTOMER_PO_RULE_DETAILS_PATH = `${CUSTOMER_PATH}/approval-rule-details`;
export const CUSTOMER_PO_LIST_PATH = `${CUSTOMER_PATH}/purchase-orders`;
export const CUSTOMER_PO_DETAILS_PATH = `${CUSTOMER_PATH}/purchase-order-details`;

// FILE UPLOAD
export const ACCEPTED_FILE_TYPES = [
  'application/msword', // .doc
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
  'application/vnd.ms-excel', // .xls
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
  'application/pdf', // .pdf
  'text/plain', // .txt
  'image/jpeg', // .jpeg, .jpg
  'image/png', // .png
];

/**
 * Decorates links.
 * @param {string} [link] url to be localized
 * @returns {string} - The localized link
 */
export function rootLink(link) {
  const root = getRootPath().replace(/\/$/, '');

  const { countryCode: region } = getLocale(link);

  const localizedRoot = region && !root.includes(`/${region}`) ? `${root}/${region}` : root;

  // If the link is already localized, do nothing
  if (link.startsWith(localizedRoot)) return link;
  return `${localizedRoot}${link}`;
}

/* Common query fragments */
export const priceFieldsFragment = `fragment priceFields on ProductViewPrice {
  roles
  regular {
      amount {
          currency
          value
      }
  }
  final {
      amount {
          currency
          value
      }
  }
}`;

/* Queries PDP */
export const refineProductQuery = `query RefineProductQuery($sku: String!, $optionIds: [String!]!) {
  refineProduct(
    sku: $sku,
    optionIds: $optionIds
  ) {
    images(roles: []) {
      url
      roles
      label
    }
    ... on SimpleProductView {
      price {
        ...priceFields
      }
    }
    addToCartAllowed
  }
}
${priceFieldsFragment}`;

export const productDetailQuery = `query ProductQuery($sku: String!) {
  products(skus: [$sku]) {
    __typename
    externalId
    sku
    name
    description
    shortDescription
    urlKey
    inStock
    metaTitle
    metaKeyword
    metaDescription
    images(roles: []) {
      url
      label
      roles
    }
    attributes(roles: []) {
      name
      label
      value
      roles
    }
    ... on SimpleProductView {
      price {
        ...priceFields
      }
    }
    ... on ComplexProductView {
      options {
        id
        title
        required
        values {
          id
          title
          inStock
          ...on ProductViewOptionValueSwatch {
            type
            value
          }
        }
      }
      priceRange {
        maximum {
          ...priceFields
        }
        minimum {
          ...priceFields
        }
      }
    }
  }
  variants(sku: $sku) {
    variants {
    selections
      product {
        __typename
        sku
        name
        urlKey
        inStock
        images(roles: "thumbnail") {
          url
          label
          roles
        }
        attributes(roles: []) {
          name
          label
          value
          roles
        }
        ... on SimpleProductView {
          price {
            ...priceFields
          }
        }
      }
    }
    cursor
  }
}
${priceFieldsFragment}`;

const variantsQuery = `query($sku: String!, $optionIds: [String!], $pageSize: Int, $cursor: String) {
  variants(sku: $sku, optionIds: $optionIds, pageSize: $pageSize, cursor: $cursor) {
    variants {
    selections
      product {
        __typename
        sku
        name
        urlKey
        inStock
        images(roles: "thumbnail") {
          url
          label
          roles
        }

      }
    }
    cursor
  }
}
`;

function getRestProductAttribute(product, attributeCode) {
  return product.custom_attributes?.find(
    (attribute) => attribute.attribute_code === attributeCode,
  )?.value;
}

function getRestProductImageUrl(product, storeUrl) {
  const imagePath = getRestProductAttribute(product, 'image')
    || product.media_gallery_entries?.find((entry) => !entry.disabled)?.file
    || '';

  if (!imagePath || imagePath === 'no_selection') {
    return '';
  }

  if (imagePath.startsWith('http')) {
    return imagePath;
  }

  const normalizedStoreUrl = storeUrl.endsWith('/') ? storeUrl : `${storeUrl}/`;
  const imageFile = imagePath.startsWith('/') ? imagePath : `/${imagePath}`;
  return `${normalizedStoreUrl}media/catalog/product${imageFile}`;
}

function getRestProductPrice(product) {
  const price = Number(product.price);
  return Number.isFinite(price) && price > 0 ? price : null;
}

async function getConfigurableChildData(product, storeUrl, headers) {
  const parentPrice = getRestProductPrice(product);
  const fallbackPriceRange = parentPrice !== null
    ? { min: parentPrice, max: parentPrice }
    : null;
  const childrenUrl = new URL(
    `rest/V1/configurable-products/${encodeURIComponent(product.sku)}/children`,
    storeUrl,
  );

  try {
    const response = await fetch(childrenUrl, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      return { priceRange: fallbackPriceRange, baseImageUrl: '' };
    }

    const children = await response.json();
    const childItems = (Array.isArray(children) ? children : children.items || [])
      .filter((child) => Number(child.status) === 1);
      // Use the image of the child flagged as the base code display product.
    // `basecodedisplayimage` is a non-zero value on the display child and "0"
    // (or absent) on the others.
    const baseChild = childItems.find((child) => {
      const flag = getRestProductAttribute(child, 'basecodedisplayimage');
      return flag != null && String(flag) !== '' && Number(flag) !== 0;
    });
    const baseImageUrl = baseChild ? getRestProductImageUrl(baseChild, storeUrl) : '';

    const childPrices = childItems
      .map((child) => getRestProductPrice(child))
      .filter((price) => price !== null);

    const priceRange = childPrices.length
      ? { min: Math.min(...childPrices), max: Math.max(...childPrices) }
      : fallbackPriceRange;

    return { priceRange, baseImageUrl };
  } catch {
    return { priceRange: fallbackPriceRange, baseImageUrl: '' };
  }
}

function transformRestRelatedProduct(product, storeUrl, currency, childData) {
  const fallbackPrice = getRestProductPrice(product) ?? 0;
  const minRegularPrice = childData?.priceRange?.min ?? fallbackPrice;
  const maxRegularPrice = childData?.priceRange?.max ?? minRegularPrice;
  const imageUrl = childData?.baseImageUrl || getRestProductImageUrl(product, storeUrl);

  return {
    sku: product.sku,
    designer: getRestProductAttribute(product, 'designer') || '',
    relatives: getRestProductAttribute(product, 'relatives') || '',
    name: product.name,
    price: {
      regularPrice: {
        amount: {
          currency,
          value: minRegularPrice,
        },
        minimumAmount: {
          currency,
          value: minRegularPrice,
        },
        maximumAmount: {
          currency,
          value: maxRegularPrice,
        },
      },
    },
    image: {
      url: imageUrl,
    },
    url_key: getRestProductAttribute(product, 'url_key') || '',
  };
}

function setRestProductFilter(apiUrl, groupIndex, field, value, conditionType) {
  const filterPath = `searchCriteria[filter_groups][${groupIndex}][filters][0]`;
  apiUrl.searchParams.set(`${filterPath}[field]`, field);
  apiUrl.searchParams.set(`${filterPath}[value]`, value);
  apiUrl.searchParams.set(`${filterPath}[condition_type]`, conditionType);
}

const accessoriesProductsQuery = `query ProductsBySkus($skus: [String!]!) {
  products(filter: { sku: { in: $skus } }) {
    items {
      sku
      name
      price {
        regularPrice {
          amount {
            currency
            value
          }
        }
      }
      image {
        url
      }
      url_key
    }
  }
}`;

export const bulbProductDetailQuery = `query($phrase:String!) {
  productSearch(phrase:$phrase){
      items {
          productView {
              description
              id
              name
              attributes(roles: []) {
                  name
                  label
                  value
                  roles
                  }
              sku
          }
      }
  }
}`;

/* Common functionality */

export async function performCatalogServiceQuery(query, variables) {
  const headers = {
    'Content-Type': 'application/json',
    'Magento-Environment-Id': await getConfigValue('commerce-environment-id'),
    'Magento-Website-Code': await getConfigValue('commerce-website-code'),
    'Magento-Store-View-Code': await getConfigValue('commerce-store-view-code'),
    'Magento-Store-Code': await getConfigValue('commerce-store-code'),
    'Magento-Customer-Group': await getConfigValue('commerce-customer-group'),
    'x-api-key': await getConfigValue('commerce-x-api-key'),
  };

  const apiCall = new URL(await getConfigValue('commerce-endpoint'));
  apiCall.searchParams.append('query', query.replace(/(?:\r\n|\r|\n|\t|[\s]{4})/g, ' ')
    .replace(/\s\s+/g, ' '));
  apiCall.searchParams.append('variables', variables ? JSON.stringify(variables) : null);

  const response = await fetch(apiCall, {
    method: 'GET',
    headers,
  });

  if (!response.ok) {
    return null;
  }

  const queryResponse = await response.json();

  return queryResponse.data;
}

export function getSignInToken() {
  const magentoCache = getMagentoCache();
  return magentoCache['side-by-side']?.token;
}

export async function performMonolithGraphQLQuery(query, variables, GET = true, USE_TOKEN = false) {
  const GRAPHQL_ENDPOINT = await getConfigValue('commerce-core-endpoint');

  const headers = {
    'Content-Type': 'application/json',
    Store: await getConfigValue('commerce-store-view-code'),
  };

  if (USE_TOKEN) {
    if (typeof USE_TOKEN === 'string') {
      headers.Authorization = `Bearer ${USE_TOKEN}`;
    } else {
      const token = getSignInToken();
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
    }
  }

  let response;
  if (!GET) {
    response = await fetch(GRAPHQL_ENDPOINT, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        query: query.replace(/(?:\r\n|\r|\n|\t|[\s]{4})/g, ' ').replace(/\s\s+/g, ' '),
        variables,
      }),
    });
  } else {
    const endpoint = new URL(GRAPHQL_ENDPOINT);
    endpoint.searchParams.set('query', query.replace(/(?:\r\n|\r|\n|\t|[\s]{4})/g, ' ').replace(/\s\s+/g, ' '));
    endpoint.searchParams.set('variables', JSON.stringify(variables));
    response = await fetch(
      endpoint.toString(),
      { headers },
    );
  }

  if (!response.ok) {
    return null;
  }

  return response.json();
}

export function renderPrice(product, format, html = (strings, ...values) => strings.reduce((result, string, i) => result + string + (values[i] || ''), ''), Fragment = null, customerGroupPrices = null, companyType) {
  const { countryCode } = getLocale()
  if (product.price) {
    const { regular, final } = product.price;
    if (companyType === 'wholesale' && countryCode === 'us') {
      if (final.amount.value === 0 || regular.amount.value === 0) return;
      if (product.variants) {
        const priceRangeHtml = renderVariantPriceRange (
          product.variants,
          variant => variant.price.final.amount.value,
          format,
          html,
          Fragment
        );
        if (priceRangeHtml) return priceRangeHtml;
        if (regular.amount.value === final.amount.value) {
          return html`<span class="price-final">${format(final.amount.value)}</span>`;
        }
      } else {
        if (regular.amount.value === final.amount.value) {
          return html`<span class="price-final">${format(final.amount.value)}</span>`;
        }
      }
    } else if (companyType === 'wholesale') {
        if (product.tradeprice) {
          if (product.variants) {
            const priceRangeHtml = renderVariantPriceRange(
              product.variants,
              variant => variant.tradeprice?.final.amount.value || 0,
              format,
              html,
              Fragment
            );
            if (priceRangeHtml) return priceRangeHtml;
          }
          return html`<span class="price-final">${format(product.tradeprice.final.amount.value)}</span>`;
        }
      }

    if (companyType === 'trade') {
      if (product.tradeprice) {
        if (product.variants) {
          const variantTradePrices = product.variants.map(variant => {
            if (variant.tradeprice) {
              return variant.tradeprice.final.amount.value;
            } else {
              return 0;
            }
          });
          const variantFilteredPrices = variantTradePrices.filter(price => price !== 0);
          // Calculate minimum and maximum trade prices from the array
          const minPriceTrade = Math.min(...variantFilteredPrices);
          const maxPriceTrade = Math.max(...variantFilteredPrices);
          if (variantFilteredPrices.length > 0 && minPriceTrade !== maxPriceTrade) {
            if (product.priceRange) {
              const [minPrice, maxPrice] = product.priceRange;
              return html`
              <${Fragment}>
              <span class="price-range-sale">
                  <span class="price-regular">${format(minPrice)} - ${format(maxPrice)}</span>
                  <span class="price-range">
                      <span class="sale-label">TRADE </span>
                      ${format(minPriceTrade)} - ${format(maxPriceTrade)}
                  </span>
              </span>
              </${Fragment}>
              `;
            }
          } else {
            return html`<${Fragment}>
            <span class="price-regular">${format(regular.amount.value)}</span> <span class="price-final"><span class="sale-label">TRADE</span> ${format(product.tradeprice.final.amount.value)}</span>
            </${Fragment}>`
          }
        } else {
          return html`<${Fragment}>
          <span class="price-regular">${format(regular.amount.value)}</span> <span class="price-final"><span class="sale-label">TRADE</span> ${format(product.tradeprice.final.amount.value)}</span>
        </${Fragment}>`
        }
      }
    }
  }
  if (companyType === 'retail' || companyType === 'guest') {
    if (product.variants) {
      if (product.variants.length === 1) {
        if (product.variants[0].price.final.amount.value !== product.variants[0].price.regular.amount.value) {
          return html`<${Fragment}>
          <span class="price-regular">${format(product.variants[0].price.regular.amount.value)}</span> <span class="price-final"><span class="sale-label">SALE</span> ${format(product.variants[0].price.final.amount.value)}</span>
        </${Fragment}>`;
        } else {
          return html`<${Fragment}>
          <span class="price-final">${format(product.variants[0].price.final.amount.value)}</span>
          </${Fragment}>`;
        }
      }
    }
    if (product.priceRange && product.salePriceRange && product.price) {
      const [minPrice, maxPrice] = product.priceRange;
      const [minPriceSale, maxPriceSale] = product.salePriceRange;
      const { regular, final } = product.price;
      // Check if all variants have the same final price
      const allVariantsSamePrice = product.variants.every(variant => {
        return variant.price.final.amount.value === product.variants[0].price.final.amount.value;
      });
      if (minPriceSale === maxPriceSale) {
        if (minPrice === maxPrice) {
          if (final.amount.value === 0 || regular.amount.value === 0) {
            return;
          }
          if (regular.amount.value === final.amount.value) {
            return html`<span class="price-final">${format(final.amount.value)}</span>`;
          }
          return html`<${Fragment}>
            <span class="price-regular">${format(regular.amount.value)}</span> <span class="price-final"><span class="sale-label">SALE</span> ${format(final.amount.value)}</span>
          </${Fragment}>`;
        } else if (minPriceSale < minPrice) {
          if (final.amount.value === 0 || regular.amount.value === 0) {
            return;
          }
          return html`<${Fragment}>
            <span class="price-range-sale">
              <span class="price-regular">${format(minPrice)} - ${format(maxPrice)}</span>
              <span class="price-range">
                <span class="sale-label">SALE </span>
                ${format(minPriceSale)}
              </span>
            </span>
          </${Fragment}>`;
        } else if (minPrice < maxPrice) {
          if (allVariantsSamePrice) {
            return html`<${Fragment}>
              <span class="price-final">${format(product.variants[0].price.final.amount.value)}</span>
            </${Fragment}>`;
          } else {
            return html`<${Fragment}>
              <span class="price-range">${format(minPrice)} - ${format(maxPrice)}</span>
            </${Fragment}>`;
          }
        } else {
          if (product.variants.length === 1) {
            return html`<${Fragment}>
              <span class="price-final">${format(product.variants[0].price.final.amount.value)}</span>
            </${Fragment}>`;
          } else {
            if (allVariantsSamePrice) {
              return html`<${Fragment}>
                <span class="price-final">${format(product.variants[0].price.final.amount.value)}</span>
              </${Fragment}>`;
            } else {
              return html`<${Fragment}>
                <span class="price-range">${format(minPrice)} - ${format(maxPrice)}</span>
              </${Fragment}>`;
            }
          }
        }
      } else {
        if (allVariantsSamePrice) {
          return html`<${Fragment}>
            <span class="price-final">${format(product.variants[0].price.final.amount.value)}</span>
          </${Fragment}>`;
        }
        return html`<${Fragment}>
          <span class="price-range-sale">
            <span class="price-regular">${format(minPrice)} - ${format(maxPrice)}</span>
            <span class="price-range">
              <span class="sale-label">SALE </span>
              ${format(minPriceSale)} - ${format(maxPriceSale)}
            </span>
          </span>
        </${Fragment}>`;
      }
    }
  }

  // Simple product
  if (product.price && (countryCode === 'us' || companyType !== 'wholesale')) {
    const { regular, final } = product.price;
    if (final.amount.value === 0 || regular.amount.value === 0) {
      return;
    }
    if (product.tradeprice) {
      return html`<${Fragment}>
        <span class="price-regular">${format(final.amount.value)}</span> <span class="price-final"><span class="sale-label">TRADE</span> ${format(product.tradeprice.final.amount.value)}</span>
      </${Fragment}>`
    }
    if (regular.amount.value === final.amount.value) {
      return html`<span class="price-final">${format(final.amount.value)}</span>`;
    }
    return html`<${Fragment}>
      <span class="price-regular">${format(regular.amount.value)}</span> <span class="price-final"><span class="sale-label">SALE</span> ${format(final.amount.value)}</span>
    </${Fragment}>`;
  }

  if (product.priceRange) {
    const [regular, final] = product.priceRange;
    if (final === 0 || final === 0) {
      return;
    }
    if (regular === final) {
      return html`<${Fragment}>
      <span class="price-final">${format(final)}</span>
      </${Fragment}>`;
    } else {
      return html`<${Fragment}>
        <span class="price-range">${format(regular)} - ${format(final)}</span>
      </${Fragment}>`;
    }
  }

  // Complex product
  if (product.priceRange) {
    const { regular: regularMin, final: finalMin } = product.priceRange.minimum;
    const { final: finalMax } = product.priceRange.maximum;
    if (finalMin.amount.value === 0 || finalMax.amount.value === 0) {
      return;
    }

    if (finalMin.amount.value !== finalMax.amount.value) {
      return html`
      <div class="price-range">
        ${finalMin.amount.value !== regularMin.amount.value ? html`<span class="price-regular">${format(regularMin.amount.value)}</span>` : ''}
        <span class="price-from">${format(finalMin.amount.value)} - ${format(finalMax.amount.value)}</span>
      </div>`;
    }

    if (finalMin.amount.value !== regularMin.amount.value) {
      return html`<${Fragment}>
      <span class="price-final">${format(finalMin.amount.value)} - ${format(regularMin.amount.value)}</span>
    </${Fragment}>`;
    }

    return html`<span class="price-final">${format(finalMin.amount.value)}</span>`;
  }

  return null;
}

function renderVariantPriceRange(variants, getPriceFn, format, html, Fragment) {
  const variantFilteredPrices = variants
    .map(getPriceFn)
    .filter(price => price !== 0);

  if (variantFilteredPrices.length === 0) return null;

  const min = Math.min(...variantFilteredPrices);
  const max = Math.max(...variantFilteredPrices);

  if (min !== max) {
    return html`<${Fragment}>
      <span class="price-range">${format(min)} - ${format(max)}</span>
    </${Fragment}>`;
  }

  return null;
}

/* PDP specific functionality */

export function getSkuFromUrl() {
  const path = window.location.pathname;
  const result = path.match(/\/products\/[\w|-]+\/([\w|-]+)$/);
  // return result?.[1];
  // TODO Remove | For testing purposes
  return 'TOB5090';
  return 'KW5531';
  return 'TOB5115';
  return 'CHO2152'; // Social native gallery has only two images
}

const productsCache = {};
export async function getProduct(sku) {
  // eslint-disable-next-line no-param-reassign
  sku = sku.toUpperCase();
  if (productsCache[sku]) {
    return productsCache[sku];
  }
  const rawProductPromise = performCatalogServiceQuery(productDetailQuery, { sku });
  const productPromise = rawProductPromise.then((productData) => {
    if (!productData?.products?.[0]) {
      return null;
    }

    // TODO: Remove if not needed and separate query for variants is used
    // Alternatively return with variants data
    productData.products[0].variants = productData.variants.variants;

    return productData?.products?.[0];
  });

  productsCache[sku] = productPromise;
  return productPromise;
}
// Not currently useing Adobe Data Layer for tracking so commenting out this code
/* export async function trackHistory() {
  if (!getConsent('commerce-recommendations')) {
    return;
  }
  // Store product view history in session storage
  const storeViewCode = await getConfigValue('commerce-store-view-code');
  window.adobeDataLayer?.push((dl) => {
    dl.addEventListener('adobeDataLayer:change', (event) => {
      const key = `${storeViewCode}:productViewHistory`;
      let viewHistory = JSON.parse(window.localStorage.getItem(key) || '[]');
      viewHistory = viewHistory.filter((item) => item.sku !== event.productContext.sku);
      viewHistory.push({ date: new Date().toISOString(), sku: event.productContext.sku });
      window.localStorage.setItem(key, JSON.stringify(viewHistory.slice(-10)));
    }, { path: 'productContext' });
    dl.addEventListener('place-order', () => {
      const shoppingCartContext = dl.getState('shoppingCartContext');
      if (!shoppingCartContext) {
        return;
      }
      const key = `${storeViewCode}:purchaseHistory`;
      const purchasedProducts = shoppingCartContext.items.map((item) => item.product.sku);
      const purchaseHistory = JSON.parse(window.localStorage.getItem(key) || '[]');
      purchaseHistory.push({ date: new Date().toISOString(), items: purchasedProducts });
      window.localStorage.setItem(key, JSON.stringify(purchaseHistory.slice(-5)));
    });
  });
} */

export function setJsonLd(data, name, appendToBody = false) {
  const existingScript = document.head.querySelector(`script[data-name="${name}"]`);
  if (existingScript) {
    existingScript.innerHTML = JSON.stringify(data);
    return;
  }

  const script = document.createElement('script');
  script.type = 'application/ld+json';

  script.innerHTML = JSON.stringify(data);
  script.dataset.name = name;
  if (appendToBody) {
    document.body.appendChild(script);
  }else {
    document.head.appendChild(script);
  }
}

export async function loadErrorPage(code = 404) {
  const htmlText = await fetch(`/${code}.html`).then((response) => {
    if (response.ok) {
      return response.text();
    }
    throw new Error(`Error getting ${code} page`);
  });
  const parser = new DOMParser();
  const doc = parser.parseFromString(htmlText, 'text/html');
  document.body.innerHTML = doc.body.innerHTML;
  document.head.innerHTML = doc.head.innerHTML;

  // When moving script tags via innerHTML, they are not executed. They need to be re-created.
  const notImportMap = (c) => c.textContent && c.type !== 'importmap';
  Array.from(document.head.querySelectorAll('script'))
    .filter(notImportMap)
    .forEach((c) => c.remove());
  Array.from(doc.head.querySelectorAll('script'))
    .filter(notImportMap)
    .forEach((oldScript) => {
      const newScript = document.createElement('script');
      Array.from(oldScript.attributes).forEach(({ name, value }) => {
        newScript.setAttribute(name, value);
      });
      const scriptText = document.createTextNode(oldScript.innerHTML);
      newScript.appendChild(scriptText);
      document.head.appendChild(newScript);
    });
}
export async function getCategoryNameFromUrlKey() {
  const { data: possibleProducts } = await performMonolithGraphQLQuery(
    productBreadcrumbQuery,
    { urlKey: getUrlKeyFromUrl() },
  );
  const product = possibleProducts?.products?.items?.[0];

  if (!product) {
    return null;
  }

  const clearanceFilter = document.referrer.toLowerCase().includes('clearance')
    ? (category) => category.name.toLowerCase().includes('clearance')
    : (category) => !category.name.toLowerCase().includes('clearance');

  // find the category that matches a PLP
  const plpIndex = (await fetchIndex('query-index')).data;

  const possiblePLPs = product.categories?.filter(
    (category) => plpIndex.find((plp) => plp.path === `/${category.url_key}`),
  ).filter(clearanceFilter);

  return possiblePLPs || product.categories;
}

export function isPDP() {
  return window.location.href.match(/\/products\/[\w|-]+\/[\w|-]+/) !== null;
}

export async function getProductVariants(sku, options) {
  const response = await performCatalogServiceQuery(
    variantsQuery,
    { sku, optionIds: options || [] },
  );
  return response?.variants;
}

export async function refineProduct(sku, options) {
  const response = await performCatalogServiceQuery(
    refineProductQuery,
    { sku, optionIds: options || [] },
  );
  return response;
}

export async function getRelatedProducts(series, pageSize = 48) {
  const storeUrl = await getConfigValue('commerce-store-url');
  const token = await getConfigValue('product-accessories-token');
  const currency = await getConfigValue('commerce-base-currency-code')
    || getLocale().countryCurrency
    || 'USD';
  const apiUrl = new URL('rest/V1/products', storeUrl);
  const productFields = [
    'sku',
    'name',
    'type_id',
    'status',
    'price',
    'custom_attributes[attribute_code,value]',
    'media_gallery_entries[file,disabled]',
  ].join(',');
  const fields = `items[${productFields}],total_count`;

  setRestProductFilter(apiUrl, 0, 'relatives', series, 'eq');
  setRestProductFilter(apiUrl, 1, 'type_id', 'configurable', 'eq');
  setRestProductFilter(apiUrl, 2, 'status', '1', 'eq');
  setRestProductFilter(apiUrl, 3, 'website_id', '1', 'eq');
  apiUrl.searchParams.set('searchCriteria[pageSize]', pageSize);
  apiUrl.searchParams.set('fields', fields);

  const headers = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(apiUrl, {
    method: 'GET',
    headers,
  });

  if (!response.ok) {
    return null;
  }

  const data = await response.json();
  const childData = await Promise.all(
    (data.items || []).map(
      (product) => getConfigurableChildData(product, storeUrl, headers),
    ),
  );

  return {
    data: {
      products: {
        items: (data.items || []).map(
          (product, index) => transformRestRelatedProduct(
            product,
            storeUrl,
            currency,
            childData[index],
          ),
        ),
      },
    },
  };
}

export async function getAccessoriesBySKUs(items) {
  const itemsPromise = await items;
  if (typeof itemsPromise === 'string') {
    const skus = itemsPromise.split(",");
    const response = await performMonolithGraphQLQuery(
      accessoriesProductsQuery,
      { skus },
    );
    return response;
  }
}

function normalizeGroup(value) {
  if (!value) return '';

  const map = {
    consumer: 'non-logged-in',
    guest: 'non-logged-in',
    'not-logged-in': 'non-logged-in',
    retail: 'retail',
    trade: 'trade',
    wholesale: 'wholesale',
    employee: 'employee',
  };

  return map[value.toLowerCase()] || value.toLowerCase();
}

export async function applySectionTargeting() {
  const sections = document.querySelectorAll('[data-targetgroups]');
  if (!sections.length) return;

  const rawCustomerType = getCustomerType();
  const customerType = normalizeGroup(rawCustomerType);

  sections.forEach((section) => {
    const allowed = section.dataset.targetgroups
      .split(',')
      .map((g) => normalizeGroup(g.trim()));

    if (!allowed.includes(customerType)) {
      section.remove();
    }
  });
}

export function getProductLink(urlKey, sku) {
  if (!urlKey) {
    console.warn('getProductLink: urlKey is missing or empty', { urlKey, sku });
  }
  if (!sku) {
    console.warn('getProductLink: sku is missing or empty', { urlKey, sku });
  }
  const sanitizedUrlKey = urlKey ? sanitizeName(urlKey) : '';
  const sanitizedSku = sku ? `?selectedVariant=${sanitizeName(sku)}` : '';
  return rootLink(`/p/${sanitizedUrlKey}${sanitizedSku}`);
}

/**
 * Creates a commerce endpoint URL with query parameters including a cache-busting hash.
 * @param {Object} [customHeaders] - Optional custom headers to merge into the CB Hash
 * @returns {Promise<URL>} A promise that resolves to the endpoint URL with query parameters
 */
export async function commerceEndpointWithQueryParams(customHeaders = {}) {
  const endpoint = await getConfigValue('commerce-endpoint');
  const urlWithQueryParams = new URL(endpoint);
  const headers = {
    ...getHeaders('cs'),
    ...customHeaders,
  };
  const shortHash = createHashFromObject(headers);
  urlWithQueryParams.searchParams.append('cb', shortHash);
  return urlWithQueryParams;
}

/**
 * Initializes commerce configuration
 */
export async function initializeCommerce() {
  const configValues = await getConfigValue();
  const { isDefaultLocale, countryCode } = getLocale();
  const config = {
    "public": {}
  };
  const root = isDefaultLocale ? 'default' : `/${countryCode}/`
  config.public[root] = {
    "commerce-core-endpoint": configValues.find((cv) => cv.key === 'commerce-core-endpoint')?.value,
    "commerce-endpoint": configValues.find((cv) => cv.key === 'commerce-endpoint')?.value,
    "commerce-assets-enabled": true,
    "commerce-b2b-enabled": true,
    "commerce-companies-enabled": true,
    "headers": {
      "all": {
        "Store": configValues.find((cv) => cv.key === 'commerce-store-view-code')?.value,
      },
      "cs": {
        "Magento-Store-Code": configValues.find((cv) => cv.key === 'commerce-store-code')?.value,
        "Magento-Store-View-Code": configValues.find((cv) => cv.key === 'commerce-store-view-code')?.value,
        "Magento-Website-Code": configValues.find((cv) => cv.key === 'commerce-website-code')?.value,
        "x-api-key": configValues.find((cv) => cv.key === 'commerce-x-api-key')?.value,
        "Magento-Environment-Id": configValues.find((cv) => cv.key === 'commerce-environment-id')?.value,
        "Magento-Customer-Group": configValues.find((cv) => cv.key === 'commerce-customer-group')?.value,
      }
    },
    "analytics": {
      "base-currency-code": configValues.find((cv) => cv.key === 'commerce-base-currency-code')?.value,
      "customer-group": configValues.find((cv) => cv.key === 'commerce-customer-group')?.value,
      "environment": configValues.find((cv) => cv.key === 'commerce-environment')?.value,
      "environment-id": configValues.find((cv) => cv.key === 'commerce-environment-id')?.value,
      "root-category-id": configValues.find((cv) => cv.key === 'commerce-root-category-id')?.value,
      "store-code": configValues.find((cv) => cv.key === 'commerce-store-code')?.value,
      "store-id": configValues.find((cv) => cv.key === 'commerce-store-id')?.value,
      "store-name": configValues.find((cv) => cv.key === 'commerce-store-name')?.value,
      "store-url": configValues.find((cv) => cv.key === 'commerce-store-url')?.value,
      "store-view-code": configValues.find((cv) => cv.key === 'commerce-store-view-code')?.value,
      "store-view-id": configValues.find((cv) => cv.key === 'commerce-store-view-id')?.value,
      "store-view-name": configValues.find((cv) => cv.key === 'commerce-store-view-name')?.value,
      "website-code": configValues.find((cv) => cv.key === 'commerce-website-code')?.value,
      "website-id": configValues.find((cv) => cv.key === 'commerce-website-id')?.value,
      "website-name": configValues.find((cv) => cv.key === 'commerce-website-name')?.value
    }
  }

  // Initialize Config
  await initializeConfig(config);

  // Set Fetch GraphQL (Core)
  CORE_FETCH_GRAPHQL.setEndpoint(config.public[root]['commerce-core-endpoint']);
  CORE_FETCH_GRAPHQL.setFetchGraphQlHeaders((prev) => ({ ...prev, ...config.public[root]['headers']['all'] }));

  // Set Fetch GraphQL (Catalog Service)
  CS_FETCH_GRAPHQL.setEndpoint(config.public[root]['commerce-endpoint']);
  CS_FETCH_GRAPHQL.setFetchGraphQlHeaders((prev) => ({ ...prev, ...config.public[root]['headers']['cs'] }));

  return initializeDropins();
}

/**
 * Fetches and merges placeholder data from multiple sources with intelligent caching.
 *
 * This function retrieves placeholder data from a path-specific file and optional fallback file,
 * then merges them together. It implements request deduplication to prevent multiple simultaneous
 * requests for the same resources and caches results for optimal performance.
 *
 * @param {string} [path] - Optional path to a specific placeholders file to include in the merge.
 *                         If provided, this file's data will be merged with fallback data.
 *                         If not provided, returns all currently cached placeholders.
 * @returns {Promise<Object>} A promise that resolves the merged placeholders object.
 * @example
 * // Get all currently cached placeholders (no fetching)
 * const allPlaceholders = await fetchPlaceholders();
 *
 * // Fetch placeholders with specific path
 * const placeholders = await fetchPlaceholders('placeholders/auth.json');
 *
 * // Get all placeholders including newly fetched ones
 * const updatedPlaceholders = await fetchPlaceholders();
 */
export async function fetchPlaceholders(path) {
  const rootPath = getRootPath();
  const fallback = getMetadata('placeholders');
  const countryCode = getLocale().countryCode;
  window.placeholders = window.placeholders || {};

  // Track pending requests to prevent duplicate fetches
  window.placeholders._pending = window.placeholders._pending || {};

  // Initialize merged results storage as a single merged object
  window.placeholders._merged = window.placeholders._merged || {};

  // If no path is provided, return the merged placeholders
  if (!path) {
    return Promise.resolve(window.placeholders._merged || {});
  }

  // Create cache key for this specific combination
  const cacheKey = [path, fallback].filter(Boolean).join('|');

  // Prevent empty cache keys
  if (!cacheKey) {
    return Promise.resolve({});
  }

  // Check if there's already a pending request for this combination
  if (window.placeholders._pending[cacheKey]) {
    return window.placeholders._pending[cacheKey];
  }

  // fetch placeholders
  const fetchPromise = new Promise((resolve) => {
    const promises = [];

    // Helper function to get or create fetch promise for a single resource
    const getOrCreateFetch = (url, resourceCacheKey) => {
      // Check if already cached
      if (window.placeholders[resourceCacheKey]) {
        return Promise.resolve(window.placeholders[resourceCacheKey]);
      }

      // Check if already pending
      if (window.placeholders._pending[resourceCacheKey]) {
        return window.placeholders._pending[resourceCacheKey];
      }

      // Create new fetch promise
      const resourceFetchPromise = fetch(`${url}?sheet=data`).then(async (response) => {
        if (response.ok) {
          const data = await response.json();
          // Cache the response
          window.placeholders[resourceCacheKey] = data;
          return data;
        }
        console.warn(`Failed to fetch placeholders from ${url}: HTTP ${response.status} ${response.statusText}`);
        return {};
      }).catch((error) => {
        console.error(`Error fetching placeholders from ${url}:`, error);
        return {};
      }).finally(() => {
        // Remove from pending
        delete window.placeholders._pending[resourceCacheKey];
      });

      // Store pending promise
      window.placeholders._pending[resourceCacheKey] = resourceFetchPromise;
      return resourceFetchPromise;
    };

    // path
    if (path) {
      const pathUrl = rootPath.replace(
        /\/$/,
        rootPath.includes(countryCode)
          ? `/${path}`
          : `/${countryCode}/${path}`,
      );
      promises.push(getOrCreateFetch(pathUrl, path));
    }

    // fallback - only if it exists from overrides
    if (fallback) {
      promises.push(getOrCreateFetch(fallback, fallback));
    }

    Promise.all(promises)
      // process json from sources and combine them
      .then((jsons) => {
        // Early return if no data
        const hasData = jsons.some((json) => json.data?.length > 0);
        if (!hasData) {
          console.warn(`No placeholder data found for path: ${path}${fallback ? ` and fallback: ${fallback}` : ''}`);
          resolve({});
          return;
        }

        // Create data object where later values override earlier ones
        const data = {};

        // Process all JSONs in one pass
        jsons.forEach((json) => {
          if (json.data?.length) {
            json.data.forEach(({ Key, Value }) => {
              if (Key && Value !== undefined) {
                data[Key] = Value;
              }
            });
          }
        });

        // Early return if no valid data
        if (Object.keys(data).length === 0) {
          console.warn(`No valid placeholder data found after processing for path: ${path}${fallback ? ` and fallback: ${fallback}` : ''}`);
          resolve({});
          return;
        }

        // Convert data object to placeholders object with nested structure
        const placeholders = {};

        Object.entries(data).forEach(([Key, Value]) => {
          const keys = Key.split('.');
          const lastKey = keys.pop();
          let target = placeholders;

          // Navigate/create nested structure
          keys.forEach((key) => {
            target[key] = target[key] || {};
            target = target[key];
          });

          // Set the final value
          target[lastKey] = Value;
        });

        // Merge the new placeholders into the global merged object
        const merged = Object.assign(window.placeholders._merged, placeholders);

        resolve(merged);
      })
      .catch((error) => {
        console.error(`Error loading placeholders for path: ${path}${fallback ? ` and fallback: ${fallback}` : ''}`, error);
        // error loading placeholders
        resolve({});
      });
  });

  // Store the pending promise for this combination
  window.placeholders._pending[cacheKey] = fetchPromise;

  // Clean up pending promise when resolved
  fetchPromise.finally(() => {
    delete window.placeholders._pending[cacheKey];
  });

  return fetchPromise;
}

/**
 * Detects the page type based on DOM elements
 * @returns {string} The detected page type
 */
export function detectPageType() {
  if (document.body.querySelector('main .product-details')) {
    return 'Product';
  } if (document.body.querySelector('main .product-list-page')) {
    return 'Category';
  } if (document.body.querySelector('main .commerce-cart')) {
    return 'Cart';
  } if (document.body.querySelector('main .commerce-checkout')) {
    return 'Checkout';
  } if (document.body.querySelector('main .commerce-b2b-quote-checkout')) {
    return 'B2B Checkout';
  }
  return 'CMS';
}

/**
 * Extracts option UIDs from the URL search parameters.
 * @returns {string[]|undefined} Array of option UIDs, or undefined if not found
 */
export function getOptionsUIDsFromUrl() {
  return new URLSearchParams(window.location.search).get('optionsUIDs')?.split(',');
}

/**
 * Gets the product SKU from metadata or URL fallback.
 * @returns {string|null} The SKU from metadata or URL, or null if not found
 */
export function getProductSku() {
  return getMetadata('sku') || getSkuFromUrl();
}

/**
 * Preloads a file with specified attributes
 * @param {string} href - The URL to preload
 * @param {string} as - The type of resource being preloaded
 */
export function preloadFile(href, as) {
  const link = document.createElement('link');
  link.rel = 'preload';
  link.as = as;
  link.crossOrigin = 'anonymous';
  link.href = href;
  document.head.appendChild(link);
}
