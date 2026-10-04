import { events } from '@dropins/tools/event-bus.js';
import { initializers } from '@dropins/tools/initializer.js';
import * as productApi from '@dropins/storefront-pdp/api.js';
import { render as productRenderer } from '@dropins/storefront-pdp/render.js';
import ProductDetails from '@dropins/storefront-pdp/containers/ProductDetails.js';
import { viewItem, view3DModelEvent } from '../../scripts/datalayer-vcgtm.js';
import {
  getProductCustomHeight,
} from './ProductsApi.js';
// Libs
import { getConfigValue } from '../../scripts/configs.js';
import {
  buildBlock, decorateBlock, loadBlock, loadScript,
} from '../../scripts/aem.js';
import { isVariantSelected } from '../../scripts/scripts.js';

// Slots
import Breadcrumbs from './slots/Breadcrumbs.js';
import Title from './slots/Title.js';
import SKU from './slots/SKU.js';
import GalleryContent from './slots/GalleryContent.js';
import Quantity from './slots/Quantity.js';
import Options, { isHeightOption, applyCarouselImagePresets } from './slots/Options.js';
import Actions from './slots/Actions.js';
// import SpecialPrice from './slots/SpecialPrice.js';
import Content from './slots/Content.js';
import {
  getCookie, setCookie, getCustomHeightFilterValue,
} from '../../scripts/utils.js';
import {
  updateMagentoCacheSections,
  getCustomerType,
  getLoggedInFromLocalStorage,
  isLastLookEnabled,
} from '../../scripts/storage/util.js';
import InfoContent from './slots/InfoContent.js';
import { getVariantTradePrice } from './product-detail-price.js';
import { initializeProductPrice } from './price-container.js';
import { setJsonLd, loadErrorPage } from '../../scripts/commerce.js';

const customerType = getCustomerType();

function prependSlash(path) {
  return path.startsWith('/') ? path : `/${path}`;
}

function moveSlot(elementSelector, parentSelector) {
  const element = document.querySelector(elementSelector);
  const parent = document.querySelector(parentSelector);

  if (element && parent) {
    parent.appendChild(element);
  }
}

// async function addToCart({
//   sku, quantity, optionsUIDs, product,
// }) {
//   const { cartApi } = await import('../../../scripts/minicart/api.js');

//   return cartApi.addToCart(sku, optionsUIDs, quantity, product);
// }

function cleanOptionTitle(title = '') {
  return title
    .replace(/\b\d+(?:\.\d+)?\s*(?:"|')?/g, '')
    .replace(/\s*[xX]\s*/g, ' ')
    .replace(/\s{2,}/g, ' ')
    .trim();
}

function getVariantOptionLabels(variant, options = []) {
  const selectionIds = variant?.selections || [];

  return selectionIds
    .map((selectionId) => {
      const option = options.find((opt) => opt.values?.some((value) => value.id === selectionId
        || value.value === selectionId));

      if (!option) return null;

      const matchedValue = option.values.find(
        (value) => value.id === selectionId || value.value === selectionId,
      );

      if (!matchedValue?.title) return null;

      return {
        optionId: option.id,
        optionTitle: option.title,
        cleanedTitle: cleanOptionTitle(matchedValue.title),
      };
    })
    .filter(Boolean);
}

function getVariantColor(variant, options = []) {
  const values = getVariantOptionLabels(variant, options)
    .map((item) => item.cleanedTitle)
    .filter(Boolean);

  return [...new Set(values)].join(' / ');
}

async function setJsonLdProduct(product) {
  const {
    name, sku, price, priceRange, images, attributes,
  } = product;
  const script = document.head.querySelector('script[type="application/ld+json"]');
  if (script) {
    script.remove();
  }
  const baseUrl = `${window.location.origin}${window.location.pathname}`;
  const pageUrl = window.location.href;
  const variantSku = product.selectedVariant?.sku
    || product.variants?.[0]?.sku
    || '';

  const encodedSku = encodeURIComponent(variantSku).replace(/%20/g, '+');

  const variantUrl = `${baseUrl}?selected_product=${encodedSku}`;
  const getAttr = (attrs, attrName) => attrs?.find((attr) => attr.name === attrName)?.value;
  const amount = priceRange?.minimum?.final?.amount || price?.final?.amount;
  const brand = getAttr(attributes, 'brand');
  const category = getAttr(attributes, 'category_filter');
  const collection = getAttr(attributes, 'relatives');
  const designer = getAttr(attributes, 'designer');
  const diameter = getAttr(attributes, 'width');
  const mounting = getAttr(attributes, 'mounting');
  const functionAttr = getAttr(attributes, 'function');
  const description = window.product?.selectedVariant?.description || '';
  const offers = (
    window.product.variants.length
      ? window.product.variants
      : [product])
    .map((variant) => {
      const variantAmount = variant.price?.final?.amount
      || variant.price?.regular?.amount
      || amount;

      const color = getVariantColor(variant, window.product?.options || []);
      const variantImage = variant.images?.[0]?.img?.src
        || variant.images?.[0]?.url
        || images?.[0]?.url;
      const region = window.location.pathname.split('/').filter(Boolean)[0]?.toLowerCase();
      const countryMap = {
        us: 'US',
        uk: 'UK',
        eu: 'EU',
      };

      const countryCode = countryMap[region] || 'US';
      return {
        '@type': 'Offer',
        sku: variant.sku || sku,
        name: variant.name || name,
        url: variantUrl,
        image: variantImage,
        price: variantAmount?.value,
        priceCurrency: variantAmount?.currency,
        availability: variant.inStock
          ? 'https://schema.org/InStock'
          : 'https://schema.org/OutOfStock',
        itemCondition: 'https://schema.org/NewCondition',
        shippingDetails: {
          '@type': 'OfferShippingDetails',
          ShippingDestination: {
            '@type': 'DefinedRegion',
            addressCountry: {
              '@type': 'Country',
              name: countryCode,
            },
          },
          deliveryTime: {
            '@type': 'ShippingDeliveryTime',
            businessDays: {
              '@type': 'OpeningHoursSpecification',
            },
          },
        },
        itemOffered: {
          '@type': 'Product',
          name: variant.name || name,
          sku: variant.sku || sku,
          ...(color ? { color } : {}),
          isVariantOf: {
            '@id': baseUrl,
          },
        },
      };
    });

  setJsonLd({
    '@context': 'http://schema.org',
    '@type': 'Product',
    '@id': pageUrl,
    url: baseUrl,
    sku,
    mpn: sku,
    brand: {
      '@type': 'Brand',
      name: brand,
    },
    manufacturer: {
      '@type': 'Organization',
      name: 'Visual Comfort & Co.',
    },
    category,
    description,
    additionalProperty: [
      {
        '@type': 'PropertyValue',
        name: 'Collection',
        value: collection || '',
      },
      {
        '@type': 'PropertyValue',
        name: 'Designer',
        value: designer || '',
      },
      {
        '@type': 'PropertyValue',
        name: 'Diameter',
        value: diameter || '',
      },
      {
        '@type': 'PropertyValue',
        name: 'Mounting',
        value: mounting || '',
      },
      {
        '@type': 'PropertyValue',
        name: 'Function',
        value: functionAttr || '',
      },
    ],
    name,
    image: images[0]?.url,
    productID: sku,
    offers,
  }, 'product');
}

function setJsonLdBreadcrumbs(breadcrumbs) {
  setJsonLd({
    '@context': 'http://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: breadcrumbs.map((breadcrumb, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      item: {
        '@id': `https://www.visualcomfort.com${prependSlash(breadcrumb.category_url_path ?? breadcrumb.url_path_ld ?? breadcrumb.url_path)}`,
        name: breadcrumb.name,
      },
    })),
  }, 'breadcrumbs');
}

function createMetaTag(property, content, type) {
  if (!property || !type) {
    return;
  }
  let meta = document.head.querySelector(`meta[${type}="${property}"]`);
  if (meta) {
    if (!content) {
      meta.remove();
      return;
    }
    meta.setAttribute(type, property);
    meta.setAttribute('content', content);
    return;
  }
  if (!content) {
    return;
  }
  meta = document.createElement('meta');
  meta.setAttribute(type, property);
  meta.setAttribute('content', content);
  document.head.appendChild(meta);
}

// TODO verify if we need this
// eslint-disable-next-line no-unused-vars
function setMetaTags(product) {
  if (!product) {
    return;
  }

  const price = product.priceRange
    ? product.priceRange.minimum.final.amount : product.price.final.amount;

  createMetaTag('title', product.metaTitle, 'name');
  createMetaTag('description', product.metaDescription, 'name');
  createMetaTag('keywords', product.metaKeyword, 'name');

  createMetaTag('og:type', 'og:product', 'property');
  createMetaTag('og:description', product.shortDescription, 'property');
  createMetaTag('og:title', product.metaTitle, 'property');
  createMetaTag('og:url', window.location.href, 'property');
  const mainImage = product?.images?.filter((image) => image.roles.includes('thumbnail'))[0];
  const metaImage = mainImage?.url || product?.images[0]?.url;
  createMetaTag('og:image', metaImage, 'property');
  createMetaTag('og:image:secure_url', metaImage, 'property');
  createMetaTag('og:product:price:amount', price.value, 'property');
  createMetaTag('og:product:price:currency', price.currency, 'property');

  createMetaTag('twitter:card', product.shortDescription, 'name');
  createMetaTag('twitter:title', product.metaTitle, 'name');
  createMetaTag('twitter:image', metaImage, 'name');
}

function conditionallyUpdateImageText(image, replacementText = '1 of 1') {
  const altText = image ? image.getAttribute('alt') : null;
  if (altText) {
    if (altText.includes('1 of 2')) {
      image.setAttribute('alt', altText.replace('1 of 2', replacementText));
    } else if (altText.includes('2 of 2')) {
      image.setAttribute('alt', altText.replace('2 of 2', replacementText));
    }
  }
}

function animateGalleryButtons() {
  const galleries = document.querySelectorAll('.pdp-carousel');

  galleries.forEach((gallery) => {
    // Mobile image carousel keeps arrows visible; hover slide-out would block taps.
    if (gallery.classList.contains('pdp-product__images--carousel')) return;

    gallery.addEventListener('mouseover', (e) => {
      const currentGallery = e.target.closest('.pdp-carousel');

      if (currentGallery) {
        // Find all buttons that are direct children of the current gallery
        const buttons = currentGallery.querySelectorAll(':scope > button');

        buttons.forEach((button) => {
          if (!button.hasAttribute('disabled')) {
            if (button.classList.contains('pdp-carousel__button--prev')) {
              button.classList.remove('slideout-left');
              button.classList.add('slidein-left');
            } else if (button.classList.contains('pdp-carousel__button--next')) {
              button.classList.remove('slideout-right');
              button.classList.add('slidein-right');
            }
          }
        });
      }
    });

    gallery.addEventListener('mouseout', (e) => {
      const currentGallery = e.target.closest('.pdp-carousel');

      if (currentGallery) {
        const buttons = currentGallery.querySelectorAll(':scope > button');

        buttons.forEach((button) => {
          if (!button.hasAttribute('disabled')) {
            if (button.classList.contains('pdp-carousel__button--prev')) {
              button.classList.remove('slidein-left');
              button.classList.add('slideout-left');
            } else if (button.classList.contains('pdp-carousel__button--next')) {
              button.classList.remove('slidein-right');
              button.classList.add('slideout-right');
            }
          }
        });
      }
    });
  });
}

function getNumberOfImages() {
  if (isVariantSelected()) {
    return window.product.selectedVariant.images.length;
  }
  return window.product.images.length;
}

function hasAttributeValue(name) {
  let attrValue = '';
  if (isVariantSelected()) {
    attrValue = window.product.selectedVariant.attributes.find((attr) => attr.name === name)?.value;
  } else {
    attrValue = window.product.attributes.find((attr) => attr.name === name)?.value;
  }
  return (attrValue && attrValue !== '');
}

/**
 * Adjust the controls for the product overlay:
 * * add '+' and '-' zoom buttons
 * * add behavior to the 'wheel' to zoom in & out
 * * if there is only 1 image, disable the 'prev' and 'next' arrows
 */
function addZoomButtons() {
  const overlay = document.querySelector('.pdp-overlay.pdp-overlay.pdp-product__overlay');
  if (!overlay) return;

  // if there is only one image, remove/disable the carousel controls for 'prev' and 'next'
  if (getNumberOfImages() === 1 && !getPdp360AttributeValue()) {
    let buttons = overlay.querySelectorAll('.pdp-overlay__content .pdp-carousel__controls');
    buttons.forEach((button) => {
      button.disabled = true;
      button.style.display = 'none';
    });
    buttons = overlay.querySelectorAll('.pdp-carousel--arrows .pdp-carousel__button--prev');
    buttons.forEach((button) => {
      button.disabled = true;
      button.style.display = 'none';
    });
    buttons = overlay.querySelectorAll('.pdp-carousel--arrows .pdp-carousel__button--next');
    buttons.forEach((button) => {
      button.disabled = true;
      button.style.display = 'none';
    });
    const images = overlay.querySelectorAll('.pdp-carousel--arrows img');
    images.forEach((image) => {
      conditionallyUpdateImageText(image);
    });
  }

  const carouselWrapper = overlay.querySelector('.pdp-carousel__wrapper');
  if (!carouselWrapper) return;

  const overlayCarousel = overlay.querySelector('#overlay-content .pdp-product__overlay__carousel');
  const carouselSlides = overlayCarousel.querySelectorAll('.pdp-carousel__slide');
  const buttons = overlayCarousel.querySelectorAll('.pdp-carousel__controls__button');
  const thumbnailsRow = overlayCarousel.querySelector('div:last-child:not([class])');
  const controlsContainer = document.querySelector('.pdp-overlay__content .pdp-carousel__controls');

  function buildOverlayThumbnailSlide(slide) {
    const clonedSlide = slide.cloneNode(true);
    clonedSlide.classList.remove(
      'pdp-carousel__slide--hidden',
      'pdp-carousel__slide--active',
      'pdp-carousel__slide--orphan',
    );
    clonedSlide.removeAttribute('style');
    return clonedSlide;
  }

  function centerActiveButton() {
    const activeButton = controlsContainer.querySelector('.pdp-carousel__controls__button--active');

    if (activeButton && activeButton.children.length > 0) {
      const containerWidth = overlayCarousel.offsetWidth;
      let totalButtonsWidth = 0;

      buttons.forEach((button) => {
        totalButtonsWidth += button.offsetWidth;
      });

      if (totalButtonsWidth <= containerWidth) {
        controlsContainer.style.transform = 'translateX(0)';
      } else {
        const buttonWidth = activeButton.offsetWidth;
        const buttonLeft = activeButton.offsetLeft;

        // Calculate the offset to ensure the active button is visible
        let offset = buttonLeft - (containerWidth / 2) + (buttonWidth / 2);

        // Ensure the offset is within bounds
        const maxOffset = controlsContainer.scrollWidth - containerWidth;
        if (offset < 0) {
          offset = 0;
        } else if (offset > maxOffset) {
          offset = maxOffset;
        }

        controlsContainer.style.transform = `translateX(-${offset}px)`;
      }
    }
  }

  function updateThumbnailsRow() {
    const isMobile = window.matchMedia('(max-width: 768px)').matches;
    if (thumbnailsRow) {
      // Remove additional set of PDP buttons
      const buttonsInThumbnailsRow = Array.from(thumbnailsRow.children).filter((child) => child.tagName.toLowerCase() === 'button');
      buttonsInThumbnailsRow.forEach((button) => button.remove());

      if (!isMobile) {
        buttons.forEach((button, index) => {
          if (carouselSlides[index]) {
            const clonedSlide = buildOverlayThumbnailSlide(carouselSlides[index]);
            button.innerHTML = '';
            button.appendChild(clonedSlide);
            const img = button.querySelector('img');
            if (img) {
              img.classList.remove('dropin-image');
              img.style.transform = 'none';
            }
          }
        });

        thumbnailsRow.style.cssText = '';
        centerActiveButton();
      } else {
        // Reverse the logic and delete cloned slides
        buttons.forEach((button) => {
          button.innerHTML = '';
        });
        controlsContainer.style.transform = '';
      }

      animateGalleryButtons();
    }
  }

  // Initial thumbnails row update
  updateThumbnailsRow();

  // Event listener for overlay resize
  const resizeObserver = new ResizeObserver(() => {
    updateThumbnailsRow();
  });

  resizeObserver.observe(overlay);

  // MutationObserver to track changes to the active class of the buttons
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
        centerActiveButton();
      }
    });
  });

  buttons.forEach((button) => {
    observer.observe(button, { attributes: true });
  });

  // Check if zoom buttons already exist
  if (overlay.querySelector('.zoom-button.zoom-in') || overlay.querySelector('.zoom-button.zoom-out')) {
    return;
  }

  // Create zoom buttons
  const zoomInButton = document.createElement('button');
  zoomInButton.classList.add('zoom-button', 'zoom-in');

  const zoomOutButton = document.createElement('button');
  zoomOutButton.classList.add('zoom-button', 'zoom-out');

  // Append zoom buttons to the overlay
  overlay.appendChild(zoomInButton);
  overlay.appendChild(zoomOutButton);

  // Add zoom functionality
  let zoomLevel = 1;
  const maxZoomLevel = 3;
  const minZoomLevel = 1;
  let isDragging = false;
  let startX;
  let startY;
  let translateX = 0;
  let translateY = 0;

  const applyTransform = (element, smooth = true, duration = '0.3s') => {
    if (smooth) {
      element.style.transition = `transform ${duration} ease`;
    } else {
      element.style.transition = 'none';
    }
    element.style.transform = `translate(${translateX}px, ${translateY}px) scale(${zoomLevel})`;
  };

  const updateCursorStyle = () => {
    if (zoomLevel > 1) {
      carouselWrapper.style.cursor = isDragging ? 'grabbing' : 'grab';
    } else {
      carouselWrapper.style.cursor = 'default';
    }
  };

  const getActiveImage = () => {
    const activeSlide = carouselWrapper.querySelector('.pdp-carousel__slide--active');
    if (activeSlide) {
      const activeImage = activeSlide.querySelector('img');
      if (activeImage) {
        // Disable default drag-and-drop behavior
        activeImage.ondragstart = () => false;
      }
      return activeImage;
    }
    return null;
  };

  const getHighestQualitySrc = (srcset) => {
    const sources = srcset.split(',').map((src) => {
      const [url, descriptor] = src.trim().split(' ');
      const resolution = parseFloat(descriptor);
      return { url, resolution };
    });
    sources.sort((a, b) => b.resolution - a.resolution);
    return sources[0].url;
  };

  zoomInButton.addEventListener('click', () => {
    const activeImage = getActiveImage();
    if (activeImage && zoomLevel < maxZoomLevel) {
      // Use the highest quality image for zooming
      if (!activeImage.dataset.highestQualitySet) {
        // Fall back to the current src when there is no srcset (empty srcset made
        // getHighestQualitySrc return '', which blanked the image on zoom). Mirrors
        // the wheel-zoom handler below.
        const highestQualitySrc = getHighestQualitySrc(activeImage.srcset) || activeImage.src;
        if (activeImage.src !== highestQualitySrc) {
          activeImage.src = highestQualitySrc;
          activeImage.dataset.highestQualitySet = 'true'; // Set the flag
        }
      }
      zoomLevel += 1;
      applyTransform(activeImage, true, '0.5s'); // Longer duration for smooth transition
      updateCursorStyle();
    }
  });

  zoomOutButton.addEventListener('click', () => {
    const activeImage = getActiveImage();
    if (activeImage && zoomLevel > minZoomLevel) {
      zoomLevel -= 1;
      applyTransform(activeImage, true, '0.5s'); // Longer duration for smooth transition
      updateCursorStyle();
    }
  });

  // Add mouse scroll zoom functionality
  overlay.addEventListener('wheel', (event) => {
    event.preventDefault();
    const activeImage = getActiveImage();
    if (!activeImage) return;

    if (event.deltaY < 0) { // Zooming in
      if (!activeImage.dataset.highestQualitySet) {
        const highestQualitySrc = getHighestQualitySrc(activeImage.srcset) || activeImage.src;
        if (activeImage.src !== highestQualitySrc) {
          activeImage.src = highestQualitySrc;
          activeImage.dataset.highestQualitySet = 'true'; // Set the flag
        }
      }

      zoomLevel = Math.min(zoomLevel + 0.1, 3);
    } else {
      zoomLevel = Math.max(zoomLevel - 0.1, 1);
    }

    applyTransform(activeImage, false); // No smooth transition for wheel zoom
    updateCursorStyle();
  });

  // Add drag functionality
  carouselWrapper.addEventListener('mousedown', (event) => {
    const activeImage = getActiveImage();
    if (!activeImage) return;

    // Disable dragging at zoom level 1
    if (zoomLevel === 1) return;

    isDragging = true;
    startX = event.clientX - translateX;
    startY = event.clientY - translateY;
    carouselWrapper.style.cursor = 'grabbing';
  });

  document.addEventListener('mousemove', (event) => {
    if (!isDragging) return;

    event.preventDefault();
    const activeImage = getActiveImage();
    if (!activeImage) return;

    translateX = event.clientX - startX;
    translateY = event.clientY - startY;

    applyTransform(activeImage, false); // No smooth transition for dragging
  });

  document.addEventListener('mouseup', () => {
    isDragging = false;
    updateCursorStyle();
  });

  document.addEventListener('mouseleave', () => {
    isDragging = false;
    updateCursorStyle();
  });

  // Reset zoom level when scrolling through pictures
  const carouselButtons = overlay.querySelectorAll('.pdp-product__overlay__carousel button');
  carouselButtons.forEach((button) => {
    button.addEventListener('click', () => {
      zoomLevel = 1;
      translateX = 0;
      translateY = 0;
      const activeImage = getActiveImage();
      if (activeImage) {
        applyTransform(activeImage, true);
      }
      updateCursorStyle();
    });
  });

  // Set initial cursor style
  carouselWrapper.style.cursor = 'default';
}

let modelViewScriptLoaded = false;

async function loadModelViewerScript() {
  if (!modelViewScriptLoaded) {
    await loadScript('https://ajax.googleapis.com/ajax/libs/model-viewer/4.0.0/model-viewer.min.js', { type: 'module' });
    modelViewScriptLoaded = true;
  }
}

function setup3DThumbnailClickTracking() {
  document.addEventListener('click', async (event) => {
    const clicked3DImage = event.target.closest('img[title="3dmodel-modelviewer"]');

    if (clicked3DImage) {
      await view3DModelEvent(window.product);
    }
  });
}

// Function to check if active slide has 3dmodel image and replace it with model-viewer
async function replace3dImageWithModelViewer(img) {
  // A variant without its own pdp_360 value should never show the 360 viewer,
  // even if the base product (or another variant) has one.
  const pdp360Attribute = getPdp360AttributeValue();
  if (!pdp360Attribute) {
    img.remove();
    return;
  }

  await loadModelViewerScript();

  // Guard against a concurrent mutation already having replaced this img
  if (!img.isConnected) return;

  const modelViewer = document.createElement('model-viewer');
  modelViewer.setAttribute('alt', '360 Viewer');
  modelViewer.setAttribute('shadow-intensity', '1');
  modelViewer.setAttribute('camera-controls', '');
  modelViewer.setAttribute('ar', '');
  modelViewer.setAttribute('touch-action', 'pan-y');
  modelViewer.setAttribute('data-pdp360', 'true');
  modelViewer.setAttribute('src', `/media/docs/360/${pdp360Attribute}`);

  img.replaceWith(modelViewer);
}

// Reacts both to a slide becoming active (class mutation) and to a slide's content
// being swapped while it's already active — e.g. mobile re-renders the carousel on a
// variant change and the 360 slide can end up "active" without its class ever toggling.
async function checkActiveSlide(mutationsList) {
  const slidesToCheck = new Set();

  mutationsList.forEach((mutation) => {
    if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
      const { target } = mutation;
      if (target.classList?.contains('pdp-carousel__slide--active')) {
        slidesToCheck.add(target);
      }
    } else if (mutation.type === 'childList') {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType !== 1) return;
        const slide = node.classList?.contains('pdp-carousel__slide--active')
          ? node
          : node.closest?.('.pdp-carousel__slide--active');
        if (slide) {
          slidesToCheck.add(slide);
        }
      });
    }
  });

  slidesToCheck.forEach((slide) => {
    const img = slide.querySelector('img[title="3dmodel-modelviewer"]');
    if (img) {
      replace3dImageWithModelViewer(img);
    }
  });
}

let modelObserver;

function setup3dModelObserver() {
  if (modelObserver) {
    modelObserver.disconnect();
  }

  modelObserver = new MutationObserver(checkActiveSlide);

  const config = {
    attributes: true,
    attributeFilter: ['class'],
    childList: true,
    subtree: true,
  };

  modelObserver.observe(document.body, config);
}

// Function to observe the DOM for dynamic elements added to the page. Used for 3D model viewer
function observeDynamicElements() {
  const targetNode = document.querySelector('.pdp-product');
  if (!targetNode) {
    return;
  }

  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.addedNodes.length > 0) {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === 1) {
            const img = node.querySelector('img[title="3dmodel-modelviewer"]');
            const modelViewer = node.querySelector('model-viewer');
            if (img || modelViewer) {
              setup3dModelObserver();
            }
          }
        });
      }
    });
  });

  observer.observe(targetNode, {
    childList: true,
    subtree: true,
  });
}

function getBadge() {
  const enableLastLookSale = isLastLookEnabled();

  // Use selectedVariant if available
  const selectedProduct = window?.product.selectedVariant;
  if (!selectedProduct) return '';

  const badgeAttribute = selectedProduct?.attributes?.find((attr) => attr.name === 'badge');
  const badge = badgeAttribute?.value || '';
  if (badge === 'Last Look' && (!enableLastLookSale || customerType !== 'trade')) {
    return '';
  }
  return badge;
}

let badgeRenderFrame = null;

function addBadgesToCarousels() {
  const badge = getBadge();
  if (!badge) return;
  const isMobileViewport = window.matchMedia('(max-width: 768px)').matches;

  // Find all carousels (main carousel, overlay carousel, etc.)
  const carousels = document.querySelectorAll('.pdp-carousel');
  if (!carousels?.length) return;

  carousels.forEach((carousel) => {
    if (!carousel) return;

    const isDesktopThumbnailCarousel = !isMobileViewport
      && carousel.classList.contains('pdp-carousel--main-image-controls')
      && carousel.classList.contains('pdp-carousel--thumbnailsColumn');

    const desktopSlideWrapper = Array.from(carousel.querySelectorAll('.pdp-carousel__wrapper'))
      .find((wrapper) => !wrapper.classList.contains('pdp-carousel__controls__wrapper')
        && wrapper.querySelector('.pdp-carousel__slide'));

    const badgeContainer = isMobileViewport || isDesktopThumbnailCarousel
      ? carousel
      : (desktopSlideWrapper || carousel.querySelector('.pdp-carousel__wrapper') || carousel);

    if (badgeContainer.querySelector('.product-gallery-badge')) {
      return;
    }

    const badgeElement = document.createElement('div');
    badgeElement.className = 'product-gallery-badge';
    if (isDesktopThumbnailCarousel) {
      badgeElement.classList.add('product-gallery-badge--desktop-carousel');
    }
    badgeElement.innerHTML = `<span>${badge}</span>`;

    badgeContainer.appendChild(badgeElement);
  });
}

let badgeRefreshAnimationFrame;
let badgeRefreshTimeout;
let isBadgeResizeListenerBound = false;

function scheduleBadgesToCarousels() {
  if (badgeRenderFrame) {
    cancelAnimationFrame(badgeRenderFrame);
  }

  badgeRenderFrame = requestAnimationFrame(() => {
    badgeRenderFrame = requestAnimationFrame(() => {
      badgeRenderFrame = null;
      addBadgesToCarousels();
    });
  });
}

export function updateBadgesOnVariantChange() {
  // Remove existing badges
  const existingBadges = document.querySelectorAll('.product-gallery-badge');
  existingBadges?.forEach((badgeEl) => {
    if (badgeEl) badgeEl.remove();
  });

  scheduleBadgesToCarousels();
}

function observeBadgeTargets() {
  const targetNode = document.querySelector('.pdp-product');
  if (!targetNode) {
    return;
  }

  const badgeTargetSelector = '.pdp-carousel, .pdp-carousel__wrapper, .pdp-product__images, .variants-container';

  const observer = new MutationObserver((mutations) => {
    const shouldScheduleBadges = mutations.some((mutation) => Array.prototype.some.call(
      mutation.addedNodes,
      (node) => {
        if (node.nodeType !== Node.ELEMENT_NODE) {
          return false;
        }

        return node.matches?.(badgeTargetSelector)
          || node.querySelector?.(badgeTargetSelector);
      },
    ));

    if (shouldScheduleBadges) {
      scheduleBadgesToCarousels();
    }
  });

  observer.observe(targetNode, {
    childList: true,
    subtree: true,
  });
}

function scheduleBadgeRefresh() {
  window.cancelAnimationFrame(badgeRefreshAnimationFrame);
  window.clearTimeout(badgeRefreshTimeout);

  badgeRefreshAnimationFrame = window.requestAnimationFrame(() => {
    updateBadgesOnVariantChange();

    badgeRefreshTimeout = window.setTimeout(() => {
      updateBadgesOnVariantChange();
    }, 150);
  });
}

// Function to observe the DOM for the overlay
function observeOverlay() {
  const overlay = document.querySelector('.pdp-overlay.pdp-overlay--centered.pdp-product__overlay');
  if (overlay) {
    addZoomButtons();
    scheduleBadgesToCarousels();
    return;
  }

  const observer = new MutationObserver((mutations, obs) => {
    const newOverlay = document.querySelector('.pdp-overlay.pdp-overlay--centered.pdp-product__overlay');
    if (newOverlay) {
      addZoomButtons();
      scheduleBadgesToCarousels();
      obs.disconnect();
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
}

export function buildMessages() {
  if (!document.querySelector('.message-body')) {
    const messageCookie = getCookie('mage-messages');
    const messages = messageCookie ? JSON.parse(messageCookie) : [];
    setCookie('mage-messages', '{}');

    const messagesContainer = document.createElement('div');
    messagesContainer.classList.add('messages-container');

    if (Array.isArray(messages)) {
      messages.forEach((msg) => {
        const message = document.createElement('div');
        message.classList.add('message', msg.type);

        const messageBody = document.createElement('div');
        messageBody.classList.add('message-body');
        messageBody.innerHTML = msg.text;

        const closeBtn = document.createElement('span');
        closeBtn.classList.add('close-message');
        closeBtn.addEventListener('click', (event) => {
          const container = event.target.closest('.message');
          container.remove();
        });
        message.appendChild(messageBody);
        message.appendChild(closeBtn);
        messagesContainer.appendChild(message);
      });
    }

    const main = document.querySelector('.product-details-container');
    main.insertBefore(messagesContainer, main.firstChild);
  }
}

// Select product options based on variant UIDs
export function selectOptionByUID(uids) {
  if (!Array.isArray(uids) || uids.length === 0) {
    console.warn('No valid UIDs provided to selectOptionByUID');
    return;
  }

  const selects = document.querySelectorAll('.pdp-product__options select');

  if (selects.length === 0) {
    console.warn('No product option selects found on page');
    return;
  }

  uids.forEach((uid) => {
    // Skip invalid UIDs
    if (!uid || typeof uid !== 'string') {
      console.warn('Invalid UID provided:', uid);
      return;
    }

    let optionFound = false;

    selects.forEach((select) => {
      const option = select.querySelector(`option[value="${uid}"]`);
      if (option) {
        option.selected = true;
        optionFound = true;
      }
    });

    if (!optionFound) {
      console.error(`Option with value "${uid}" not found.`);
    }
  });
}

function addHeightLegend() {
  const mounting = window?.product?.variants[0]?.attributes?.find((attr) => attr.label === 'mounting');
  if (mounting != null && mounting.value === 'Rod') {
    const customHeightLabel = document.querySelector('#swatch-item-height_filter .pdp-swatches__field__label');
    if (!customHeightLabel) {
      return;
    }

    // Check if legend already exists to prevent duplicates
    const existingLegend = customHeightLabel.nextElementSibling;
    if (existingLegend && existingLegend.classList.contains('legend')) {
      return;
    }

    const customHeightLegend = document.createElement('div');
    customHeightLegend.classList.add('legend');
    const customHeightCalculator = document.createElement('a');
    // eslint-disable-next-line no-script-url
    customHeightCalculator.href = 'javascript:void(0);';
    customHeightCalculator.id = 'custom_height_calculator';
    customHeightCalculator.textContent = 'calculator';

    customHeightLegend.textContent = 'Use our ';
    customHeightLegend.append(customHeightCalculator);
    customHeightLegend.append(' for height recommendations');
    customHeightCalculator.onclick = async () => {
      try {
        // eslint-disable-next-line no-use-before-define
        await addCustomHeightModal();
      } catch (error) {
        console.error('Error opening custom height modal:', error);
      }
    };

    customHeightLabel.insertAdjacentElement('afterend', customHeightLegend);
  }
}

function debounce(func, delay) {
  let timeout;
  // eslint-disable-next-line func-names
  return function (...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), delay);
  };
}

function parseHeight(heightData) {
  let height = heightData.split(':')[1];
  height = height.replace(/"/g, '');
  return parseFloat(height);
}

function getRoomOptions(baseCode, sku) {
  return getProductCustomHeight(baseCode, sku)
    .then((data) => {
      if (data && data.data && data.data.locations) {
        return data;
      }
      return '';
    })
    .catch((error) => {
      console.error('Error fetching room options:', error);
    });
}

async function addCustomHeightModal() {
  if (document.querySelector('#calculatorModal')) {
    document.querySelector('#calculatorModal').remove();
  }
  const modal = document.createElement('div');
  modal.id = 'calculatorModal';
  modal.className = 'modal';

  const modalContent = document.createElement('div');
  modalContent.className = 'modal-content';

  const closeSpan = document.createElement('span');
  closeSpan.className = 'close';
  closeSpan.id = 'closeModal';
  closeSpan.innerHTML = '&times;';

  const header = document.createElement('h2');
  header.textContent = 'Custom Height Calculator';

  const hr = document.createElement('hr');

  const roomSelectionDiv = document.createElement('div');
  roomSelectionDiv.id = 'roomSelection';

  const roomHeader = document.createElement('h3');
  roomHeader.textContent = 'Where will this fixture be installed?';

  const roomForm = document.createElement('form');
  roomForm.id = 'roomForm';

  // Add loading state initially
  const loadingDiv = document.createElement('div');
  loadingDiv.className = 'loading-spinner';
  loadingDiv.innerHTML = '<p>Loading room options...</p>';
  roomForm.appendChild(loadingDiv);

  roomSelectionDiv.appendChild(roomHeader);
  roomSelectionDiv.appendChild(roomForm);

  const measurementInputsDiv = document.createElement('div');
  measurementInputsDiv.id = 'measurementInputs';
  measurementInputsDiv.style.display = 'none';

  const measurementHeader = document.createElement('h3');
  measurementHeader.id = 'measurementHeader';
  measurementHeader.textContent = 'Measurement Inputs';

  const measurementTable = document.createElement('tbody');
  measurementTable.id = 'measurementTable';

  const measurementTableContainer = document.createElement('table');
  measurementTableContainer.appendChild(measurementTable);

  measurementInputsDiv.appendChild(measurementHeader);
  measurementInputsDiv.appendChild(measurementTableContainer);

  const recommendationDiv = document.createElement('div');
  recommendationDiv.className = 'recommendation-section';
  recommendationDiv.style.display = 'none';

  const recommendationHeader = document.createElement('h4');
  recommendationHeader.textContent = 'Based on your measurements, we recommend selecting an overall height of:';

  const heightDropdown = document.createElement('select');
  heightDropdown.id = 'recommendedHeightOptions';

  const recommendButton = document.createElement('button');
  recommendButton.textContent = 'Proceed With Standard Height';

  recommendationDiv.appendChild(recommendationHeader);
  recommendationDiv.appendChild(heightDropdown);
  recommendationDiv.appendChild(recommendButton);

  modalContent.appendChild(closeSpan);
  modalContent.appendChild(header);
  modalContent.appendChild(hr);
  modalContent.appendChild(roomSelectionDiv);
  modalContent.appendChild(measurementInputsDiv);
  modalContent.appendChild(recommendationDiv);
  modal.appendChild(modalContent);
  document.body.appendChild(modal);
  modal.style.display = 'block';

  // Store fetchRoomOptions data globally for use in populateMeasurementTable
  let roomOptionsData = null;

  // Fetch room options asynchronously after modal is displayed
  const baseCode = window.product?.sku.replace(' ', '+');
  const sku = window.product?.selectedVariant?.sku ? window.product.selectedVariant?.sku.replace(' ', '+').replace('/', '%2f') : window.product?.variants[0]?.sku.replace(' ', '+').replace('/', '%2f');

  getRoomOptions(baseCode, sku).then((fetchRoomOptions) => {
    // Remove loading spinner
    loadingDiv.remove();

    if (fetchRoomOptions?.data?.locations) {
      // Store the data for use in populateMeasurementTable
      roomOptionsData = fetchRoomOptions;

      const roomOptions = fetchRoomOptions.data.locations.map((location) => location.label);
      roomOptions.forEach((room) => {
        const label = document.createElement('label');
        const input = document.createElement('input');
        input.type = 'radio';
        input.name = 'room';
        input.value = room;
        label.appendChild(input);
        label.appendChild(document.createTextNode(room));
        roomForm.appendChild(label);
      });

      // Set up room option click handlers
      const roomOptionsInputs = document.querySelectorAll('input[name="room"]');
      roomOptionsInputs.forEach((option) => {
        option.addEventListener('click', () => {
          roomSelectionDiv.style.display = 'none';
          measurementInputsDiv.style.display = 'block';
          // eslint-disable-next-line no-use-before-define
          populateMeasurementTable(option.value);
        });
      });

      // Populate height dropdown options
      const recommendedHeightSelect = document.getElementById('recommendedHeightOptions');
      const heightSelects = document.querySelectorAll('select[aria-label="Height"]');
      heightSelects.forEach((select) => {
        Array.from(select.options).forEach((option) => {
          const newOption = document.createElement('option');
          newOption.value = option.value;
          newOption.textContent = option.textContent;
          if (newOption.textContent.includes('Standard')) {
            newOption.selected = true;
          }
          recommendedHeightSelect.appendChild(newOption);
        });
      });
    } else {
      // Show error message if no room options available
      const errorDiv = document.createElement('div');
      errorDiv.innerHTML = '<p>Unable to load room options. Please try again later.</p>';
      roomForm.appendChild(errorDiv);
    }
  }).catch((error) => {
    // Remove loading spinner and show error
    loadingDiv.remove();
    const errorDiv = document.createElement('div');
    errorDiv.innerHTML = '<p>Error loading room options. Please try again later.</p>';
    roomForm.appendChild(errorDiv);
    console.error('Failed to load room options:', error);
  });

  heightDropdown.addEventListener('change', () => {
    const selectedOptionText = heightDropdown.options[heightDropdown.selectedIndex].text;
    const isStandard = selectedOptionText.includes('Standard');
    recommendButton.textContent = isStandard ? 'Proceed With Standard Height' : 'Proceed with Custom Height';
    document.getElementById('dropin-picker-height').dispatchEvent(new Event('change'));
  });

  recommendButton.onclick = async () => {
    try {
      const selectedOptionValue = document.querySelector('#recommendedHeightOptions').value;
      const currentHeightOption = window.product.customOptions.find((option) => option.id === 'height_filter');
      if (currentHeightOption) {
        currentHeightOption.selectedValue = selectedOptionValue;
      }
      if (window.product.selectedVariant?.selections) {
        window.product.selectedVariant.selections = window.product.selectedVariant.selections
          .filter((selection) => {
            const decodedValue = atob(selection);

            if (decodedValue.startsWith('{') && decodedValue.endsWith('}')) {
              return false;
            }

            return true;
          });
      } else {
        console.error('No selections found in window.product.selectedVariant.');
      }

      const isLoggedIn = getLoggedInFromLocalStorage();
      if (isLoggedIn) {
        if (customerType === 'retail') {
          const attribute = window.product?.attributes?.find((attr) => attr.name === 'badge')?.value;
          if (attribute === 'Open Box' || attribute === 'Last Call') {
            let finalPrice = '';
            if (window.product.selectedVariant) {
              finalPrice = window.product.selectedVariant.price.final.amount.value;
              let customPrice = 0;
              let height = getCustomHeightFilterValue();
              height = height?.filter((selection) => isHeightOption(selection));
              if (height && height.length > 0) {
                const heightOption = window?.product?.customOptions?.find((option) => option.id === 'height_filter');
                customPrice = heightOption.values.find((attr) => attr.id === height[0]);
                if (customPrice) {
                  customPrice = customPrice.value;
                } else {
                  customPrice = 0;
                }
              }
              finalPrice += parseFloat(customPrice);
            }

            const priceElement = document.querySelector('.price-final .price-value');
            if (priceElement) {
              priceElement.textContent = `$${new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(finalPrice)}`;
            }
          } else {
            let regularPrice = '';
            if (window.product.selectedVariant) {
              regularPrice = window.product.selectedVariant.price.regular.amount.value;
              let customPrice = 0;
              let height = getCustomHeightFilterValue();
              height = height?.filter((selection) => isHeightOption(selection));
              if (height && height.length > 0) {
                const heightOption = window?.product?.customOptions?.find((option) => option.id === 'height_filter');
                customPrice = heightOption.values.find((attr) => attr.id === height[0]);
                if (customPrice) {
                  customPrice = customPrice.value;
                } else {
                  customPrice = 0;
                }
              }
              regularPrice += parseFloat(customPrice);
            }
            const priceElement = document.querySelector('.retail-price-value');
            if (priceElement) {
              priceElement.textContent = `$${new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(regularPrice)}`;
            }
          }
        } else if (customerType === 'wholesale') {
          let regularPrice = '';
          if (window.product.selectedVariant) {
            regularPrice = window.product.selectedVariant.price.regular.amount.value;
            let customPrice = 0;
            let height = getCustomHeightFilterValue();
            height = height?.filter((selection) => isHeightOption(selection));
            if (height && height.length > 0) {
              const heightOption = window?.product?.customOptions?.find((option) => option.id === 'height_filter');
              customPrice = heightOption.values.find((attr) => attr.id === height[0]);
              if (customPrice) {
                customPrice = customPrice.value;
              } else {
                customPrice = 0;
              }
            }
            regularPrice += parseFloat(customPrice);
          }
          const priceElement = document.querySelector('.wholesale-price-value');
          if (priceElement) {
            priceElement.textContent = `$${new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(regularPrice)}`;
          }
        } else if (customerType === 'trade' || customerType === 'employee') {
          let finalPrice = await getVariantTradePrice();
          if (window.product.selectedVariant) {
            let customPrice = 0;
            let height = getCustomHeightFilterValue();
            height = height?.filter((selection) => isHeightOption(selection));
            if (height && height.length > 0) {
              const heightOption = window?.product?.customOptions?.find((option) => option.id === 'height_filter');
              customPrice = heightOption.values.find((attr) => attr.id === height[0]);
              if (customPrice) {
                customPrice = customPrice.value;
              } else {
                customPrice = 0;
              }
            }
            finalPrice += parseFloat(customPrice);
          }
          const priceElement = document.querySelector('.price-final .price-value');
          if (priceElement) {
            priceElement.textContent = `$${new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(finalPrice)}`;
          }
        }
      } else {
        const attribute = window.product?.attributes?.find((attr) => attr.name === 'badge')?.value;
        if (attribute === 'Open Box' || attribute === 'Last Call') {
          let finalPrice = '';
          if (window.product.selectedVariant) {
            finalPrice = window.product.selectedVariant.price.final.amount.value;
            let customPrice = 0;
            let height = getCustomHeightFilterValue();
            height = height?.filter((selection) => isHeightOption(selection));
            if (height && height.length > 0) {
              const heightOption = window?.product?.customOptions?.find((option) => option.id === 'height_filter');
              customPrice = heightOption.values.find((attr) => attr.id === height[0]);
              if (customPrice) {
                customPrice = customPrice.value;
              } else {
                customPrice = 0;
              }
            }
            finalPrice += parseFloat(customPrice);
          }

          const priceElement = document.querySelector('.price-final .price-value');
          if (priceElement) {
            priceElement.textContent = `$${new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(finalPrice)}`;
          }
        } else {
          let regularPrice = '';
          if (window.product.selectedVariant) {
            regularPrice = window.product.selectedVariant.price.regular.amount.value;
            let customPrice = 0;
            let height = getCustomHeightFilterValue();
            height = height?.filter((selection) => isHeightOption(selection));
            if (height && height.length > 0) {
              const heightOption = window?.product?.customOptions?.find((option) => option.id === 'height_filter');
              customPrice = heightOption.values.find((attr) => attr.id === height[0]);
              if (customPrice) {
                customPrice = customPrice.value;
              } else {
                customPrice = 0;
              }
            }
            regularPrice += parseFloat(customPrice);
          }
          const priceElement = document.querySelector('.guest-price-value');
          if (priceElement) {
            priceElement.textContent = `$${new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(regularPrice)}`;
          }
        }
      }
    } catch (error) {
      console.error('Error updating height selection:', error);
    }

    // Trigger the same event that the dropdown triggers to update prices
    const currentSku = window.product.selectedVariant?.sku
      ? window.product.selectedVariant.sku
      : window.product.sku;
    events.emit('eds/pdp', {
      sku: currentSku,
    });

    modal.style.display = 'none';
    // eslint-disable-next-line no-use-before-define
    resetModal();
  };
  closeSpan.onclick = () => {
    modal.style.display = 'none';
    // eslint-disable-next-line no-use-before-define
    resetModal();
  };

  const swatchHeightFilter = document.querySelector('#swatch-item-height_filter select');
  const swatchHeightoptions = swatchHeightFilter.querySelectorAll('option');

  const resetModal = () => {
    roomSelectionDiv.style.display = 'block';
    measurementInputsDiv.style.display = 'none';
    recommendationDiv.style.display = 'none';
    roomForm.reset();
    const selectElement = document.getElementById('recommendedHeightOptions');
    const selectedOptionText = selectElement.options[selectElement.selectedIndex].text;
    swatchHeightoptions.forEach((option) => {
      const toMatch = `${selectedOptionText}`;
      if (option.text.includes(toMatch)) {
        option.selected = true;
      } else {
        option.selected = false;
      }
    });
    measurementTable.innerHTML = '';
    measurementHeader.textContent = 'Measurement Inputs';
  };

  // eslint-disable-next-line no-unused-vars
  const populateRecommendationDropdown = (response) => {
    heightDropdown.innerHTML = '';
    const suggestedOption = response.suggestion;
    const suggestedHeight = suggestedOption.slug;
    response.options.forEach((option) => {
      const optionElement = document.createElement('option');
      optionElement.value = option.price;
      optionElement.setAttribute('data-height-value', option.slug);
      if (option.default === true) {
        optionElement.textContent = `Standard ${option.label} +$${option.price}`;
      } else {
        optionElement.textContent = `Height ${option.label} +$${option.price}`;
      }

      if (option.slug === suggestedHeight) {
        optionElement.selected = true;
      }
      heightDropdown.appendChild(optionElement);
    });

    swatchHeightoptions.forEach((option) => {
      const toMatch = `height_${suggestedHeight}`;
      if (option.value === toMatch) {
        option.selected = true;
      } else {
        option.selected = false;
      }
    });
  };

  const populateMeasurementTable = (room) => {
    measurementTable.innerHTML = '';
    measurementHeader.textContent = room;

    const measurements = roomOptionsData.data.locations.reduce((acc, location) => {
      const locationLabel = location.label;
      const variableLabels = location.variables.map((variable) => variable.label);
      acc[locationLabel] = variableLabels;
      return acc;
    }, {});

    const measurementInputs = {};

    measurements[room].forEach((label, index) => {
      const row = document.createElement('tr');
      row.innerHTML = `
            <td>${label}</td>
            <td align="right"><input type="text" min="0" placeholder="Ft." value="0" class="feet" /></td>
            <td>Ft.</td>
            <td align="right"><input type="text" min="0" placeholder="In." value="0" class="inches" /></td>
            <td>In.</td>
        `;
      measurementTable.appendChild(row);

      if (index === 0) {
        measurementInputs.ceiling = row;
      } else if (index === 1) {
        measurementInputs.gap = row;
      } else if (index === 2) {
        measurementInputs.modifier = row;
      }
    });

    recommendationDiv.style.display = 'block';

    // Add input change listener
    measurementTable.addEventListener('input', debounce(async () => {
      const ceilingInches = {
        feet: parseFloat(measurementInputs.ceiling.querySelector('.feet').value) || 0,
        inches: parseFloat(measurementInputs.ceiling.querySelector('.inches').value) || 0,
      };

      const modifierInches = {
        feet: parseFloat(measurementInputs.modifier?.querySelector('.feet').value) || 0,
        inches: parseFloat(measurementInputs.modifier?.querySelector('.inches').value) || 0,
      };

      const gapInches = {
        feet: parseFloat(measurementInputs.gap?.querySelector('.feet').value) || 0,
        inches: parseFloat(measurementInputs.gap?.querySelector('.inches').value) || 0,
      };

      const ceilingTotalInches = ceilingInches.feet * 12 + ceilingInches.inches * 1;
      const modifierTotalInches = modifierInches.feet * 12 + modifierInches.inches * 1;
      const gapTotalInches = gapInches.feet * 12 + gapInches.inches * 1;

      if (
        ceilingTotalInches !== 0
        && (modifierTotalInches !== 0 || (!modifierInches.feet && !modifierInches.inches))
        && gapTotalInches !== 0
      ) {
        const recommendedHeight = ceilingTotalInches - gapTotalInches - (modifierTotalInches ?? 0);

        let minHeight = window?.product?.variants[0]?.attributes?.find((attr) => attr.label === 'Criteria 3')?.value;
        let oaHeight = window?.product?.variants[0]?.attributes?.find((attr) => attr.label === 'Details')?.value;

        minHeight = parseHeight(minHeight);
        oaHeight = parseHeight(oaHeight);
        const maxHeight = parseFloat(oaHeight) + 36;
        if (recommendedHeight < minHeight || recommendedHeight > maxHeight) {
          [...heightDropdown.options].find((option) => option.text.includes('Standard')).selected = true;
          swatchHeightoptions.forEach((option) => {
            if (option.value.includes('Standard')) {
              option.selected = true;
            } else {
              option.selected = false;
            }
          });
          recommendButton.textContent = 'Proceed with Standard Height';
          document.getElementById('dropin-picker-height').dispatchEvent(new Event('change'));
          const section = document.getElementsByClassName('recommendation-section')[0];
          let errorMsg = section.querySelector('.error-msg');
          if (!errorMsg) {
            errorMsg = document.createElement('p');
            errorMsg.className = 'error-msg';
            section.prepend(errorMsg);
          }
          errorMsg.textContent = (recommendedHeight < minHeight) ? `The calculated suggestion of ${recommendedHeight}" was smaller than the fixture's min height ${minHeight}".` : 'The calculated suggestion exceeds 180" please talk with a team member.';
        } else {
          recommendButton.textContent = 'Proceed with Custom Height';
          const section = document.getElementsByClassName('recommendation-section')[0];
          const errorMsg = section.querySelector('.error-msg');

          if (errorMsg) {
            errorMsg.remove();
          }
          [...heightDropdown.options].find((option) => option.text.includes(`${recommendedHeight}`)).selected = true;
          swatchHeightoptions.forEach((option) => {
            const toMatch = `${recommendedHeight}`;
            if (option.text.includes(toMatch)) {
              option.selected = true;
            } else {
              option.selected = false;
            }
          });
          document.getElementById('dropin-picker-height').dispatchEvent(new Event('change'));
        }
      }
    }, 100));
  };

  window.onclick = (event) => {
    if (event.target === modal) {
      modal.style.display = 'none';
      resetModal();
    }
  };
}// end of addCustomHeightModal() ------------------------------------------------------------

/**
 * Enable smooth scrolling for anchor links
 * Anchor's parent element should have a data-label-id attribute
 */
function enableSmoothScrolling() {
  document.querySelectorAll('a[href]').forEach((anchor) => {
    if (anchor.getAttribute('href').includes('#tab-content')) {
      anchor.addEventListener('click', (e) => {
        e.preventDefault();

        const { parentElement } = anchor;
        if (!parentElement) {
          return;
        }

        const targetElementId = parentElement.getAttribute('data-label-id');
        if (!targetElementId) {
          return;
        }

        const targetElement = document.getElementById(targetElementId);
        if (!targetElement) {
          return;
        }

        targetElement.scrollIntoView({
          behavior: 'smooth',
        });
      });
    }
  });
}

function isManual360Product() {
  return getNumberOfImages() === 1 && getPdp360AttributeValue();
}

let isUpdatingCarousel = false;
// ensureMobile360Carousel appends nodes inside the subtree its own MutationObserver
// watches; this guard stops that self-triggered mutation from reentering mid-run.
let isUpdatingMobileCarousel = false;

const CAROUSEL_360 = {
  slideClass: 'pdp-carousel__slide--360',
  thumbClass: 'pdp-carousel__thumbnail__container--360',
  iconSrc: '/icons/360thumb.svg',
  modelTitle: '3dmodel-modelviewer',
  disabledBtnClass: 'dropin-button--tertiary--disabled',
};

function is360Image(img) {
  if (!img) return false;
  const src = img.getAttribute('src') || '';
  const alt = img.alt || '';
  const title = img.title || '';
  return src.includes('360thumb')
    || alt === CAROUSEL_360.modelTitle
    || title === CAROUSEL_360.modelTitle
    || alt === '360 view';
}

function syncManual360FirstThumbnail(controls, carousel) {
  const firstThumbImg = controls?.querySelector(
    `.pdp-carousel__thumbnail__container:not(.${CAROUSEL_360.thumbClass}) img`,
  );
  const firstSlideImg = carousel?.querySelector(
    `.pdp-carousel__slide:not(.${CAROUSEL_360.slideClass}) img:not([title="${CAROUSEL_360.modelTitle}"])`,
  );
  if (firstThumbImg && firstSlideImg?.src) {
    firstThumbImg.srcset = '';
    firstThumbImg.src = firstSlideImg.src.replace(
      '$product_page_image_medium$',
      '$mini_cart_product_thumbnail$',
    );
  }
}

function normalizeManual360Slides(wrapper) {
  if (!wrapper) return;

  const slides = [...wrapper.querySelectorAll('.pdp-carousel__slide')];
  // Only assert a default active slide on the initial build. The observer re-runs
  // this on every mutation; re-activating the product slide would clobber the
  // user's 360 selection and snap the stage back to the static image.
  const hasActiveSlide = !!wrapper.querySelector('.pdp-carousel__slide--active');
  let keptProductSlide = false;

  slides.forEach((slide) => {
    // Keep our managed 360 slide — removing/re-adding it retriggers the
    // carousel MutationObserver and can loop with enableMainCarouselControls.
    if (slide.classList.contains(CAROUSEL_360.slideClass)) return;

    if (is360Image(slide.querySelector('img'))) {
      slide.remove();
      return;
    }

    if (!keptProductSlide) {
      keptProductSlide = true;
      slide.classList.remove('pdp-carousel__slide--hidden');
      if (!hasActiveSlide) slide.classList.add('pdp-carousel__slide--active');
    } else {
      slide.remove();
    }
  });
}

function is360Thumbnail(thumb) {
  return is360Image(thumb?.querySelector('img'));
}

function removeDropin360Thumbnails(controls) {
  if (!controls) return;
  [...controls.querySelectorAll(
    `.pdp-carousel__thumbnail__container:not(.${CAROUSEL_360.thumbClass})`,
  )].forEach((thumb) => {
    if (is360Thumbnail(thumb)) thumb.remove();
  });
}

function reset360Carousel() {
  // Only reset the desktop gallery carousel. The mobile carousel's 360 slide
  // comes from dropin images and must stay intact across variant changes.
  const desktop = document.querySelector('.pdp-carousel--main-image-controls');
  if (!desktop) return;

  desktop.querySelectorAll(`.${CAROUSEL_360.thumbClass}`).forEach((el) => el.remove());
  desktop.querySelectorAll(`.${CAROUSEL_360.slideClass}`).forEach((el) => el.remove());
  desktop.querySelectorAll('[data-manual-360="true"]').forEach((el) => el.remove());
  desktop.querySelectorAll('.pdp-carousel__slide img[src*="360thumb"]').forEach((img) => {
    img.closest('.pdp-carousel__slide')?.remove();
  });
}

function ensure360Slide(wrapper, { a11y = false } = {}) {
  if (!wrapper) return null;

  let slide360 = wrapper.querySelector(`.${CAROUSEL_360.slideClass}`);
  if (slide360) {
    // A variant-change re-render can swap in a fresh <img> without the title
    // tag (dropin only knows about `alt`/`label`, not our `title` marker), so
    // checkActiveSlide's selector stops matching. Re-tag defensively every call.
    const untaggedImg = slide360.querySelector('img:not([title="3dmodel-modelviewer"])');
    if (untaggedImg) {
      untaggedImg.title = CAROUSEL_360.modelTitle;
      if (!untaggedImg.alt) untaggedImg.alt = CAROUSEL_360.modelTitle;
      return slide360;
    }

    // The `variantchange` handler force-removes every <model-viewer> on the page
    // (see triggerUpdatesOnVariantChange) without putting an <img> back, leaving
    // this slide empty — rebuild the clickable icon so it can be reactivated.
    if (!slide360.querySelector('img, model-viewer')) {
      const rebuiltImg = document.createElement('img');
      rebuiltImg.src = CAROUSEL_360.iconSrc;
      rebuiltImg.alt = CAROUSEL_360.modelTitle;
      rebuiltImg.title = CAROUSEL_360.modelTitle;
      rebuiltImg.className = 'dropin-image';
      slide360.appendChild(rebuiltImg);
    }

    return slide360;
  }

  const existing = wrapper.querySelector(
    `.pdp-carousel__slide img[src*="360thumb"], .pdp-carousel__slide img[title="${CAROUSEL_360.modelTitle}"]`,
  )?.closest('.pdp-carousel__slide');

  if (existing) {
    existing.classList.add(CAROUSEL_360.slideClass);
    const existingImg = existing.querySelector('img');
    if (existingImg) existingImg.title = CAROUSEL_360.modelTitle;
    return existing;
  }

  slide360 = document.createElement('div');
  slide360.className = `pdp-carousel__slide pdp-carousel__slide--horizontal ${CAROUSEL_360.slideClass}`;
  if (a11y) {
    slide360.setAttribute('role', 'group');
    slide360.setAttribute('aria-roledescription', 'Slide');
  }

  const img360 = document.createElement('img');
  img360.src = CAROUSEL_360.iconSrc;
  img360.alt = CAROUSEL_360.modelTitle;
  img360.title = CAROUSEL_360.modelTitle;
  img360.className = 'dropin-image';
  if (a11y) img360.loading = 'lazy';

  slide360.appendChild(img360);
  wrapper.appendChild(slide360);
  return slide360;
}

function syncThumbnailsColumnCount(carousel) {
  const container = carousel?.querySelector('.pdp-carousel__controls__container--thumbnailsColumn');
  const controls = carousel?.querySelector('.pdp-carousel__controls');
  if (!container || !controls) return;

  container.classList.remove('pdp-carousel__controls__container--no-arrows');
  container.style.setProperty(
    '--nr-thumbnails',
    String(controls.querySelectorAll('.pdp-carousel__thumbnail__container').length),
  );
}

function createCarouselNavButton(direction, extraClasses = []) {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = [
    'dropin-button',
    'dropin-button--medium',
    'dropin-button--tertiary',
    'pdp-carousel__button',
    `pdp-carousel__button--${direction}`,
    ...extraClasses,
  ].filter(Boolean).join(' ');
  btn.setAttribute('aria-label', direction === 'prev' ? 'Previous' : 'Next');
  return btn;
}

function insertCarouselNavButton(carousel, btn, direction) {
  if (direction === 'prev') {
    carousel.insertBefore(btn, carousel.firstChild);
    return;
  }
  const wrapper = carousel.querySelector('.pdp-carousel__wrapper');
  if (wrapper?.nextSibling) {
    carousel.insertBefore(btn, wrapper.nextSibling);
  } else {
    carousel.appendChild(btn);
  }
}

function setCarouselButtonEnabled(btn, enabled) {
  if (!btn) return;
  const isDisabled = btn.disabled || btn.classList.contains(CAROUSEL_360.disabledBtnClass);
  if (enabled && isDisabled) {
    btn.disabled = false;
    btn.removeAttribute('disabled');
    btn.classList.remove(
      CAROUSEL_360.disabledBtnClass,
      'dropin-button--disabled',
      'pdp-carousel__button--disabled',
    );
  } else if (!enabled && !isDisabled) {
    btn.disabled = true;
    btn.classList.add(CAROUSEL_360.disabledBtnClass);
  }
}

function wire360ThumbnailClick(input) {
  input.addEventListener('click', () => {
    const currentCarousel = input.closest('.pdp-carousel');
    if (!currentCarousel) return;

    currentCarousel.querySelectorAll('.pdp-carousel__slide').forEach((slide) => {
      slide.classList.remove('pdp-carousel__slide--active');
    });

    currentCarousel.querySelectorAll('.pdp-carousel__thumbnail').forEach((thumbnail) => {
      thumbnail.checked = false;
      thumbnail.classList.remove('pdp-carousel__thumbnail--selected');
    });

    input.checked = true;
    input.classList.add('pdp-carousel__thumbnail--selected');

    const carouselWrapper = currentCarousel.querySelector('.pdp-carousel__wrapper');
    const slide360El = currentCarousel.querySelector(`.${CAROUSEL_360.slideClass}`);

    if (slide360El) {
      slide360El.classList.add('pdp-carousel__slide--active');
      carouselWrapper?.scrollTo({ left: slide360El.offsetLeft, behavior: 'auto' });
      checkActiveSlide([{ type: 'attributes', attributeName: 'class', target: slide360El }]);
      view3DModelEvent(window.product);
    }
  });
}

function append360ToCarousel(carousel, controls) {
  if (!carousel || !controls) return;

  const wrapper = carousel.querySelector('.pdp-carousel__wrapper');
  if (!wrapper) return;

  ensure360Slide(wrapper);

  // Thumb may already exist from a prior run — still ensure the slide above was created.
  if (controls.querySelector(`.${CAROUSEL_360.thumbClass}`)) {
    syncThumbnailsColumnCount(carousel);
    return;
  }

  const totalSlides = controls.querySelectorAll('.pdp-carousel__thumbnail__container').length + 1;

  const label = document.createElement('label');
  label.className = `pdp-carousel__thumbnail__container ${CAROUSEL_360.thumbClass}`;

  const input = document.createElement('input');
  input.type = 'radio';
  input.name = 'carousel-thumbnails';
  input.className = 'pdp-carousel__thumbnail';
  input.setAttribute('aria-label', `Show slide ${totalSlides} of ${totalSlides}`);

  const span = document.createElement('span');
  span.className = 'pdp-carousel__thumbnail__span';
  span.style.cursor = 'pointer';

  const img = document.createElement('img');
  img.src = CAROUSEL_360.iconSrc;
  img.alt = '360 view';
  img.width = 200;
  img.height = 248;
  img.className = 'dropin-image';

  span.appendChild(img);
  label.appendChild(input);
  label.appendChild(span);
  controls.appendChild(label);

  syncThumbnailsColumnCount(carousel);
  wire360ThumbnailClick(input);
}

function getCarouselSlides(carousel) {
  return [...(carousel?.querySelectorAll('.pdp-carousel__wrapper .pdp-carousel__slide') || [])];
}

function goToMobileCarouselSlide(carousel, index) {
  const wrapper = carousel?.querySelector('.pdp-carousel__wrapper');
  const slides = getCarouselSlides(carousel);
  if (!wrapper || !slides.length || index < 0 || index >= slides.length) return;

  slides.forEach((slide, i) => {
    slide.classList.toggle('pdp-carousel__slide--active', i === index);
    slide.classList.toggle('pdp-carousel__slide--hidden', i !== index);
  });

  wrapper.scrollTo({ left: slides[index].offsetLeft, behavior: 'smooth' });

  const prevBtn = carousel.querySelector('.pdp-carousel__button--prev');
  const nextBtn = carousel.querySelector('.pdp-carousel__button--next');
  if (prevBtn) prevBtn.disabled = index === 0;
  if (nextBtn) nextBtn.disabled = index === slides.length - 1;

  carousel.querySelectorAll('.pdp-carousel__controls__button').forEach((dot, i) => {
    dot.classList.toggle('pdp-carousel__controls__button--active', i === index);
  });

  checkActiveSlide([{
    type: 'attributes',
    attributeName: 'class',
    target: slides[index],
  }]);
}

function dedupeMobileCarouselControls(carousel) {
  const allControls = [...carousel.querySelectorAll('.pdp-carousel__controls')];
  if (allControls.length <= 1) return allControls[0] || null;

  // Prefer the dropin/direct-child row; remove every extra row.
  const keep = carousel.querySelector(':scope > .pdp-carousel__controls') || allControls[0];
  allControls.forEach((el) => {
    if (el !== keep) el.remove();
  });
  return keep;
}

function ensureMobileCarouselControls(carousel, slideCount) {
  carousel.classList.add('pdp-carousel--arrows');

  let controls = dedupeMobileCarouselControls(carousel);

  let prevBtn = carousel.querySelector(':scope > .pdp-carousel__button--prev');
  let nextBtn = carousel.querySelector(':scope > .pdp-carousel__button--next');

  if (!prevBtn) {
    prevBtn = createCarouselNavButton('prev', ['slidein-left']);
    insertCarouselNavButton(carousel, prevBtn, 'prev');
  } else {
    prevBtn.classList.add('slidein-left');
    prevBtn.classList.remove('slideout-left');
  }

  if (!nextBtn) {
    nextBtn = createCarouselNavButton('next', ['slidein-right']);
    insertCarouselNavButton(carousel, nextBtn, 'next');
  } else {
    nextBtn.classList.add('slidein-right');
    nextBtn.classList.remove('slideout-right');
  }

  if (!controls) {
    controls = document.createElement('div');
    controls.className = 'pdp-carousel__controls';
    controls.setAttribute('role', 'group');
    controls.setAttribute('aria-label', 'Carousel Controls');
    controls.dataset.manualMobile360 = 'true';
    carousel.appendChild(controls);
  }

  const existingDots = controls.querySelectorAll('.pdp-carousel__controls__button');
  if (existingDots.length !== slideCount) {
    controls.innerHTML = '';
    for (let i = 0; i < slideCount; i += 1) {
      const dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'pdp-carousel__controls__button';
      dot.setAttribute('aria-label', `Show slide ${i + 1} of ${slideCount}`);
      controls.appendChild(dot);
    }
  }

  // Delegate clicks on the carousel root so navigation survives dropin re-renders
  // that replace the arrow button nodes.
  if (!carousel.dataset.mobile360NavBound) {
    carousel.dataset.mobile360NavBound = 'true';
    carousel.addEventListener('click', (event) => {
      const next = event.target.closest('.pdp-carousel__button--next');
      const prev = event.target.closest('.pdp-carousel__button--prev');
      const dot = event.target.closest('.pdp-carousel__controls__button');
      const slides = getCarouselSlides(carousel);
      const activeIndex = slides.findIndex((slide) => slide.classList.contains('pdp-carousel__slide--active'));

      if (next && carousel.contains(next) && !next.disabled) {
        event.preventDefault();
        event.stopPropagation();
        // eslint-disable-next-line max-len
        goToMobileCarouselSlide(carousel, Math.min(slides.length - 1, Math.max(0, activeIndex) + 1));
        return;
      }

      if (prev && carousel.contains(prev) && !prev.disabled) {
        event.preventDefault();
        event.stopPropagation();
        goToMobileCarouselSlide(carousel, Math.max(0, activeIndex - 1));
        return;
      }

      if (dot && carousel.contains(dot)) {
        event.preventDefault();
        event.stopPropagation();
        const liveDots = [...carousel.querySelectorAll('.pdp-carousel__controls .pdp-carousel__controls__button')];
        goToMobileCarouselSlide(carousel, liveDots.indexOf(dot));
      }
    });
  }

  prevBtn.style.display = '';
  nextBtn.style.display = '';
  controls.style.display = '';
}

/**
 * Ensure the mobile carousel includes the 360 slide for any pdp_360 product.
 * Reuses the existing dropin dots row (never adds a second row).
 */
function ensureMobile360Carousel() {
  if (isUpdatingMobileCarousel) return;

  const mobileCarousel = document.querySelector('.pdp-product__images--carousel');
  if (!mobileCarousel) return;

  const wrapper = mobileCarousel.querySelector('.pdp-carousel__wrapper');
  if (!wrapper) return;

  if (!getPdp360AttributeValue()) {
    // Currently selected variant has no pdp_360 value — strip any leftover 360
    // slide left behind from a previously selected variant that had one.
    wrapper.querySelector(`.${CAROUSEL_360.slideClass}`)?.remove();
    return;
  }

  isUpdatingMobileCarousel = true;
  try {
    dedupeMobileCarouselControls(mobileCarousel);
    ensure360Slide(wrapper, { a11y: true });

    const slides = getCarouselSlides(mobileCarousel);
    if (slides.length < 2) return;

    slides.forEach((slide, index) => {
      slide.setAttribute('data-index', String(index));
      slide.style.setProperty('--length', String(slides.length));
      const img = slide.querySelector('img');
      if (img?.alt) {
        img.alt = img.alt.replace(/Image \d+ of \d+/, `Image ${index + 1} of ${slides.length}`);
      }
    });

    ensureMobileCarouselControls(mobileCarousel, slides.length);

    const activeIndex = Math.max(
      0,
      slides.findIndex((slide) => slide.classList.contains('pdp-carousel__slide--active')),
    );
    goToMobileCarouselSlide(mobileCarousel, activeIndex);
  } finally {
    isUpdatingMobileCarousel = false;
  }
}

function ensureDesktopArrowButtons(carousel) {
  if (!carousel?.classList.contains('pdp-carousel--main-image-controls')) return;
  if (getCarouselSlides(carousel).length < 2) return;

  let prevBtn = carousel.querySelector('.pdp-carousel__button--prev');
  let nextBtn = carousel.querySelector('.pdp-carousel__button--next');

  if (!prevBtn) {
    prevBtn = createCarouselNavButton('prev');
    insertCarouselNavButton(carousel, prevBtn, 'prev');
  }

  if (!nextBtn) {
    nextBtn = createCarouselNavButton('next');
    insertCarouselNavButton(carousel, nextBtn, 'next');
  }

  // Single-image carousels start with buttons display:none via :disabled CSS.
  prevBtn.style.display = '';
  nextBtn.style.display = '';
  setCarouselButtonEnabled(prevBtn, false);
  setCarouselButtonEnabled(nextBtn, true);
}

/**
 * Own desktop arrow navigation when a 360 slide is appended after dropin init.
 * Dropin only knows its own slide count, so it disables Next too early via
 * `dropin-button--tertiary--disabled` (pointer-events: none).
 */
function syncDesktop360Navigation(carousel) {
  if (!carousel?.classList.contains('pdp-carousel--main-image-controls')) return;
  if (!carousel.querySelector(`.${CAROUSEL_360.thumbClass}`)) return;

  const getSlides = () => getCarouselSlides(carousel);
  const getThumbs = () => [...carousel.querySelectorAll('.pdp-carousel__thumbnail')];
  const getActiveIndex = () => {
    const slides = getSlides();
    const byClass = slides.findIndex((s) => s.classList.contains('pdp-carousel__slide--active'));
    if (byClass >= 0) return byClass;

    const byThumb = getThumbs().findIndex((t) => t.checked);
    if (byThumb >= 0) return byThumb;

    const wrapper = carousel.querySelector('.pdp-carousel__wrapper');
    if (!wrapper || !slides.length) return 0;
    return slides.reduce((best, slide, idx) => {
      const bestD = Math.abs((slides[best]?.offsetLeft || 0) - wrapper.scrollLeft);
      const currD = Math.abs(slide.offsetLeft - wrapper.scrollLeft);
      return currD < bestD ? idx : best;
    }, 0);
  };

  const fixButtons = () => {
    const slides = getSlides();
    const activeIdx = getActiveIndex();
    if (!slides.length) return;

    // Only the 360 slide is truly "last" — disable Next when it's the active
    // slide, not merely when it's the upcoming slide.
    setCarouselButtonEnabled(
      carousel.querySelector('.pdp-carousel__button--next'),
      activeIdx < slides.length - 1,
    );
    setCarouselButtonEnabled(
      carousel.querySelector('.pdp-carousel__button--prev'),
      activeIdx > 0,
    );
  };

  // Re-run on every call (e.g. after a variant change re-renders slides) even if
  // the click/observer wiring below is already bound to this carousel node.
  if (carousel.dataset.desktop360GuardBound) {
    fixButtons();
    return;
  }
  carousel.dataset.desktop360GuardBound = 'true';

  const activateByIndex = (index) => {
    const slides = getSlides();
    const thumbs = getThumbs();
    const wrapper = carousel.querySelector('.pdp-carousel__wrapper');
    if (!slides[index] || !wrapper) return;

    const applyState = () => {
      slides.forEach((s, i) => {
        s.classList.toggle('pdp-carousel__slide--active', i === index);
        s.classList.remove('pdp-carousel__slide--hidden');
      });
      thumbs.forEach((t, i) => {
        t.checked = i === index;
        t.classList.toggle('pdp-carousel__thumbnail--selected', i === index);
      });
      fixButtons();
    };

    applyState();
    wrapper.scrollTo({ left: slides[index].offsetLeft, behavior: 'smooth' });
    checkActiveSlide([{ type: 'attributes', attributeName: 'class', target: slides[index] }]);

    // Re-assert active/thumb state if dropin briefly reclaims the prior slide.
    // Do not reset scrollLeft — that cancels the smooth animation.
    requestAnimationFrame(applyState);
    setTimeout(applyState, 50);
    setTimeout(applyState, 320);
  };

  carousel.addEventListener('click', (event) => {
    const clickedNext = event.target.closest('.pdp-carousel__button--next');
    const clickedPrev = event.target.closest('.pdp-carousel__button--prev');
    if (!clickedNext && !clickedPrev) return;
    if (!carousel.contains(clickedNext || clickedPrev)) return;

    event.preventDefault();
    event.stopImmediatePropagation();

    const slides = getSlides();
    const activeIdx = getActiveIndex();

    if (clickedNext && activeIdx < slides.length - 1) {
      activateByIndex(activeIdx + 1);
    } else if (clickedPrev && activeIdx > 0) {
      activateByIndex(activeIdx - 1);
    }
  }, true);

  fixButtons();

  new MutationObserver(fixButtons).observe(carousel, {
    subtree: true,
    attributes: true,
    attributeFilter: ['class', 'disabled'],
    childList: true,
  });
}

function finalizeDesktop360Setup(carousel, controls, { syncFirstThumb = false } = {}) {
  if (!controls) {
    ensureMobile360Carousel();
    return;
  }

  append360ToCarousel(carousel, controls);
  if (syncFirstThumb) syncManual360FirstThumbnail(controls, carousel);
  ensureDesktopArrowButtons(carousel);
  syncDesktop360Navigation(carousel);
  ensureMobile360Carousel();
}

function ensureDesktop360NavigationReady() {
  if (!hasAttributeValue('pdp_360')) return;

  const bind = () => {
    const c = document.querySelector('.pdp-carousel--main-image-controls');
    if (c) syncDesktop360Navigation(c);
  };
  bind();
  // Dropin can finish mounting after our first pass.
  [200, 500, 1000].forEach((d) => setTimeout(bind, d));
}

function refreshCarouselControls() {
  enableMainCarouselControls();
  ensureDesktop360NavigationReady();
  carouselbutton();
}

function carouselbutton() {
  const carouselWrapper = document.querySelector('.pdp-carousel__controls__wrapper--thumbnailsColumn.pdp-carousel__controls__wrapper');
  if (!carouselWrapper) return;

  carouselWrapper.querySelectorAll('.carousel-btn-prev, .carousel-btn-next').forEach((el) => el.remove());
  const prevButton = document.createElement('div');
  const nextButton = document.createElement('div');
  prevButton.classList.add('carousel-btn-prev', 'hidden-mobile', 'hidden');
  nextButton.classList.add('carousel-btn-next', 'hidden-mobile', 'hidden');

  carouselWrapper.insertBefore(prevButton, carouselWrapper.firstChild);
  carouselWrapper.appendChild(nextButton);

  const scrollIncrement = 500;

  carouselWrapper.addEventListener('scroll', () => {
    const maxScroll = carouselWrapper.scrollHeight
      - carouselWrapper.clientHeight;

    if (carouselWrapper.scrollTop === 0) {
      prevButton.classList.add('hidden');
    } else {
      prevButton.classList.remove('hidden');
    }

    if (carouselWrapper.scrollTop === maxScroll) {
      nextButton.classList.add('hidden');
    } else {
      nextButton.classList.remove('hidden');
    }
  });

  prevButton.addEventListener('click', () => {
    carouselWrapper.scrollBy({
      top: -scrollIncrement,
      behavior: 'smooth',
    });
  });

  nextButton.addEventListener('click', () => {
    carouselWrapper.scrollBy({
      top: scrollIncrement,
      behavior: 'smooth',
    });
  });

  const carouselObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const maxScroll = carouselWrapper.scrollHeight
          - carouselWrapper.clientHeight;
        if (maxScroll > 0) {
          nextButton.classList.remove('hidden');
        }
        observer.unobserve(entry.target);
      }
    });
  }, {
    root: null,
    rootMargin: '0px',
    threshold: 0.1,
  });

  const imageContainer = document.querySelector(
    '.pdp-carousel__controls.pdp-carousel__controls--thumbnailsColumn',
  );
  if (imageContainer) {
    carouselObserver.observe(imageContainer);
  }
}

function getPdp360AttributeValue() {
  if (isVariantSelected()) {
    return window?.product?.selectedVariant?.attributes?.find((attr) => attr.name === 'pdp_360')?.value || '';
  }
  return window?.product?.attributes?.find((attr) => attr.name === 'pdp_360')?.value || '';
}

function removeDuplicateThumbnailContainer() {
  const carousel = document.querySelector('.pdp-carousel--main-image-controls');

  if (!carousel) return;

  const containers = carousel.querySelectorAll('.pdp-carousel__controls__container--thumbnailsColumn');

  if (containers.length > 1) {
    // Remove only the last duplicate
    containers[containers.length - 1].remove();
  }
}

function enableMainCarouselControls() {
  if (isUpdatingCarousel) return;
  isUpdatingCarousel = true;

  try {
    // if there is only one image, disable the carousel controls
    if (getNumberOfImages() === 1 && !getPdp360AttributeValue()) {
      const targetElement = document.querySelector('.pdp-carousel--main-image-controls .pdp-carousel__controls__container--thumbnailsColumn');
      if (targetElement) {
        const nrThumbnails = targetElement.style.getPropertyValue('--nr-thumbnails');
        if (nrThumbnails && nrThumbnails !== '1') {
          targetElement.style.setProperty('--nr-thumbnails', 1);
        }
      }
      document.querySelector('.pdp-carousel--main-image-controls .pdp-carousel__button--prev').disabled = true;
      document.querySelector('.pdp-carousel--main-image-controls .pdp-carousel__button--next').disabled = true;
      const thumbnails = document.querySelectorAll('.pdp-carousel--main-image-controls .pdp-carousel__thumbnail__container');
      if (thumbnails.length > 1) {
        thumbnails[1].style.display = 'none';
      }
      const thumbnailSpan = document.querySelector('.pdp-carousel--main-image-controls .pdp-carousel__thumbnail__container .pdp-carousel__thumbnail__span');
      if (thumbnailSpan) {
        thumbnailSpan.style.cursor = 'default';
      }
      const element = document.querySelector('.pdp-carousel--arrows.pdp-product__images--carousel .pdp-carousel__controls');
      if (element) {
        element.style.display = 'none';
      }
      document.querySelector('.pdp-carousel--arrows.pdp-product__images--carousel .pdp-carousel__button--prev').disabled = true;
      document.querySelector('.pdp-carousel--arrows.pdp-product__images--carousel .pdp-carousel__button--next').disabled = true;
      const firstRadioButton = document.querySelector('.pdp-carousel__thumbnail__container input[type="radio"]');
      const ariaLabel = firstRadioButton ? firstRadioButton.getAttribute('aria-label') : null;
      if (ariaLabel && ariaLabel.includes('1 of 2')) {
        firstRadioButton.setAttribute('aria-label', ariaLabel.replace('1 of 2', '1 of 1'));
      }
      conditionallyUpdateImageText(document.querySelector('.pdp-carousel__thumbnail__container img'));
      document.querySelectorAll('.pdp-carousel--main-image-controls .pdp-carousel__wrapper img').forEach((image) => {
        conditionallyUpdateImageText(image);
      });
    } else {
      const carousel = document.querySelector('.pdp-carousel--main-image-controls') || document.querySelector('.pdp-product__images');
      if (!carousel) return;

      const desktopPrevBtn = document.querySelector('.pdp-carousel--main-image-controls .pdp-carousel__button--prev');
      const desktopNextBtn = document.querySelector('.pdp-carousel--main-image-controls .pdp-carousel__button--next');
      if (desktopPrevBtn) desktopPrevBtn.disabled = false;
      if (desktopNextBtn) desktopNextBtn.disabled = false;

      const thumbnails = document.querySelectorAll('.pdp-carousel--main-image-controls .pdp-carousel__thumbnail__container');
      if (thumbnails.length > 1) thumbnails[1].style.display = '';

      const thumbnailSpan = document.querySelector('.pdp-carousel--main-image-controls .pdp-carousel__thumbnail__container .pdp-carousel__thumbnail__span');
      if (thumbnailSpan) thumbnailSpan.style.cursor = 'pointer';

      const mobileControls = document.querySelector('.pdp-carousel--arrows.pdp-product__images--carousel .pdp-carousel__controls');
      if (mobileControls) mobileControls.style.display = '';

      const mobilePrevBtn = document.querySelector('.pdp-carousel--arrows.pdp-product__images--carousel .pdp-carousel__button--prev');
      const mobileNextBtn = document.querySelector('.pdp-carousel--arrows.pdp-product__images--carousel .pdp-carousel__button--next');
      if (mobilePrevBtn) mobilePrevBtn.disabled = false;
      if (mobileNextBtn) mobileNextBtn.disabled = false;

      if (getPdp360AttributeValue()) {
        let controls = carousel.querySelector('.pdp-carousel__controls');

        if (isManual360Product()) {
          normalizeManual360Slides(carousel.querySelector('.pdp-carousel__wrapper'));
          removeDropin360Thumbnails(controls);

          if (!controls) {
            carousel.classList.add('pdp-carousel--thumbnailsColumn');
            carousel.style.setProperty('--flex-carousel', 'row-reverse');
            carousel.style.setProperty('--gap', '0');

            const container = document.createElement('div');
            container.className = 'pdp-carousel__controls__container--thumbnailsColumn pdp-carousel__controls__container--no-arrows';
            container.dataset.manual360 = 'true';
            container.style.setProperty('--width', '100%');

            const thumbWrapper = document.createElement('div');
            thumbWrapper.className = 'pdp-carousel__controls__wrapper--thumbnailsColumn pdp-carousel__controls__wrapper';
            thumbWrapper.innerHTML = `
              <div class="carousel-btn-prev hidden-mobile hidden"></div>
              <div role="group" aria-label="Carousel Controls" class="pdp-carousel__controls pdp-carousel__controls--thumbnailsColumn"></div>
              <div class="carousel-btn-next hidden-mobile hidden"></div>
            `;

            container.appendChild(thumbWrapper);
            carousel.appendChild(container);
            controls = thumbWrapper.querySelector('.pdp-carousel__controls');

            const firstImg = carousel.querySelector(
              '.pdp-carousel__slide:not(.pdp-carousel__slide--360) img:not([title="3dmodel-modelviewer"])',
            );

            if (firstImg) {
              const firstThumb = document.createElement('label');
              firstThumb.className = 'pdp-carousel__thumbnail__container';
              firstThumb.innerHTML = `
                <input type="radio" checked name="carousel-thumbnails" class="pdp-carousel__thumbnail pdp-carousel__thumbnail--selected" aria-label="Show slide 1 of 2">
                <span class="pdp-carousel__thumbnail__span">
                  <img src="${firstImg.src.replace('$product_page_image_medium$', '$mini_cart_product_thumbnail$')}" class="dropin-image">
                </span>
              `;
              controls.appendChild(firstThumb);

              const firstInput = firstThumb.querySelector('.pdp-carousel__thumbnail');
              firstInput.addEventListener('click', () => {
                const currentCarousel = firstInput.closest('.pdp-carousel');
                if (!currentCarousel) return;

                const productSlide = currentCarousel.querySelector('.pdp-carousel__slide:not(.pdp-carousel__slide--360)');
                currentCarousel.querySelectorAll('.pdp-carousel__slide').forEach((slide) => {
                  slide.classList.remove('pdp-carousel__slide--active');
                });
                currentCarousel.querySelectorAll('.pdp-carousel__thumbnail').forEach((thumb) => {
                  thumb.checked = false;
                  thumb.classList.remove('pdp-carousel__thumbnail--selected');
                });

                if (productSlide) {
                  productSlide.classList.add('pdp-carousel__slide--active');
                }

                firstInput.checked = true;
                firstInput.classList.add('pdp-carousel__thumbnail--selected');
                currentCarousel.querySelector('.pdp-carousel__wrapper')?.scrollTo({
                  left: productSlide?.offsetLeft || 0,
                  behavior: 'auto',
                });

                if (productSlide) {
                  checkActiveSlide([{ type: 'attributes', attributeName: 'class', target: productSlide }]);
                }
              });
            }
          }

          if (!controls) {
            ensureMobile360Carousel();
            return;
          }

          finalizeDesktop360Setup(carousel, controls, {
            syncFirstThumb: !!controls.querySelector(`.${CAROUSEL_360.thumbClass}`),
          });
          return;
        }

        finalizeDesktop360Setup(carousel, controls);
      } else {
        ensureMobile360Carousel();
      }
    }
  } finally {
    isUpdatingCarousel = false;
  }
}

function observeMainCarouselControls() {
  // watch whenever a new "option" (variant) has been selected, and thus changes the carousel
  const mainCarousel = document.querySelector('.pdp-carousel--main-image-controls .pdp-carousel__wrapper');
  if (mainCarousel) {
    const observer = new MutationObserver(() => {
      enableMainCarouselControls();
      removeDuplicateThumbnailContainer();
      applyCarouselImagePresets();
    });
    observer.observe(mainCarousel, { childList: true, subtree: true });
  }

  const mobileCarousel = document.querySelector('.pdp-product__images--carousel');
  if (mobileCarousel) {
    const mobileObserver = new MutationObserver(() => ensureMobile360Carousel());
    mobileObserver.observe(mobileCarousel, { childList: true, subtree: true });
  }

  // On variant change the dropin re-renders the gallery, often replacing the carousel
  // wrapper node entirely (orphaning the observer above). Watch a STABLE ancestor that
  // survives the re-render so the preset is re-applied on every variant change.
  // applyCarouselImagePresets is idempotent (skips imgs already carrying the preset).
  const galleryRoot = document.querySelector('.product-details.block')
    || document.querySelector('.pdp-product');
  if (galleryRoot) {
    const presetObserver = new MutationObserver(applyCarouselImagePresets);
    presetObserver.observe(galleryRoot, {
      childList: true, subtree: true, attributes: true, attributeFilter: ['src'],
    });
  }
  applyCarouselImagePresets();
}

function updateOptionsDropDownState() {
  const options = document.querySelectorAll('.pdp-swatches .pdp-swatches__options');
  const firstOptionContainer = options[0];
  const selectedFirstOption = firstOptionContainer?.querySelector('.dropin-picker__selected');
  const firstSelect = firstOptionContainer?.querySelector('.dropin-picker > select');
  const hasFirstSelection = Boolean(firstSelect?.value);
  const shouldDisableDependents = !selectedFirstOption && !hasFirstSelection;

  Array.from(options).forEach((option, index) => {
    const select = option.querySelector('.dropin-picker > select');
    if (select && index !== 0) {
      select.disabled = shouldDisableDependents;
    }
  });
}

function observeOptionsDropDown() {
  const options = document.querySelectorAll('.pdp-swatches .pdp-swatches__options');
  const firstOption = options[0]?.querySelector('.dropin-picker');

  // Update 1st selector if any variant is active
  const activeVariant = document.querySelector('.pdp-product .variants-container .active');
  if (activeVariant && firstOption) {
    firstOption.classList.add('dropin-picker__selected');
  }

  const observer = new MutationObserver((mutationsList) => {
    mutationsList.forEach((mutation) => {
      if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
        updateOptionsDropDownState();
      }
    });
  });

  if (firstOption) {
    observer.observe(firstOption, { attributes: true });
  }
  updateOptionsDropDownState();
}

const triggerUpdatesOnVariantChange = () => {
  events.on('variantchange', async () => {
    document.querySelectorAll(
      '.carousel-btn-prev, .carousel-btn-next',
    ).forEach((el) => el.remove());

    document.querySelectorAll(
      'model-viewer',
    ).forEach((el) => el.remove());

    reset360Carousel();
    updateBadgesOnVariantChange();

    setTimeout(refreshCarouselControls, 150);
  }, { eager: true });
};

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

export default async function decorate(block) {
  // TODO Review | Prevent initial PDP call
  // if (!window.getProductPromise) {
  //   window.getProductPromise = getProduct(this.props.sku);
  // }
  // const product = await window.getProductPromise;

  // if (!product) {
  //   await loadErrorPage();
  //   return Promise.reject();
  // }

  const { product } = window;
  if (!product) {
    console.error('Product data is not available.');
    return;
  }

  // Deduplicate variant images BEFORE dropin initialization
  if (product.selectedVariant?.images && product.selectedVariant.images.length > 1) {
    const uniqueVariantImages = [];
    const seenVariantUrls = new Set();

    product.selectedVariant.images.forEach((image) => {
      const imageUrl = image.img?.src || image.url;
      if (imageUrl && !seenVariantUrls.has(imageUrl)) {
        seenVariantUrls.add(imageUrl);
        uniqueVariantImages.push(image);
      }
    });

    if (uniqueVariantImages.length !== product.selectedVariant.images.length) {
      product.selectedVariant.images = uniqueVariantImages;
    }
  }

  // Deduplicate all variants BEFORE dropin initialization
  if (product.variants && Array.isArray(product.variants)) {
    product.variants.forEach((variant) => {
      if (variant.images && variant.images.length > 1) {
        const uniqueImages = [];
        const seenUrls = new Set();

        variant.images.forEach((image) => {
          const imageUrl = image.img?.src || image.url;
          if (imageUrl && !seenUrls.has(imageUrl)) {
            seenUrls.add(imageUrl);
            uniqueImages.push(image);
          }
        });

        if (uniqueImages.length !== variant.images.length) {
          variant.images = uniqueImages;
        }
      }
    });
  }

  const models = {
    ProductDetails: {
      initialData: { ...product },
      transform: (data) => {
        // IMPORTANT: Always use the full deduplicated variant images instead of data.images
        // The dropin filters data.images to match the variant, but we want ALL unique images
        let images = [];
        if (window.product?.selectedVariant?.images) {
          // Use the variant images that we already deduplicated before initialization
          images = [...window.product.selectedVariant.images];
          // Convert variant image format to dropin format
          images = images.map((img) => ({
            url: img.img?.src || img.url,
            label: img.img?.alt || img.label || '',
            width: img.img?.width || img.width,
            height: img.img?.height || img.height,
          }));
        } else if (Array.isArray(data.images)) {
          images = [...data.images];
        }

        // Remove all duplicate images based on URL first
        const uniqueImages = [];
        const seenUrls = new Set();

        images.forEach((image) => {
          if (image && image.url && !seenUrls.has(image.url)) {
            seenUrls.add(image.url);
            uniqueImages.push(image);
          }
        });

        images = uniqueImages;

        // Add 360 viewer slide for both desktop and mobile carousels.
        // Desktop still applies manual thumbnail wiring for single-image + 360 products.
        const pdp360attr = getPdp360AttributeValue();
        if (pdp360attr && !images.some((image) => image.label === '3dmodel-modelviewer')) {
          images.push({
            url: '/icons/360thumb.svg',
            label: '3dmodel-modelviewer',
          });
        }

        // If only one unique image, duplicate it to enable the carousel
        if (images.length === 1) {
          images.push({ ...images[0] });
        }

        data.images = images;
        return data;
      },
    },
  };

  // TODO Remove: Currently variants are added to product onject
  // const variantsSkus = await getProductVariants(product.sku);

  // Initialize Dropins
  initializers.register(productApi.initialize, {
    models,
  });

  // Set Fetch Endpoint (Service)
  productApi.setEndpoint(await getConfigValue('commerce-endpoint'));

  // Set Fetch Headers (Service)
  productApi.setFetchGraphQlHeaders({
    'Content-Type': 'application/json',
    'Magento-Environment-Id': await getConfigValue('commerce-environment-id'),
    'Magento-Website-Code': await getConfigValue('commerce-website-code'),
    'Magento-Store-View-Code': await getConfigValue('commerce-store-view-code'),
    'Magento-Store-Code': await getConfigValue('commerce-store-code'),
    'Magento-Customer-Group': await getConfigValue('commerce-customer-group'),
    'x-api-key': await getConfigValue('commerce-x-api-key'),
  });

  // Listen for LCP event
  events.on('eds/lcp', async () => {
    if (!product) {
      return;
    }

    // TODO: Remove Do we need to have this with SSR?
    setJsonLdProduct(product);
    // TODO Removed as metatags are already set in SSR
    // setMetaTags(product);
    // GTM dataLayer
    viewItem(product);
    window.adobeDataLayer.push((dl) => {
      dl.push({
        productContext: {
          productId: parseInt(product.externalId, 10) || 0,
          ...product,
        },
      });
      // TODO: Remove eventInfo once collector is updated
      dl.push({ event: 'product-page-view', eventInfo: { ...dl.getState() } });
    });
    updateMagentoCacheSections(['customer', 'multiplewishlist', 'custom_height_availability_message']);
  }, { eager: true });

  let productCategory = window?.product?.attributes?.find((attr) => attr.label === 'Category');
  productCategory = productCategory?.value || '';
  if (productCategory === '') {
    productCategory = window?.product?.variants[0]?.attributes?.find((attr) => attr.label === 'Category');
    productCategory = productCategory?.value || '';
  }
  productCategory = productCategory?.split('-')[0]?.trim().toLowerCase();

  import('../../scripts/configs.js')
    // eslint-disable-next-line no-shadow
    .then(({ getLocale }) => {
      const breadcrumbs = [
        // Current Category
        { url_path_ld: `${getLocale().baseUri}/c/${productCategory}`, name: productCategory },
        // Current product
        { url_path_ld: window.location.pathname, name: window.product.name },
      ];
      setJsonLdBreadcrumbs(breadcrumbs);
    });

  if (window.product.variants.length === 0) {
    window.product.variants.push({});
  }

  // anchorOptions config for the 1st option
  const optionToAnchor = window.product.options?.[0]?.id ? [window.product.options[0].id] : [];

  // Render Containers
  // eslint-disable-next-line consistent-return
  return new Promise((resolve) => {
    setTimeout(async () => {
      try {
        await productRenderer.render(ProductDetails, {
          sku: window.product?.sku,
          hideSelectedOptionValue: true,
          hideURLParams: true,
          hideShortDescription: true,
          hideDescription: true,
          hideAttributes: true,
          disableDropdownPreselection: true,
          carousel: {
            controls: {
              desktop: 'thumbnailsColumn',
              mobile: 'dots',
            },
            arrowsOnMainImage: true,
            mobile: true,
            loopable: false, // https://jira.corp.adobe.com/browse/DATA-6246
            peak: {
              mobile: false,
              desktop: false,
            },
            gap: 'small',
            imageParams: {},
            thumbnailParams: {},
          },
          optionsConfig: {
            anchorOptions: optionToAnchor,
          },
          slots: {
            Breadcrumbs: (ctx) => Breadcrumbs(ctx),
            Title: (ctx) => Title(ctx),
            Options: (ctx) => Options(ctx),
            SKU: (ctx) => SKU(ctx),
            Quantity: (ctx) => Quantity(ctx, block),
            InfoContent: (ctx) => InfoContent(ctx),
            Actions: (ctx) => Actions(ctx, block),
            // SpecialPrice: (ctx) => SpecialPrice(ctx, block),
            Content: (ctx) => Content(ctx, block),
            GalleryContent: (ctx) => GalleryContent(ctx, block),
          },
        })(block);
        scheduleBadgesToCarousels();
        // Error will be caught in global catch for Social Native Gallery
        await loadSocialNativeGallery();
      } catch (e) {
        // eslint-disable-next-line no-console
        console.error(e);
        // eslint-disable-next-line no-undef
        await loadErrorPage();
      } finally {
        resolve();

        // Remove all duplicate images from the carousel
        if (window.product.selectedVariant.images
          && window.product.selectedVariant.images.length > 1
        ) {
          const uniqueImages = [];
          const seenUrls = new Set();

          window.product.images.forEach((image) => {
            if (!seenUrls.has(image.url)) {
              seenUrls.add(image.url);
              uniqueImages.push(image);
            }
          });

          if (uniqueImages.length !== window.product.images.length) {
            window.product.images = uniqueImages;
            // as this is the initial load, manually adjust the carousel
            enableMainCarouselControls();
          }
        }

        // Remove duplicate images from selected variant
        if (window.product.selectedVariant?.images
          && window.product.selectedVariant.images.length > 1) {
          const uniqueVariantImages = [];
          const seenVariantUrls = new Set();

          window.product.selectedVariant.images.forEach((image) => {
            const imageUrl = image.img?.src || image.url;
            if (imageUrl && !seenVariantUrls.has(imageUrl)) {
              seenVariantUrls.add(imageUrl);
              uniqueVariantImages.push(image);
            }
          });

          if (uniqueVariantImages.length !== window.product.selectedVariant.images.length) {
            window.product.selectedVariant.images = uniqueVariantImages;
          }
        }

        // Remove duplicate images from all variants
        if (window.product.variants && Array.isArray(window.product.variants)) {
          window.product.variants.forEach((variant) => {
            if (variant.images && variant.images.length > 1) {
              const uniqueImages = [];
              const seenUrls = new Set();

              variant.images.forEach((image) => {
                const imageUrl = image.img?.src || image.url;
                if (imageUrl && !seenUrls.has(imageUrl)) {
                  seenUrls.add(imageUrl);
                  uniqueImages.push(image);
                }
              });

              if (uniqueImages.length !== variant.images.length) {
                variant.images = uniqueImages;
              }
            }
          });
        }

        if (customerType === 'wholesale') {
          const swatchItem = document.getElementById('swatch-item-height_filter');
          if (swatchItem) {
            swatchItem.remove();
          }
        }

        moveSlot('.pdp-product__sku', '.pdp-product__content-column .pdp-product__column-body');
        moveSlot('.pdp-product__info-content', '.pdp-product__content-column .pdp-product__column-body .pdp-product__actions');

        // Select product options based on variant UIDs
        if (window.product && window.product.selectedVariant
          && Array.isArray(window.product.selectedVariant.selections)
          && window.product.selectedVariant.selections.length > 0) {
          try {
            selectOptionByUID(window.product.selectedVariant.selections);
          } catch (error) {
            console.error('Error selecting product options:', error);
          }
        }

        // Event listener for gallery overlay
        document.addEventListener('click', (event) => {
          if (event.target.closest('.pdp-product__column-body .pdp-carousel .pdp-carousel__wrapper')) {
            observeOverlay();
          }
        });
        await (async () => {
          const productFirstVariant = window.product.variants[0];
          if (Object.keys(productFirstVariant).length === 0) {
            return;
          }

          await initializeProductPrice(customerType);
        })();
        animateGalleryButtons();
        buildMessages();
        setup3dModelObserver();
        observeDynamicElements();
        observeBadgeTargets();
        observeOptionsDropDown();
        events.on('pdp/data', () => {
          requestAnimationFrame(() => {
            updateOptionsDropDownState();
            if (window.product?.selectedVariant?.selections?.length) {
              selectOptionByUID(window.product.selectedVariant.selections);
            }
          });
        });
        observeMainCarouselControls();
        setup3DThumbnailClickTracking();
        setTimeout(refreshCarouselControls, 150);
        setTimeout(() => {
          enableSmoothScrolling();
        }, '2000');
        triggerUpdatesOnVariantChange();
        scheduleBadgeRefresh();
        if (!isBadgeResizeListenerBound) {
          window.addEventListener('resize', scheduleBadgeRefresh);
          isBadgeResizeListenerBound = true;
        }
        events.on('pdp/values', async () => {
          scheduleBadgesToCarousels();
          addHeightLegend();
        }, { eager: true });

        events.on('eds/pdp/sku', () => {
          setTimeout(refreshCarouselControls, 150);
        });

        const productFirstVariant = window.product.variants[0];
        if (Object.keys(productFirstVariant).length === 0) {
          const options = document.querySelector('.pdp-product__options');
          const addtocart = document.querySelector('.pdp-product__actions .pdp-product__buttons');
          const quantity = document.querySelector('.pdp-product__actions .pdp-product__quantity');
          const productVariationsContainer = document.querySelector('.pdp-product__actions .product-variations-container');
          const wishlist = document.querySelector('.pdp-product__actions .pdp-product__wishlist');
          wishlist?.classList.add('alternate');
          options?.remove();
          addtocart?.remove();
          quantity?.remove();
          productVariationsContainer?.remove();
        }
      }
    }, 0);
  });
}
window.addEventListener('scroll', () => {
  const fixedDiv = document.querySelector('.pdp-product__content-attributes-header');
  const targetSection = document.querySelector('.pdp-product__content');
  const targetOffsetTop = targetSection.offsetTop - 500;
  const scrollPosition = window.scrollY;

  if (scrollPosition >= targetOffsetTop) {
    fixedDiv.classList.remove('sticky-attributes-header');
  }

  if (scrollPosition === 0) {
    fixedDiv.classList.add('sticky-attributes-header');
  }
});
