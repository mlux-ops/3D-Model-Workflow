import { events } from '@dropins/tools/event-bus.js';
import {
  sampleRUM,
  buildBlock,
  loadHeader,
  loadHeaderProf,
  loadHeaderShop,
  loadFooter,
  decorateButtons,
  decorateIcons,
  decorateSections,
  decorateBlocks,
  decorateTemplateAndTheme,
  getMetadata,
  loadBlock, decorateBlock,
  loadCSS,
  loadScript,
  toCamelCase,
  toClassName,
  readBlockConfig,
} from './aem.js';
import {
  getProduct,
  getSkuFromUrl,
  applySectionTargeting,
  initializeCommerce,
} from './commerce.js';
import { pageContextPush } from './datalayer.js';
import { pageTypePushGtm } from './datalayer-vcgtm.js';
import { getCountries, getLocale } from './configs.js';
import {
  addMagentoCacheListener,
  updateMagentoCacheSections,
  setActiveHeader,
  isProShopEnabled,
} from './storage/util.js';
import parseSsrData from './custom/pdp-parser.js';
import pushFpUserData from './fp-userdata.js';

let pageTypePushedOnce = false;
let fpUserDataPushedOnce = false;

(function interceptManagedTags() {
  const originalFetch = window.fetch;

  window.fetch = async function fetchWithConsentLinkExtraction(...args) {
    const response = await originalFetch.apply(this, args);

    const url = args[0];

    if (
      !window.__CONSENT_LINK__
      && typeof url === 'string'
      && url.includes('/managed-tags/show')
    ) {
      response.clone().json()
        .then((data) => {
          const consentScript = data?.data?.find(
            (item) => item.type === 'js'
              && item.definition?.includes('/consent'),
          );

          const consentLink = consentScript?.definition.match(/href="([^"]+)"/)?.[1];

          if (consentLink) {
            window.__CONSENT_LINK__ = consentLink;

            window.dispatchEvent(
              new CustomEvent('consent-link-ready', {
                detail: consentLink,
              }),
            );
          }
        })
        .catch((e) => {
          console.warn('Consent link extraction failed', e);
        });
    }

    return response;
  };
}());

// Function to get the value of a query parameter by name
function getQueryParam(param) {
  const urlParams = new URLSearchParams(window.location.search);
  const value = urlParams.get(param);
  return value !== null ? value : null;
}

// Function to update the selected variant in the window.product object
export function updateSelectedVariant(selectedProduct) {
  if (!window.product || !window.product.variants) {
    console.error('Product or product variants are not defined.');
    return;
  }

  // Find the variant with the same SKU as selectedProduct
  const selectedVariant = window.product.variants
    .find((variant) => variant.sku === selectedProduct);

  if (selectedVariant) {
    window.product.selectedVariant = { ...selectedVariant };
    events.emit('variantchange');
  } else {
    console.error(`Product variant with SKU: "${selectedProduct}" was not found.`);
  }
}

export function isVariantSelected() {
  if (!window.product.selectedVariant && !!getQueryParam('selected_product') === false) {
    updateSelectedVariant(window.product.variants.find(
      (variant) => variant.images[0].img.src === window.product.images[0]?.url,
    )?.sku);
  }
  return !!getQueryParam('selected_product');
}

const LCP_BLOCKS = [
  'custom-hero',
  'product-list-page',
  'product-list-page-custom',
  'product-details',
  'commerce-cart',
  'commerce-checkout',
  'commerce-account',
  'commerce-login',
]; // add your LCP blocks to the list

window.adobeDataLayer = window.adobeDataLayer || [];

const AUDIENCES = {
  mobile: () => window.innerWidth < 600,
  desktop: () => window.innerWidth >= 600,
  // define your custom audiences here as needed
};

let pageType = 'CMS';

/**
 * Gets all the metadata elements that are in the given scope.
 * @param {String} scope The scope/prefix for the metadata
 * @returns an array of HTMLElement nodes that match the given scope
 */
export function getAllMetadata(scope) {
  return [...document.head.querySelectorAll(`meta[property^="${scope}:"],meta[name^="${scope}-"]`)]
    .reduce((res, meta) => {
      const id = toClassName(meta.name
        ? meta.name.substring(scope.length + 1)
        : meta.getAttribute('property').split(':')[1]);
      res[id] = meta.getAttribute('content');
      return res;
    }, {});
}

// Define an execution context
const pluginContext = {
  getAllMetadata,
  getMetadata,
  loadCSS,
  loadScript,
  sampleRUM,
  toCamelCase,
  toClassName,
};

/**
 * Builds hero block and prepends to main in a new section.
 * @param {Element} main The container element
 */
// eslint-disable-next-line no-unused-vars
function buildHeroBlock(main) {
  // Check if there is a manual hero block.
  // If so, do not try to build an autoblock hero.
  if (main.querySelector(['.block', '.hero'])) {
    return;
  }

  const h1 = main.querySelector('h1');
  const picture = main.querySelector('picture');
  // eslint-disable-next-line no-bitwise
  if (h1 && picture && (h1.compareDocumentPosition(picture) & Node.DOCUMENT_POSITION_PRECEDING)) {
    const section = document.createElement('div');
    section.append(buildBlock('hero', { elems: [picture, h1] }));
    main.prepend(section);
  }
}

/**
 * load fonts.css and set a session storage flag
 */
function loadFonts() {
  loadCSS('https://use.typekit.net/gyy3evs.css');
  loadCSS(`${window.hlx.codeBasePath}/styles/fonts.css`);
  try {
    if (!window.location.hostname.includes('localhost')) sessionStorage.setItem('fonts-loaded', 'true');
  } catch (e) {
    console.error('Error setting fonts-loaded flag:', e.message || e);
  }
}

// Preload images
function preloadImages(images) {
  if (images.length > 0) {
    const image = images[0];
    const baseUrl = image.url.split('?')[0];

    // srcset based on PDP gallery images sizes
    const srcset = [
      `${baseUrl}?width=384&format=webp&optimize=medium&auto=webp&quality=80&crop=false&fit=cover 768w`,
      `${baseUrl}?width=512&format=webp&optimize=medium&auto=webp&quality=80&crop=false&fit=cover 1024w`,
      `${baseUrl}?width=683&format=webp&optimize=medium&auto=webp&quality=80&crop=false&fit=cover 1366w`,
      `${baseUrl}?width=960&format=webp&optimize=medium&auto=webp&quality=80&crop=false&fit=cover 1920w`,
    ].join(', ');

    // Create a single link tag with imagesrcset and imagesizes
    const preloadLink = document.createElement('link');
    preloadLink.rel = 'preload';
    preloadLink.as = 'image';
    preloadLink.href = image.url;
    preloadLink.setAttribute('imagesrcset', srcset);
    preloadLink.setAttribute('imagesizes', '100vw');
    document.head.appendChild(preloadLink);
  }
}

// Preload the first image of each visible variant
function preloadVariantImages(variants) {
  variants.slice(0, 4).forEach((variant) => {
    if (variant.images && variant.images.length > 0) {
      const firstImage = variant.images[0].img.src;
      const baseUrl = firstImage.split('?')[0];
      const link = document.createElement('link');
      link.rel = 'preload';
      link.as = 'image';
      link.href = `${baseUrl}?width=200&format=webp&optimize=medium`;
      document.head.appendChild(link);
    }
  });
}

let MANUAL_BREADCRUMB;
function buildBreadcrumb(main) {
  if (getMetadata('breadcrumb') === 'none') {
    return;
  }

  if (getMetadata('breadcrumb') === 'auto') {
    main.classList.add('with-breadcrumb');
  } else if (document.querySelector('.breadcrumb')) {
    MANUAL_BREADCRUMB = document.querySelector('.breadcrumb');
    main.classList.add('with-breadcrumb');
  }
}

/**
 * Builds all synthetic blocks in a container element.
 * @param {Element} main The container element
 */
// eslint-disable-next-line no-unused-vars
function buildAutoBlocks(main) {
  try {
    buildBreadcrumb(document.querySelector('header'));
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error('Auto Blocking failed', error);
  }
}

/**
 * Decorates the main element.
 * @param {Element} main The main element
 */
export function decorateMain(main) {
  // hopefully forward compatible button decoration
  decorateButtons(main);
  decorateIcons(main);
  buildAutoBlocks(main);
  decorateSections(main);
  decorateBlocks(main);
}

function preloadFile(href, as) {
  const link = document.createElement('link');
  link.rel = 'preload';
  link.as = as;
  link.crossOrigin = 'anonymous';
  link.href = href;
  document.head.appendChild(link);
}

function decorateProductListPageHeader(main) {
  const headingSection = main.querySelector('h1')?.closest('.section');
  if (headingSection && !headingSection.classList.contains('plp-custom-hero-container')) {
    headingSection.classList.add('product-list-page-custom-header', 'category-results-header');
  }
}

async function loadBreadcrumb(main) {
  let wrapper;
  if (MANUAL_BREADCRUMB) {
    wrapper = MANUAL_BREADCRUMB.parentElement;
  } else if (getMetadata('breadcrumb') === 'auto') {
    wrapper = document.createElement('div');
    const block = buildBlock('breadcrumb', { elems: [document.createElement('ul')] });
    wrapper.append(block);
  } else {
    return;
  }
  main.append(wrapper);

  decorateBlock(wrapper.firstElementChild);
  await loadBlock(wrapper.firstElementChild);
}

/**
 * Load LCP block and/or wait for LCP in default content.
 * @param {Array} lcpBlocks Array of blocks
 */
async function waitForLCP(lcpBlocks) {
  const block = document.querySelector('.block');
  const hasLCPBlock = block && lcpBlocks.includes(block.dataset.blockName);
  if (hasLCPBlock) await loadBlock(block);

  document.body.style.display = null;
  const lcpCandidate = document.querySelector('main img');

  await new Promise((resolve) => {
    if (lcpCandidate && !lcpCandidate.complete) {
      lcpCandidate.setAttribute('loading', 'eager');
      lcpCandidate.addEventListener('load', resolve);
      lcpCandidate.addEventListener('error', resolve);
    } else {
      resolve();
    }
  });
}

/**
 * Gets showroom locations object.
 * @param {string} [prefix] Location of Showroom locations
 * @returns {object} Window locations object
 */
export async function fetchShowroomLocationsData(sheetName = 'default') {
  window.locations = window.locations || {};
  if (!window.locations[sheetName]) {
    window.locations[sheetName] = new Promise((resolve) => {
      fetch('/us/showrooms/showroom-locations.json')
        .then((resp) => {
          if (resp.ok) {
            return resp.json();
          }
          return {};
        })
        .then((json) => {
          const locations = json.data || [];
          // Store all location data instead of filtering by columnKey and columnValue
          window.locations = locations || []; // Assuming locations.data holds the array of rows
          resolve(window.locations);
        })
        .catch(() => {
          // Error loading locations
          window.locations = [];
          resolve(window.locations);
        });
    });
  }
  return window.locations[sheetName];
}

/**
 * Loads a block named 'geopopup' into geopopupBlock
 * @param geopopup element
 * @returns {Promise}
 */
async function loadGeopopup(geopopup) {
  const geopopupBlock = buildBlock('geopopup', '');
  geopopup.append(geopopupBlock);
  decorateBlock(geopopupBlock);
  return loadBlock(geopopupBlock);
}

/**
 * Wraps images followed by links within a matching <a> tag.
 * @param {Element} container The container element
 */
export function wrapImgsInLinks(container) {
  const pictures = container.querySelectorAll('picture');
  pictures.forEach((pic) => {
    const br = pic.nextElementSibling;
    const link = br?.nextElementSibling;
    if (link && link.tagName === 'A' && link.href) {
      link.innerHTML = pic.outerHTML;
      pic.replaceWith(link);
    }
  });
}

async function loadSocialNativeGallery() {
  const socialGalleryParent = document.querySelector('.social-native-gallery-wrapper');
  if (!socialGalleryParent) {
    return;
  }
  socialGalleryParent.style.visibility = 'hidden';

  const socialBlock = buildBlock('social-native-gallery', '');

  let olapicId = window.product.attributes.find((attr) => attr.name === 'olapic_id')?.value;
  // If id is not found in product attributes, check variants
  if (!olapicId) {
    const { variants } = window.product;
    if (variants && Object.keys(variants[0]).length > 0) {
      const variantWithOlapicId = variants.find((variant) => variant.attributes.some((attr) => attr.name === 'olapic_id'));
      olapicId = variantWithOlapicId ? variantWithOlapicId.attributes.find((attr) => attr.name === 'olapic_id').value : undefined;
    }
  }

  socialBlock.classList.add('block');
  socialBlock.innerHTML = `
    <div><div>Stream tag</div><div>${olapicId}</div></div>
    <div><div>Gallery Text</div><div>#visualcomfort</div></div>
  `;
  socialBlock.setAttribute('data-block-origin', 'pdp');
  socialGalleryParent.appendChild(socialBlock);
  decorateBlock(socialBlock);
  await loadBlock(socialBlock);
  socialGalleryParent.style.visibility = 'visible';
}

/**
 * Updates all section status in a container element.
 * @param {Element} main The container element
 */
function updateSectionsStatus(main) {
  const sections = [...main.querySelectorAll(':scope > div.section')];
  for (let i = 0; i < sections.length; i += 1) {
    const section = sections[i];
    const status = section.dataset.sectionStatus;
    if (status !== 'loaded') {
      const loadingBlock = section.querySelector(
        '.block[data-block-status="initialized"], .block[data-block-status="loading"]',
      );
      if (loadingBlock) {
        section.dataset.sectionStatus = 'loading';
        break;
      } else {
        section.dataset.sectionStatus = 'loaded';
        section.style.display = null;
        if (i === 0 && sampleRUM.enhance) {
          sampleRUM.enhance();
        }
      }
    }
  }
}

/**
 * Loads JS and CSS for all blocks in a container element.
 * @param {Element} main The container element
 */
export async function loadBlocks(main) {
  updateSectionsStatus(main);
  const blocks = [...main.querySelectorAll('div.block')];
  for (let i = 0; i < blocks.length; i += 1) {
    // eslint-disable-next-line no-await-in-loop
    await loadBlock(blocks[i]);
    updateSectionsStatus(main);
  }
}

/**
 * Wraps images with size attributes
 * @param {Element} container The container element
 */
export function wrapImgsInSize(container) {
  const images = container.querySelectorAll('img');
  images.forEach((imgElement) => {
    // Get the rendered size
    const renderedWidth = imgElement.width;
    const renderedHeight = imgElement.height;
    imgElement.setAttribute('width', renderedWidth);
    imgElement.setAttribute('height', renderedHeight);
  });
}

function insertWelcomeHeader() {
  const main = document.querySelector('#main') || document.querySelector('main');
  if (!main || document.querySelector('#welcome-header')) return;

  const { isDefaultLocale, language } = getLocale();
  const normalizedPath = window.location.pathname.replace(/\/$/, '');

  if (isDefaultLocale || normalizedPath !== `/${language}`) return;

  main.insertAdjacentHTML(
    'afterbegin',
    `<div id="welcome-header"><h3>Welcome to our ${language.toUpperCase()} Site</h3></div>`,
  );
}

/**
 * Loads everything needed to get to LCP.
 * @param {Element} doc The container element
 */
async function loadEager(doc) {
  // gtm set up
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    'gtm.start': new Date().getTime(),
    event: 'gtm.js',
  });

  loadCSS('/styles/styles.css');

  document.documentElement.lang = 'en';
  await initializeCommerce();
  decorateTemplateAndTheme();
  const main = doc.querySelector('main');
  let isProductListPage = false;
  if (main) {
    main.id = 'main';
  }
  function getActiveHeaderFromURL() {
    const path = window.location.pathname;
    if (path === '/' || path === '') {
      return 'shop';
    }

    if (path.includes('/professional') || path.includes('/lighting-experience-pro') || path.includes('/explore-landscape-collection')) {
      return 'professional';
    }

    const savedHeader = localStorage.getItem('activeHeader');
    return savedHeader || 'shop';
  }

  await updateMagentoCacheSections(['customer', 'company']);
  const isProShopHeader = isProShopEnabled();

  const headerElement = doc.querySelector('header');
  let savedHeader = 'shop';
  const { isDefaultLocale } = getLocale();
  const useProShopHeader = isProShopHeader && isDefaultLocale;

  if (useProShopHeader) {
    savedHeader = getActiveHeaderFromURL();
  }

  setActiveHeader(savedHeader);
  localStorage.setItem('activeHeader', savedHeader);

  const { pathname } = window.location;

  if (isProShopHeader && (pathname === '/' || pathname === '/us' || pathname.startsWith('/us/'))) {
    await (savedHeader === 'professional'
      ? loadHeaderProf(headerElement)
      : loadHeaderShop(headerElement));
  } else {
    await loadHeader(headerElement);
  }

  // Instrument experimentation plugin
  if (getMetadata('experiment')
    || Object.keys(getAllMetadata('campaign')).length
    || Object.keys(getAllMetadata('audience')).length) {
    // eslint-disable-next-line import-x/no-useless-path-segments
    const { loadEager: runEager } = await import('../plugins/experimentation/src/index.js');
    await runEager(document, { audiences: AUDIENCES }, pluginContext);
  }
  const metaSku = doc.querySelector('meta[name="sku"]');
  if (main && metaSku) {
    // Preload PDP Dropins assets
    preloadFile('/scripts/__dropins__/storefront-pdp/containers/ProductDetails.js', 'script');
    await parseSsrData();
    pageType = 'product_detail_page';

    // Preload images
    if (window.product && window.product.images) {
      preloadImages(window.product.images);
    }
    // Preload variant images for Options
    if (window.product.variants) {
      preloadVariantImages(window.product.variants);
    }

    // Remove pre-rendered product details
    const productOptionsElement = document.querySelector('div.product-options');
    if (productOptionsElement && productOptionsElement.parentElement) {
      productOptionsElement.parentElement.remove();
    }

    const wrapper = document.createElement('div');
    const block = buildBlock('product-details', '');
    wrapper.append(block);
    main.append(wrapper);
  } else if (document.body.querySelector('main .product-details-custom')) {
    pageType = 'product_detail_page';
    preloadFile('/blocks/product-details-custom/ProductDetailsCarousel.js', 'script');
    preloadFile('/blocks/product-details-custom/ProductDetailsSidebar.js', 'script');
    preloadFile('/blocks/product-details-custom/ProductDetailsShimmer.js', 'script');
    preloadFile('/blocks/product-details-custom/Icon.js', 'script');

    const blockConfig = readBlockConfig(document.body.querySelector('main .product-details-custom'));
    const sku = getSkuFromUrl() || blockConfig.sku;
    window.getProductPromise = getProduct(sku);
  } else if (document.body.querySelector('main .product-list-page')) {
    // TODO Remove this bracket if not using custom PLP
    pageType = 'Category';
    isProductListPage = true;
    loadCSS('/blocks/product-list-page-custom/product-list-page-custom.css');
    preloadFile('/blocks/product-list-page-custom/FacetList.js', 'script');
    preloadFile('/blocks/product-list-page-custom/ActiveFacets.js', 'script');
    preloadFile('/blocks/product-list-page-custom/ProductList.js', 'script');
    preloadFile('/scripts/widgets/search.js', 'script');
    preloadFile('/blocks/product-list-page-custom/product-list-page-custom.js', 'script');
  } else if (document.body.querySelector('main .product-list-page-custom')) {
    // TODO Remove this bracket if not using custom PLP
    pageType = 'Category';
    isProductListPage = true;
    loadCSS('/blocks/product-list-page-custom/product-list-page-custom.css');
  } else if (document.body.querySelector('main .commerce-cart')) {
    pageType = 'Cart';
  } else if (document.body.querySelector('main .commerce-checkout')) {
    pageType = 'Checkout';
  }
  if (main) {
    decorateMain(main);
    if (isProductListPage) decorateProductListPageHeader(main);
    insertWelcomeHeader();
    // add skip to main content link
    const skipLink = document.createElement('a');
    skipLink.href = '#main';
    skipLink.classList.add('skip-link');
    skipLink.textContent = 'Skip to Content';
    document.body.prepend(skipLink);
    document.body.classList.add('appear');
    if (['/', '/us/professional', '/us/custom-video-hero', '/us/lighting-experience-pro', '/us/explore-landscape-collection'].includes(window.location.pathname)) {
      document.body.classList.add('bleed-hero');
    }
    if (main.querySelector('.cms-page')) {
      document.body.classList.add('cms-page-body');
    }
  }
}

/**
 * Loads everything that doesn't need to be delayed.
 * @param {Element} doc The container element
 */
async function loadLazy(doc) {
  loadBreadcrumb(doc.querySelector('header'));
  const main = doc.querySelector('main');
  const sections = document.querySelectorAll('[data-targetgroups]');
  if (sections.length) {
    await applySectionTargeting();
  }

  const countries = await getCountries();
  sessionStorage.setItem('countries', JSON.stringify(countries));
  loadFonts();
  loadBlocks(main);
  await waitForLCP(LCP_BLOCKS);
  events.emit('eds/lcp', true);
  const { hash } = window.location;
  const element = hash ? doc.getElementById(hash.substring(1)) : false;
  if (hash && element) element.scrollIntoView();

  loadCSS(`${window.hlx.codeBasePath}/styles/lazy-styles.css`);
  loadFooter(doc.querySelector('footer'));
  loadGeopopup(doc.querySelector('footer'));

  if (sessionStorage.getItem('acdl:debug')) {
    import('./acdl/validate.js');
  }

  // Implement experimentation preview pill
  if ((getMetadata('experiment')
    || Object.keys(getAllMetadata('campaign')).length
    || Object.keys(getAllMetadata('audience')).length)) {
    // eslint-disable-next-line import-x/no-useless-path-segments
    const { loadLazy: runLazy } = await import('../plugins/experimentation/src/index.js');
    await runLazy(document, { audiences: AUDIENCES }, pluginContext);
  }
}

/**
 * Loads everything that happens a lot later,
 * without impacting the user experience.
 */
function loadDelayed() {
  import('./delayed.js');

  // Load Social Native Gallery
  const main = document.querySelector('main');
  const metaSku = document.querySelector('meta[name="sku"]');
  if (main && metaSku) {
    loadSocialNativeGallery();
  }
}

export async function fetchIndex(indexFile, pageSize = 500) {
  const handleIndex = async (offset) => {
    const resp = await fetch(`/${indexFile}.json?limit=${pageSize}&offset=${offset}`);
    const json = await resp.json();

    const newIndex = {
      complete: (json.limit + json.offset) === json.total,
      offset: json.offset + pageSize,
      promise: null,
      data: [...window.index[indexFile].data, ...json.data],
    };

    return newIndex;
  };

  window.index = window.index || {};
  window.index[indexFile] = window.index[indexFile] || {
    data: [],
    offset: 0,
    complete: false,
    promise: null,
  };

  // Return index if already loaded
  if (window.index[indexFile].complete) {
    return window.index[indexFile];
  }

  // Return promise if index is currently loading
  if (window.index[indexFile].promise) {
    return window.index[indexFile].promise;
  }

  window.index[indexFile].promise = handleIndex(window.index[indexFile].offset);
  const newIndex = await (window.index[indexFile].promise);
  window.index[indexFile] = newIndex;

  return newIndex;
}

/**
 * Check if consent was given for a specific topic.
 * @param {*} topic Topic identifier
 * @returns {boolean} True if consent was given
 */
// eslint-disable-next-line no-unused-vars
export function getConsent(topic) {
  // eslint-disable-next-line no-console
  console.warn(`getConsent not implemented for ${topic}`);
  return true;
}

async function loadPage() {
  await loadEager(document);
  await loadLazy(document);
  loadDelayed();
  pageContextPush(pageType);
  pageTypePushGtm(pageType);
  await pushFpUserData();
  wrapImgsInSize(document);
}

function applyBodyClasses() {
  const meta = document.querySelector('meta[name="body-class"]');
  if (!meta) return;

  const classes = meta.content.split(' ').map((c) => c.trim());
  document.body.classList.add(...classes);
}

// rerender dataLayer on session update
addMagentoCacheListener(() => {
  try {
    if (!pageTypePushedOnce) {
      pageTypePushGtm(pageType);
      pageTypePushedOnce = true;
    }
    if (!fpUserDataPushedOnce) {
      pushFpUserData();
      fpUserDataPushedOnce = true;
    }
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error('Error in pageTypePushGtm:', error);
  }
});

// eslint-disable-next-line no-shadow
const observer = new MutationObserver((mutationsList, observer) => {
  const headerWrapper = document.querySelector('.headerprof-wrapper');
  const headerWrapperShop = document.querySelector('.headershop-wrapper');

  if (!headerWrapper && !headerWrapperShop) return;

  observer.disconnect();

  const innerObserver = new MutationObserver(() => {
    innerObserver.disconnect();
    const navType = document.querySelector('.nav-light') ? 'light' : 'dark';
    const navTypeElements = document.querySelectorAll(`.nav-${navType}`);
    navTypeElements.forEach((navTypeElement) => {
      navTypeElement.classList.remove(`nav-${navType}`);
    });

    if (['/', '/us/professional', '/us/custom-video-hero', '/us/lighting-experience-pro', '/us/explore-landscape-collection'].includes(window.location.pathname)) {
      const targetHeaderElement = headerWrapper || headerWrapperShop;
      if (!targetHeaderElement) return;

      if (!targetHeaderElement.matches(':hover')) {
        document.body.classList.add(`nav-${navType}`);
      } else {
        document.body.classList.remove(`nav-${navType}`);
      }

      const isMobile = /Mobi|Android|iPhone|iPad|iPod|Windows Phone/i.test(navigator.userAgent);

      if (!isMobile) {
        // Add event listener for mouse enter (hover)
        targetHeaderElement.addEventListener('mouseenter', () => {
          document.body.classList.remove(`nav-${navType}`);
        });

        // Add event listener for mouse leave (hover out)
        targetHeaderElement.addEventListener('mouseleave', () => {
          document.body.classList.add(`nav-${navType}`);
        });
      }

      if (isMobile) {
        if (!targetHeaderElement) return;

        // Tap / click inside header → remove nav-light
        const handleHeaderClick = () => {
          document.body.classList.remove(`nav-${navType}`);
        };

        // Tap / click outside header → add nav-light back
        const handleOutsideClick = (event) => {
          if (!targetHeaderElement.contains(event.target)) {
            document.body.classList.add(`nav-${navType}`);
          }
        };

        // Attach listeners
        targetHeaderElement.addEventListener('click', handleHeaderClick);
        document.addEventListener('click', handleOutsideClick);
      }
    }
  });

  // Start observing inside `headerWrapper` and `headerWrapperShop`
  if (headerWrapper) {
    innerObserver.observe(headerWrapper, { childList: true, subtree: true });
  }
  if (headerWrapperShop) {
    innerObserver.observe(headerWrapperShop, { childList: true, subtree: true });
  }
});

// Start observing the document body for changes
observer.observe(document.body, {
  childList: true, // Observe direct child additions/removals
  subtree: true, // Observe all descendants, not just direct children
});

if (!window.pageLoaded) {
  window.pageLoaded = true;
  loadPage();
  applyBodyClasses();
}
