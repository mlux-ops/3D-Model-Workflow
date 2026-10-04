import { events } from '@dropins/tools/event-bus.js';
import { getCustomerType } from '../../../scripts/storage/util.js';
import { cE } from '../../../scripts/utils.js';
import { getBulbData } from '../ProductsApi.js';
import { getBulbTradePrices } from '../../../scripts/custom/pricing.js';
import { getConfigValue } from '../../../scripts/configs.js';

let allBulbData = [];
let cachedCurrency = null;

const customerType = getCustomerType();

// Cached currency getter to avoid repeated API calls
async function getCurrency() {
  if (!cachedCurrency) {
    cachedCurrency = await getConfigValue('commerce-base-currency-code');
  }
  return cachedCurrency;
}

// Helper function to check if a bulb SKU is valid
function isValidBulbSku(sku) {
  return sku && sku.trim() !== '' && sku !== 'N/A' && sku !== 'Included';
}
function formatCurrency(currency, priceData) {
  const currencyText = currency;
  const currencyLocale = {
    USD: 'en-US',
  };

  return new Intl.NumberFormat(currencyLocale[currencyText], {
    style: 'currency',
    currency,
  }).format(priceData);
}

export function toggleBulbModal() {
  const modalContent = document.querySelector('.bulb-modal-content');
  modalContent.classList.toggle('active');

  const modal = document.querySelector('.modal-overlay');
  modal.classList.toggle('active');
  document.body.classList.toggle('no-scroll');
}

async function initializeBulbCache() {
  // Extract and process all bulb SKUs from variants
  let allBulbSku = window.product.variants
    .map((variant) => variant.attributes.find((attr) => attr.name === 'bulb_sku')?.value)
    .filter(isValidBulbSku)
    .flatMap((sku) => sku.split(','))
    .map((sku) => sku.trim())
    .filter(isValidBulbSku);

  // Remove duplicates and exit early if no valid SKUs
  allBulbSku = [...new Set(allBulbSku)];
  if (allBulbSku.length === 0) {
    return [];
  }

  // Get all bulb data with trade prices
  allBulbData = await Promise.all(allBulbSku.map(async (sku) => {
    const bulbData = await getBulbData(sku);

    if (bulbData && ['trade', 'employee'].includes(customerType)) {
      const tradeBulbData = { ...bulbData };
      tradeBulbData.sku = bulbData?.custom_attributes?.find((attr) => attr.attribute_code === 'basecode')?.value;
      const tradePrices = await getBulbTradePrices(tradeBulbData.sku);
      if (tradePrices) {
        bulbData.tradeprice = tradePrices[0].tradeprice;
      }
    }

    return bulbData;
  }));

  return allBulbData.map((bulb) => bulb.sku);
}

async function buildBulbData() {
  if (allBulbData.length > 0) {
    return allBulbData.map((bulb) => bulb.sku);
  }

  return initializeBulbCache();
}

function buildBulbDropdown(bulbsData) {
  let { hostname } = window.location;
  if (!hostname.match(/^(stage\d*)\./) && hostname !== 'www.visualcomfort.com') {
    hostname = 'stage2.visualcomfort.com';
  }
  const bulbDropdownWrapper = document.createElement('div');
  bulbDropdownWrapper.classList.add('bulb-dropdown-wrapper');

  const bulbOptions = document.createElement('div');
  bulbOptions.classList.add('bulb-options');

  bulbsData.forEach((bulbData) => {
    const bulbOption = document.createElement('div');
    const bulbOptionText = document.createElement('span');
    bulbOption.classList.add('bulb-option');
    bulbOption.setAttribute('data-sku', bulbData.sku);

    // Use trade price if available, otherwise fall back to regular price
    const price = bulbData.tradeprice || bulbData.price;
    bulbOption.setAttribute('data-price', price);

    const bulbImageContainer = document.createElement('span');
    bulbImageContainer.classList.add('bulb-option-image-container');
    const bulbImage = document.createElement('img');
    const gallery = bulbData.media_gallery_entries;
    const smallImageUrl = bulbData.custom_attributes.find((attr) => attr.attribute_code === 'small_image')?.value;
    const imageUrl = smallImageUrl || gallery.find((entry) => entry.label === 'Light On')?.file || gallery[0].file;
    bulbImage.src = `https://${hostname}/media/catalog/product${imageUrl}`;
    bulbOptionText.textContent = bulbData.name;
    bulbImageContainer.appendChild(bulbImage);
    bulbOption.prepend(bulbImageContainer);
    bulbOption.appendChild(bulbOptionText);
    bulbOptions.appendChild(bulbOption);
  });

  const bulbDropdown = document.createElement('div');
  bulbDropdown.classList.add('bulb-dropdown');
  const selectedElement = document.createElement('span');
  selectedElement.classList.add('selected-option');

  // Set the first bulb as selected if available
  selectedElement.textContent = 'None Selected';

  bulbDropdown.append(selectedElement);

  bulbDropdownWrapper.appendChild(bulbDropdown);
  bulbDropdownWrapper.appendChild(bulbOptions);

  // dropdown menu logic
  // visibility toggle
  bulbOptions.classList.add('hidden');
  bulbDropdown.addEventListener('click', () => {
    bulbOptions.classList.toggle('hidden');
  });

  return bulbDropdownWrapper;
}

export async function bulbAddtoCartModal(bulbSku) {
  if (!bulbSku || bulbSku === 'N/A' || bulbSku === 'Included') {
    return;
  }

  if (allBulbData.length === 0) {
    await buildBulbData();
  }

  const currency = await getCurrency();

  const addedProductData = window.product.selectedVariant;

  const activeBulbData = allBulbData.filter((bulbData) => bulbSku.includes(bulbData.sku));
  const bulbProduct = activeBulbData[0];

  let mainImage;
  const imagesBulb = `/media/catalog/product/${bulbProduct?.custom_attributes?.find((attr) => attr.attribute_code === 'small_image')?.value}`;
  if (addedProductData.images?.length > 0 && addedProductData.images[0]?.img.src) {
    mainImage = `${addedProductData.images[0].img.src}?$mini_cart_product_thumbnail$`;
  }

  const qtyInput = document.querySelector('#pdp-qty-input');
  if (!qtyInput) throw new Error('Quantity input not found');

  const updatedQty = parseInt(qtyInput.value, 10);
  if (Number.isNaN(updatedQty) || updatedQty < 1) {
    return;
  }
  let bulbProdPrice = '';
  if (bulbProduct) {
    if (['trade', 'employee'].includes(customerType)) {
      // Use cached bulb data
      const cachedBulbData = allBulbData.find((bulb) => bulb.sku === bulbProduct.sku);
      if (cachedBulbData && cachedBulbData.tradeprice) {
        bulbProdPrice = cachedBulbData.tradeprice || '0.00';
      } else {
        // Fallback to regular price if no trade price in cache
        bulbProdPrice = bulbProduct?.price || '0.00';
      }
    } else {
      bulbProdPrice = bulbProduct?.price || '0.00';
    }
  }
  const bulbFormatPrice = parseFloat(bulbProdPrice).toFixed(2);
  const totalBulbQty = (addedProductData?.attributes?.find((attr) => attr.name === 'bulb_qty')?.value || '') * updatedQty;
  let mainProductPrice = '';
  if (['trade', 'employee'].includes(customerType)) {
    const priceText = document.querySelector('.price-container .price-final .price-value').textContent;
    const priceNumber = parseFloat(priceText.replace(/[^0-9.]/g, ''));
    mainProductPrice = (priceNumber * updatedQty).toFixed(2);
  } else {
    mainProductPrice = (addedProductData.finalPrice * updatedQty).toFixed(2);
  }
  const modal = document.createElement('div');
  modal.id = 'bulb-modal';
  modal.classList.add('modal-overlay');
  modal.classList.add('active');
  document.body.classList.add('no-scroll');

  const modalContent = document.createElement('div');
  modalContent.classList.add('modal-content');
  modalContent.classList.add('bulb-modal-content');
  modalContent.classList.add('active');
  modalContent.classList.add('bulb-popup');

  const selectedVariant = window.product.selectedVariant.selections;
  const variantOptions = window.product.options;

  const selectedVariants = selectedVariant.map((selectionId) => {
    const selectedOptions = variantOptions
      .map((option) => {
        const variant = option.values.find((value) => value.id === selectionId);
        return variant ? [option.title, variant.title] : null;
      })
      .find((item) => item !== null);

    return selectedOptions || [];
  });

  const selectedAttributes = {
    attributes: selectedVariants.map(([attribute, value]) => ({
      name: attribute,
      value,
    }))
      .sort((a, b) => {
        if (a.name.toLowerCase() === 'finish') return -1;
        if (b.name.toLowerCase() === 'finish') return 1;
        return 0;
      }),
  };

  let qtyFinishHtml;
  if (Array.isArray(selectedAttributes?.attributes)) {
    qtyFinishHtml = selectedAttributes.attributes
      .filter((attr) => attr.name !== 'Height')
      .map((attr) => `<p><label>${attr.name}: </label>${attr.value}</p>`).join('');
  }

  const closeButton = document.createElement('div');
  closeButton.classList.add('close-button');
  closeButton.innerHTML = '&times;';
  closeButton.innerHTML = `
    <button type="button" title="Close" class="action close" data-dismiss="popup">
      <span>Close</span>
    </button>`;
  closeButton.addEventListener('click', toggleBulbModal);

  const modalHeader = document.createElement('div');
  modalHeader.classList.add('modal-header');
  modalHeader.innerHTML = '<strong class="title" id="popup-title"><span>Item Added to Cart</span></strong>';

  const modalBody = document.createElement('div');
  modalBody.classList.add('modal-body');
  modalBody.classList.add('bulb-addtocart-modal');

  modalBody.innerHTML = `
    <div class="item-container">
      <div class="image-container">
        <div class="image">
            <picture>
      <source
        type="image/webp"
        srcset="
          ${mainImage}
        "
      />
      <img
        class="product-image-photo"
        src="${mainImage}"
        alt=${window.product.name}
      />
    </picture>
        </div>
      </div>
      <div class="item-details">
        <div class="name-price">
          <h3>${window.product.name}</h3>
          <p>${formatCurrency(currency, mainProductPrice)}</p>
        </div>
        <p class="brand-and-designer"><span>${window.product?.attributes?.find((attr) => attr.name === 'brand')?.value} </span> <span> | </span> <span> ${window.product?.attributes?.find((attr) => attr.name === 'designer')?.value} </span></p>
        <div class="item-number-availability">
          <p><label>Item #:</label> ${addedProductData.sku}</p>
          <p><label>${addedProductData.stockStatus === 'inStock' ? 'In Stock' : ''}</label></p>
        </div>
        <div class="qtyFinish">
          ${qtyFinishHtml}
          <p><label>Qty:</label> ${updatedQty}</</p>
        </div>
      </div>
    </div>
    <div class="bulb-item-container">
      <h2>Would you like bulbs with that?</h2>
      <hr>
      <div class="bulb-item-details">
        <div class="image-container">
          <div class="image">
            <picture>
      <source
        type="image/webp"
        srcset="
          ${imagesBulb}
        "
      />
      <img
        class="product-image-photo"
        src="${imagesBulb}"
        alt="${bulbProduct.name}"
      />
    </picture>
          </div>
        </div>
        <div class="item-details">
          <div class="name-price">
            <h3>${bulbProduct.name}</h3>
            <p> ${formatCurrency(currency, bulbFormatPrice * totalBulbQty)}</p>
          </div>
          <div class = "bulb-dropdown-wrapper">
          </div>
          <div class="qtyFinish">
          <p> ${addedProductData?.attributes?.find((attr) => attr.name === 'bulb_qty')?.value
            ? `<p><label>Qty: </label>${totalBulbQty}</p>`
            : ''}</p>
            </div>
          <div class="actions-toolbar">
          <div class="primary">
            <button class="action primary" title="Add to cart">
              <span>Add to Cart</span>
            </button>
          </div>
        </div>
        </div>

      </div>
    </div>
    <hr>
    <div>
      <a class="lightbulb-cart-link" href="/checkout/cart/" data-uw-rm-brl="PR" data-uw-original-href="https://www.visualcomfort.com/checkout/cart/">View Shopping Cart</a>
    </div>
    `;

  // construct the bulb dropdown
  const bulbDropdownWrapper = modalBody.querySelector('.bulb-dropdown-wrapper');
  bulbDropdownWrapper.replaceWith(buildBulbDropdown(activeBulbData));

  // dropdown logic
  const bulbOptions = modalBody.querySelector('.bulb-options');
  const selectedElement = modalBody.querySelector('.selected-option');
  const namePrice = modalBody.querySelector('.bulb-item-details .name-price');
  const bulbPic = modalBody.querySelector('.bulb-item-details picture');

  Array.from(bulbOptions.children).forEach((option) => {
    option.addEventListener('click', () => {
      const optionSku = option.getAttribute('data-sku');
      const bulbImg = option.querySelector('img');
      const bulbPrice = option.getAttribute('data-price');
      const totalBulbPrice = (bulbPrice * totalBulbQty).toFixed(2);
      selectedElement.textContent = option.children[1].textContent;
      selectedElement.setAttribute('data-sku', optionSku);
      bulbOptions.classList.toggle('hidden', true);
      namePrice.firstElementChild.textContent = option.children[1].textContent;
      namePrice.lastElementChild.textContent = `${formatCurrency(currency, totalBulbPrice)}`;
      bulbPic.firstElementChild.srcset = `${bulbImg.src}`;
      bulbPic.lastElementChild.src = `${bulbImg.src}`;
      bulbPic.lastElementChild.alt = `${option.children[1].textContent}`;
    });
  });

  modalContent.appendChild(closeButton);
  modalContent.appendChild(modalHeader);
  modalContent.appendChild(modalBody);

  document.body.prepend(modalContent);
  document.body.prepend(modal);
}

export async function updateBulbOptions() {
  const prodSku = window.product.sku;
  const existingCheckbox = document.querySelector(`#lightbulb-${prodSku}`);
  const isInitialLoad = !existingCheckbox?.dataset.userTouched;
  const wasChecked = isInitialLoad ? true : existingCheckbox.checked;
  const selectedElementBefore = document.querySelector(
    '.pdp-product-bulboption .selected-option',
  );
  const selectedBulbSku = existingCheckbox?.dataset.lastSelectedSku
  || selectedElementBefore?.getAttribute('data-sku')
  || null;

  let allBulbSku = [];
  let activeBulbSku = [];
  let bulbQty = 0;

  const currency = await getCurrency();

  // check cache for bulb data
  if (allBulbData.length === 0) {
    allBulbSku = await buildBulbData();
    if (allBulbSku.length === 0) {
      return;
    }
  } else {
    // If cache exists, get the SKUs from the cached data
    allBulbSku = allBulbData.map((bulb) => bulb.sku);
  }

  // Get the appropriate variant (selected or first)
  const targetVariant = window.product.selectedVariant || window.product.variants[0];
  const bulbSkuValue = targetVariant?.attributes?.find((attr) => attr.name === 'bulb_sku')?.value;

  if (!isValidBulbSku(bulbSkuValue)) {
    return;
  }

  bulbQty = targetVariant.attributes.find((attr) => attr.name === 'bulb_qty')?.value;

  if (window.product.selectedVariant) {
    activeBulbSku = bulbSkuValue.split(',').map((sku) => sku.trim()).filter(isValidBulbSku);
  } else {
    activeBulbSku = allBulbSku;
  }

  // Get current product quantity
  const totalBulbQty = bulbQty;

  // data validation
  if (activeBulbSku.length === 0 || !activeBulbSku.some(isValidBulbSku)) {
    const dropdownWrapper = document.querySelector('.pdp-product-bulboption .bulb-dropdown-wrapper');
    if (dropdownWrapper) {
      dropdownWrapper.replaceChildren();
      const bulbDropdown = document.createElement('div');
      bulbDropdown.classList.add('bulb-dropdown');
      const selectedElement = document.createElement('span');
      selectedElement.classList.add('selected-option');
      selectedElement.textContent = activeBulbSku;
      bulbDropdown.append(selectedElement);
      dropdownWrapper.prepend(bulbDropdown);
    }
    return;
  }

  const variantBulbData = allBulbData.filter((bulbData) => activeBulbSku.includes(bulbData.sku));

  const dropdownWrapper = document.querySelector('.pdp-product-bulboption .bulb-dropdown-wrapper');
  if (!dropdownWrapper) {
    // Product doesn't have bulb options - exit gracefully
    return;
  }

  dropdownWrapper.replaceChildren();
  dropdownWrapper.replaceWith(buildBulbDropdown(variantBulbData));
  const selectedElementAfter = document.querySelector(
    '.pdp-product-bulboption .selected-option',
  );

  if (!wasChecked && existingCheckbox) {
    selectedElementAfter.textContent = 'None Selected';
    selectedElementAfter.removeAttribute('data-sku');
  }

  const bulbCheckboxAfter = document.querySelector(`#lightbulb-${prodSku}`);
  if (bulbCheckboxAfter) {
    bulbCheckboxAfter.checked = wasChecked;
  }

  const bulbOptions = document.querySelector('.pdp-product-bulboption .bulb-dropdown-wrapper .bulb-options');
  const selectedElement = document.querySelector('.pdp-product-bulboption .bulb-dropdown-wrapper .selected-option');

  if (!bulbOptions || !selectedElement) {
    // eslint-disable-next-line no-console
    console.warn('Bulb options elements not found after rebuilding dropdown');
    return;
  }

  // Option selector
  const { sku } = window.product;
  Array.from(bulbOptions.children).forEach((option) => {
    option.addEventListener('click', () => {
      const bulbSku = option.getAttribute('data-sku');
      const bulbPrice = parseFloat(option.getAttribute('data-price') || '0');
      const totalBulbPrice = (bulbPrice * totalBulbQty).toFixed(2);
      selectedElement.textContent = option.children[1].textContent;
      selectedElement.setAttribute('data-sku', bulbSku);
      bulbOptions.classList.toggle('hidden', true);
      const bulbCheckbox = document.querySelector(`#lightbulb-${sku}`);
      bulbCheckbox.setAttribute('data-sku', bulbSku);
      bulbCheckbox.setAttribute('data-price', totalBulbPrice);
      document.querySelector('#lightbulb-sku').value = bulbSku;
      document.querySelector('#bulb-price-label').textContent = ` + ${formatCurrency(currency, totalBulbPrice)}`;
    });
  });

  if (wasChecked && selectedBulbSku) {
    bulbOptions
      .querySelector(`[data-sku="${selectedBulbSku}"]`)
      ?.click();
  } else if (wasChecked && isInitialLoad) {
    bulbOptions.firstElementChild?.click();
  }

  // Update visual display in pdp-product-bulbinfo section
  const bulbInfoCheckbox = document.querySelector('.pdp-product-bulbinfo input[type="checkbox"]');
  if (bulbInfoCheckbox) {
    // Update the quantity display
    const qtySpan = document.querySelector('.pdp-product-bulbinfo .qty');
    if (qtySpan) {
      qtySpan.textContent = `Qty: ${bulbQty}`;
    }
  }
}

// Function to update the productAttributeBlock with the selected variant's attributes
async function updateProductAttributeBlock() {
  if (allBulbData.length === 0) {
    await initializeBulbCache();
  }

  const product = window.product || {};
  let finalBulbPrice = '';
  const variant = window.product.selectedVariant;
  const finalVariant = variant?.attributes ? variant : window.product.variants[0];

  const currency = await getCurrency();

  // Find the bulb_sku and bulb_qty from the variant's attributes
  let bulbSku = finalVariant?.attributes?.find((attr) => attr.name === 'bulb_sku')?.value;

  if (!isValidBulbSku(bulbSku)) {
    return;
  }

  const bulbQty = finalVariant?.attributes?.find((attr) => attr.name === 'bulb_qty')?.value;

  if (bulbSku) {
    [bulbSku] = bulbSku.split(',');
  }

  if (bulbSku && bulbSku !== 'N/A' && bulbSku !== 'Included') {
    // Use cached data
    const bulbData = allBulbData.find((bulb) => bulb.sku === bulbSku);
    if (bulbData) {
      finalBulbPrice = bulbData.tradeprice || bulbData.price;
    }
  }
  const productAttributeBlock = document.getElementById('lightbulbs-list');
  // Check if bulbSku or bulbQty bulbData is missing, and return early
  if (!bulbSku || !bulbQty || !finalBulbPrice) {
    if (productAttributeBlock) {
      productAttributeBlock.innerHTML = ''; // Clear the product info if the SKU or Qty is missing
    }
    return;
  }

  if (!productAttributeBlock) {
    return;
  }

  // Calculate the total price and convert it to a decimal format
  const totalBulbPrice = (finalBulbPrice * bulbQty).toFixed(2);

  // Update the HTML content with the variant's SKU and Qty
  productAttributeBlock.innerHTML = `
    <div class="pdp-product-bulboption">
      <label class="bulb-option-label">Bulb Option</label>
      <div class = "bulb-dropdown-wrapper">
      </div>
    </div>
    <div class="pdp-product-bulbinfo">
      <input type="hidden" class="checkbox control-checkbox product-custom-option" name="lightbulb[qty]" value="${bulbQty || 0}">
      <input type="hidden" class="checkbox control-checkbox product-custom-option" id = "lightbulb-sku" name="lightbulb[sku]" value="${bulbSku || ''}">
      <!-- Checkbox to select the bulb product -->
      <input type="checkbox" checked class="checkbox control-checkbox product-custom-option" id="lightbulb-${product.sku || ''}" value="${product.sku || ''}"
      data-sku="${bulbSku || ''}" data-qty="${bulbQty || 0}" data-price="${totalBulbPrice || 0}"
      data-product-name="${product.name || ''}">
      <label class="label admin__field-label label-lightbulb" for="lightbulb-${product.sku || ''}">
        <span class="name">Add LED bulb(s)</span>
        <span class="qty">Qty: ${bulbQty || 0}</span>
        <span class="price" id="bulb-price-label"> + ${formatCurrency(currency, totalBulbPrice)}</span>
      </label>
    </div>
  `;

  updateBulbOptions();

  // Add event listener to quantity input to update bulb options when quantity changes
  const qtyInput = document.querySelector('#pdp-qty-input');
  if (qtyInput) {
    qtyInput.addEventListener('change', () => {
      updateBulbOptions();
    });
  }

  const bulbCheckbox = document.querySelector('.pdp-product-bulbinfo input[type="checkbox"]');

  bulbCheckbox.addEventListener('change', () => {
    bulbCheckbox.dataset.userTouched = 'true';

    const selectedElement = document.querySelector('.pdp-product-bulboption .selected-option');

    if (!bulbCheckbox.checked) {
      const lastSku = selectedElement?.getAttribute('data-sku');
      if (lastSku) {
        bulbCheckbox.dataset.lastSelectedSku = lastSku;
      }

      selectedElement.textContent = 'None Selected';
      selectedElement.removeAttribute('data-sku');
    } else {
      const restoreSku = bulbCheckbox.dataset.lastSelectedSku;
      if (restoreSku) {
        const optionToSelect = document.querySelector(
          `.pdp-product-bulboption .bulb-option[data-sku="${restoreSku}"]`,
        );
        optionToSelect?.click();
      } else {
        document.querySelector('.bulb-options')?.firstElementChild?.click();
      }
    }
  });
}

function formatAvailabilityMessage(availabilityMessage) {
  const messageText = availabilityMessage;
  // Pattern 1: "12 in stock ... ships by 07.22.25"
  const pattern1 = /(\d+)\s+in\s+stock.*ships\s+by\s+(\d{2}\.\d{2}\.\d{2})/i;
  // Pattern 2: "Expected to ship by 08.04.25"
  const pattern2 = /expected\s+to\s+ship\s+by\s+(\d{2}\.\d{2}\.\d{2})/i;

  const match1 = messageText?.match(pattern1);
  if (match1) {
    return `<span class="stock_value">${match1[1]}</span> <span class="stock_label">In Stock</span> <span class="ship_by_label">Ships by</span> <span class="ship_by_value">${match1[2]}</span>`;
  }

  const match2 = messageText?.match(pattern2);
  if (match2) {
    return `Expected to ship by <span class="ship_by_value">${match2[1]}</span>`;
  }

  return messageText;
}

function getProductAttributeValueByName(sku, attributeName) {
  const selectedVariant = window.product.variants.filter((v) => v.sku === sku);
  return selectedVariant[0]?.attributes?.find((attr) => attr.name === attributeName)?.value ?? null;
}

function displayInStockInfo(sku) {
  const existingStockStatusElement = document.querySelector('.stock-status');
  if (existingStockStatusElement) {
    existingStockStatusElement.remove();
  }

  const stockStatusElement = cE('div', { class: 'stock-status' });

  const availabilityMessageValue = getProductAttributeValueByName(sku, 'availability_message');
  const displayMessage = formatAvailabilityMessage(availabilityMessageValue);
  if (displayMessage) {
    stockStatusElement.innerHTML = displayMessage;
  }

  // Function to append stock status to the right place
  function appendStockStatus() {
    if (!document.querySelector('.pdp-availability')) {
      const pdpAvailabilityElement = cE('div', { class: 'pdp-availability' });
      const infoContent = document.getElementById('lightbulbs-list');
      const swatchFields = document.querySelectorAll('.pdp-swatches__field');
      const lastSwatchFieldElement = swatchFields[swatchFields.length - 1];

      if (infoContent) {
        infoContent.insertAdjacentElement('afterend', pdpAvailabilityElement);
      } else if (lastSwatchFieldElement) {
        lastSwatchFieldElement.insertAdjacentElement('afterend', pdpAvailabilityElement);
      } else {
        return; // Exit if neither element is found
      }
    }

    const pdpAvailabilityElement = document.querySelector('.pdp-availability');
    if (pdpAvailabilityElement) {
      pdpAvailabilityElement.append(stockStatusElement);
    }
  }

  // Start MutationObserver to watch for necessary elements
  const observer = new MutationObserver(() => {
    const infoContent = document.getElementById('lightbulbs-list');
    const swatchFields = document.querySelectorAll('.pdp-swatches__field');
    const lastSwatchFieldElement = swatchFields[swatchFields.length - 1];
    // Check if either of the necessary elements is available
    if (infoContent || lastSwatchFieldElement) {
      appendStockStatus(); // Append the stock status
      observer.disconnect(); // Disconnect the observer once elements are found
    }
  });

  // Start observing changes in the document body
  observer.observe(document.body, { childList: true, subtree: true });
}

function displayFutureAvailability() {
  const futureAvailabilityAnchor = cE('a', { class: 'future-availability list-collapsed' });
  futureAvailabilityAnchor.innerHTML = 'Future Availability';

  if (!document.querySelector('.pdp-availability')) {
    const pdpAvailabilityElement = cE('div', { class: 'pdp-availability' });
    let infoContenBlock;
    if (['wholesale'].includes(customerType)) {
      infoContenBlock = document.querySelector('.pdp-product__info-content');
    } else {
      infoContenBlock = document.querySelector('.pdp-product__info-content > div');
    }
    if (infoContenBlock) {
      infoContenBlock.appendChild(pdpAvailabilityElement);
    }
  }

  const futureAvailabilities = window.product?.selectedVariant?.attributes
    ? window.product.selectedVariant.attributes
    : window.product.variants[0].attributes;
  const availabilityList = futureAvailabilities.filter((x) => x.name.startsWith('due_') || x.name === 'over_60');

  const table = document.createElement('table');
  table.classList.add('future-availability-list');

  // Create table header
  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');

  // Create header cells for 'Estimated Shipping' and 'Qty'
  const thShipping = document.createElement('th');
  thShipping.textContent = 'Estimated Shipping:';
  thShipping.setAttribute('align', 'left');
  headerRow.appendChild(thShipping);

  const thQty = document.createElement('th');
  thQty.textContent = 'QTY:';
  thQty.setAttribute('align', 'left');
  headerRow.appendChild(thQty);

  // Append header row to thead
  thead.appendChild(headerRow);
  table.appendChild(thead);

  // Create table body
  const tbody = document.createElement('tbody');
  // Iterate through the data to create table rows
  availabilityList.forEach((item) => {
    const row = document.createElement('tr');

    // Extract the number from the 'name' attribute (e.g., 'due_14' -> 14)
    const days = item.name.split('_')[1];

    // Create and append 'Estimated Shipping' cell
    const shippingCell = document.createElement('td');
    shippingCell.textContent = `Expected to ship ${item.name.includes('over') ? 'over' : 'in'} ${days} days`;
    row.appendChild(shippingCell);

    // Create and append 'Qty' cell
    const qtyCell = document.createElement('td');
    qtyCell.textContent = item.value;
    row.appendChild(qtyCell);

    // Append the row to the tbody
    tbody.appendChild(row);
  });

  // Append tbody to the table
  table.appendChild(tbody);

  if (window.product.selectedVariant) {
    document.querySelector('.pdp-availability').appendChild(futureAvailabilityAnchor);
  }

  const futureAvailabilityElement = document.querySelector('.future-availability');
  if (futureAvailabilityElement) {
    document.querySelector('.pdp-availability').insertAdjacentElement('afterend', table);
  }

  futureAvailabilityAnchor.addEventListener('click', () => {
    // Toggle the visibility of the table
    if (document.querySelector('.future-availability-list')) {
      const tbl = document.querySelector('.future-availability-list');
      tbl.style.display = (tbl.style.display === 'none' || tbl.style.display === '') ? 'table' : 'none';
      futureAvailabilityAnchor.classList.toggle('list-collapsed');
    }
  });
}

export default async function InfoContent(ctx) {
  const productVariants = window.product.variants || [];
  if (customerType !== 'wholesale' && productVariants?.length > 0) {
    const productAttributeBlock = document.createElement('div');
    productAttributeBlock.classList.add('product', 'attribute', 'bulb');
    productAttributeBlock.id = 'lightbulbs-list';
    ctx.appendChild(productAttributeBlock);
    setTimeout(async () => {
      await updateProductAttributeBlock();
    }, 1000);
  }

  // eslint-disable-next-line no-shadow
  const observer = new MutationObserver((mutationsList, observer) => {
    const swatchFields = document.querySelectorAll('.pdp-swatches__field');

    // Check visibility of .pdp-swatches__field
    if (swatchFields.length > 0) {
      if (['trade', 'wholesale', 'employee'].includes(customerType) && window.product.selectedVariant) {
        displayFutureAvailability();
      }
    }

    // Disconnect observer if both are found (optional)
    if (swatchFields.length > 0) {
      observer.disconnect();
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });

  events.on('eds/pdp', async (data) => {
    if (document.querySelector('.pdp-availability')) {
      document.querySelector('.pdp-availability').remove();
    }
    if (document.querySelector('.future-availability-list')) {
      document.querySelector('.future-availability-list').remove();
    }
    displayInStockInfo(data.sku);
    if (['trade', 'wholesale', 'employee'].includes(customerType)) {
      displayFutureAvailability();
    }
  }, { eager: true });
}
