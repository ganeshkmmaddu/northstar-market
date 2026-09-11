const STORAGE_KEY = "northstar-cart";

const formatCurrency = (value) => `$${Number(value || 0).toFixed(2)}`;

const state = {
  products: [],
  categories: [],
  selectedCategory: "All",
  searchTerm: "",
  cart: JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]"),
};

const cartToggle = document.getElementById("cart-toggle");
const cartPanel = document.getElementById("cart-panel");
const cartItems = document.getElementById("cart-items");
const cartCount = document.getElementById("cart-count");
const subtotalValue = document.getElementById("subtotal-value");
const productGrid = document.getElementById("product-grid");
const categoryRow = document.getElementById("category-row");
const productSearch = document.getElementById("product-search");
const checkoutModal = document.getElementById("checkout-modal");
const checkoutForm = document.getElementById("checkout-form");
const checkoutTotal = document.getElementById("checkout-total");

const fetchJson = async (url, options = {}) => {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    if (response.status === 401) {
      window.location.href = "/admin/login";
      throw new Error("Unauthorized");
    }
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || "Request failed.");
  }

  return response.json();
};

const saveCart = () => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.cart));
};

const addToCart = (product) => {
  const existing = state.cart.find((item) => item.product_id === product.id);
  if (existing) {
    existing.quantity += 1;
  } else {
    state.cart.push({ product_id: product.id, quantity: 1 });
  }

  saveCart();
  renderCart();
  openCart();
};

const updateCartQuantity = (productId, delta) => {
  const item = state.cart.find((entry) => entry.product_id === productId);
  if (!item) return;

  item.quantity += delta;
  if (item.quantity <= 0) {
    state.cart = state.cart.filter((entry) => entry.product_id !== productId);
  }
  saveCart();
  renderCart();
};

const openCart = () => {
  cartPanel.classList.add("open");
  cartPanel.setAttribute("aria-hidden", "false");
};

const closeCart = () => {
  cartPanel.classList.remove("open");
  cartPanel.setAttribute("aria-hidden", "true");
};

const getCartItemsWithDetails = () => {
  return state.cart
    .map((item) => {
      const product = state.products.find((entry) => entry.id === item.product_id);
      if (!product) return null;
      return {
        ...item,
        product,
        lineTotal: Number(product.price) * item.quantity,
      };
    })
    .filter(Boolean);
};

const renderCart = () => {
  const items = getCartItemsWithDetails();
  const total = items.reduce((sum, item) => sum + item.lineTotal, 0);
  cartCount.textContent = items.reduce((sum, item) => sum + item.quantity, 0);

  if (!items.length) {
    cartItems.innerHTML = '<div class="empty-state">Your cart is empty.</div>';
    subtotalValue.textContent = formatCurrency(0);
    checkoutTotal.textContent = formatCurrency(0);
    return;
  }

  cartItems.innerHTML = items
    .map(
      (item) => `
        <div class="cart-item">
          <img class="cart-image" src="${item.product.image_url || "https://placehold.co/300x220?text=Product"}" alt="${item.product.name}" />
          <div class="cart-item-info">
            <h4>${item.product.name}</h4>
            <div class="cart-item-actions">
              <div class="quantity-control">
                <button type="button" data-action="decrease" data-product-id="${item.product_id}">−</button>
                <span>${item.quantity}</span>
                <button type="button" data-action="increase" data-product-id="${item.product_id}">+</button>
              </div>
              <strong>${formatCurrency(item.lineTotal)}</strong>
            </div>
          </div>
        </div>
      `,
    )
    .join("");

  subtotalValue.textContent = formatCurrency(total);
  checkoutTotal.textContent = formatCurrency(total);

  cartItems.querySelectorAll("button[data-action]").forEach((button) => {
    button.addEventListener("click", () => {
      const productId = Number(button.dataset.productId);
      const action = button.dataset.action;
      updateCartQuantity(productId, action === "increase" ? 1 : -1);
    });
  });
};

const renderCategories = () => {
  const categories = ["All", ...state.categories.map((category) => category.name)];
  categoryRow.innerHTML = categories
    .map(
      (category) => `
        <button
          type="button"
          class="category-chip ${state.selectedCategory === category ? "active" : ""}"
          data-category="${category}"
        >
          ${category}
        </button>
      `,
    )
    .join("");

  categoryRow.querySelectorAll(".category-chip").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedCategory = button.dataset.category;
      renderCategories();
      renderProducts();
    });
  });
};

const renderProducts = () => {
  const filtered = state.products.filter((product) => {
    const matchesCategory = state.selectedCategory === "All" || product.category_name === state.selectedCategory;
    const matchesSearch = !state.searchTerm || `${product.name} ${product.description}`.toLowerCase().includes(state.searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  if (!filtered.length) {
    productGrid.innerHTML = '<div class="empty-state">No products match your filters.</div>';
    return;
  }

  productGrid.innerHTML = filtered
    .map(
      (product) => `
        <article class="product-card">
          <img class="product-image" src="${product.image_url || "https://placehold.co/600x500?text=Product"}" alt="${product.name}" />
          <div class="product-body">
            <div class="product-meta">
              <span class="product-category">${product.category_name}</span>
              <span class="stock">${product.stock} left</span>
            </div>
            <h3>${product.name}</h3>
            <p class="product-description">${product.description}</p>
            <div class="product-footer">
              <div>
                <div class="price">${formatCurrency(product.price)}</div>
                <small>⭐ ${product.rating}</small>
              </div>
              <div class="product-footer-actions">
                <button class="detail-link" type="button" data-detail-id="${product.id}">Details</button>
                <button class="add-to-cart" type="button" data-product-id="${product.id}">Add to cart</button>
              </div>
            </div>
          </div>
        </article>
      `,
    )
    .join("");

  productGrid.querySelectorAll(".add-to-cart").forEach((button) => {
    button.addEventListener("click", () => {
      const product = state.products.find((item) => item.id === Number(button.dataset.productId));
      if (product) addToCart(product);
    });
  });

  productGrid.querySelectorAll(".detail-link").forEach((button) => {
    button.addEventListener("click", () => {
      const productId = Number(button.dataset.detailId);
      window.location.href = `/product/${productId}`;
    });
  });
};

const loadCatalog = async () => {
  const [products, categories] = await Promise.all([
    fetchJson("/api/products"),
    fetchJson("/api/categories"),
  ]);

  state.products = products;
  state.categories = categories;
  renderCategories();
  renderProducts();
  renderCart();
};

const openCheckoutModal = () => {
  const items = getCartItemsWithDetails();
  if (!items.length) {
    alert("Your cart is empty.");
    return;
  }
  checkoutModal.classList.remove("hidden");
};

const closeCheckoutModal = () => {
  checkoutModal.classList.add("hidden");
};

const submitCheckout = async (event) => {
  event.preventDefault();
  const formData = new FormData(checkoutForm);
  const payload = {
    customer_name: formData.get("customer_name"),
    email: formData.get("email"),
    address: formData.get("address"),
    city: formData.get("city"),
    payment_method: formData.get("payment_method"),
    items: state.cart,
  };

  try {
    const result = await fetchJson("/api/orders/checkout", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    state.cart = [];
    saveCart();
    renderCart();
    closeCheckoutModal();
    checkoutForm.reset();
    window.location.assign(`/order/confirmation/${result.id}`);
  } catch (error) {
    alert(error.message);
  }
};

const initAdminPage = async () => {
  const form = document.getElementById("product-form");
  const categorySelect = document.getElementById("product-category");
  const productList = document.getElementById("admin-product-list");
  const ordersList = document.getElementById("admin-orders-list");
  const productIdInput = document.getElementById("product-id");

  if (!form || !categorySelect || !productList) {
    return;
  }

  const loadCategoryOptions = async () => {
    const categories = await fetchJson("/api/categories");
    categorySelect.innerHTML = categories
      .map((category) => `<option value="${category.id}">${category.name}</option>`)
      .join("");
  };

  const renderAdminOrders = async () => {
    if (!ordersList) return;
    const orders = await fetchJson("/api/orders");
    if (!orders.length) {
      ordersList.innerHTML = '<div class="empty-state">No orders yet.</div>';
      return;
    }

    ordersList.innerHTML = orders
      .slice(0, 6)
      .map((order) => {
        const itemSummary = order.items?.map((item) => `${item.product_name} x${item.quantity}`).join(', ') || 'No items';
        const statusOptions = ['processing', 'packed', 'shipped', 'delivered']
          .map((status) => `<option value="${status}" ${order.fulfillment_status === status ? 'selected' : ''}>${status}</option>`)
          .join('');
        return `
          <div class="order-card">
            <div class="order-card-main">
              <h4>Order #${order.id}</h4>
              <p>${order.customer_name} · ${order.email}</p>
              <p>${itemSummary}</p>
              <div class="order-status-row">
                <span class="status-pill ${order.fulfillment_status || 'processing'}">${order.fulfillment_status || 'processing'}</span>
                <select class="status-select" data-order-id="${order.id}">
                  ${statusOptions}
                </select>
              </div>
            </div>
            <strong>${formatCurrency(order.total_amount)}</strong>
          </div>
        `;
      })
      .join("");

    ordersList.querySelectorAll('.status-select').forEach((select) => {
      select.addEventListener('change', async (event) => {
        const orderId = Number(event.target.dataset.orderId);
        const fulfillmentStatus = event.target.value;
        await fetchJson(`/api/admin/orders/${orderId}/status`, {
          method: 'PATCH',
          body: JSON.stringify({ fulfillment_status: fulfillmentStatus }),
        });
        await renderAdminOrders();
      });
    });
  };

  const renderAdminProducts = async () => {
    const products = await fetchJson("/api/products");
    if (!products.length) {
      productList.innerHTML = '<div class="empty-state">No inventory items yet.</div>';
      return;
    }

    productList.innerHTML = products
      .map(
        (product) => `
          <div class="admin-product-card">
            <img src="${product.image_url || "https://placehold.co/120x120?text=Product"}" alt="${product.name}" />
            <div class="admin-product-info">
              <strong>${product.name}</strong>
              <div>${formatCurrency(product.price)} · ${product.stock} in stock</div>
            </div>
            <div class="admin-product-controls">
              <button class="action-button" type="button" data-edit-id="${product.id}">Edit</button>
              <button class="action-button" type="button" data-delete-id="${product.id}">Delete</button>
            </div>
          </div>
        `,
      )
      .join("");

    productList.querySelectorAll("[data-edit-id]").forEach((button) => {
      button.addEventListener("click", async () => {
        const product = await fetchJson(`/api/products/${button.dataset.editId}`);
        productIdInput.value = product.id;
        document.getElementById("product-name").value = product.name;
        document.getElementById("product-description").value = product.description;
        document.getElementById("product-price").value = product.price;
        document.getElementById("product-stock").value = product.stock;
        document.getElementById("product-category").value = product.category_id;
        document.getElementById("product-image").value = product.image_url || "";
        document.getElementById("product-rating").value = product.rating;
        document.getElementById("product-featured").checked = Boolean(product.featured);
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
    });

    productList.querySelectorAll("[data-delete-id]").forEach((button) => {
      button.addEventListener("click", async () => {
        if (!window.confirm("Delete this product?")) return;
        await fetchJson(`/api/admin/products/${button.dataset.deleteId}`, { method: "DELETE" });
        await renderAdminProducts();
        await renderAdminOrders();
      });
    });
  };

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = {
      name: document.getElementById("product-name").value,
      description: document.getElementById("product-description").value,
      price: Number(document.getElementById("product-price").value),
      stock: Number(document.getElementById("product-stock").value),
      category_id: Number(document.getElementById("product-category").value),
      image_url: document.getElementById("product-image").value || null,
      rating: Number(document.getElementById("product-rating").value),
      featured: document.getElementById("product-featured").checked,
    };

    const id = productIdInput.value;
    const url = id ? `/api/admin/products/${id}` : "/api/admin/products";
    const method = id ? "PUT" : "POST";

    await fetchJson(url, {
      method,
      body: JSON.stringify(payload),
    });

    form.reset();
    productIdInput.value = "";
    await renderAdminProducts();
    await renderAdminOrders();
  });

  document.getElementById("reset-form").addEventListener("click", () => {
    form.reset();
    productIdInput.value = "";
  });

  await loadCategoryOptions();
  await renderAdminProducts();
  await renderAdminOrders();
};

const bindHomePage = () => {
  if (cartToggle) {
    cartToggle.addEventListener("click", () => {
      if (cartPanel.classList.contains("open")) closeCart();
      else openCart();
    });
  }

  const closeCartButton = document.getElementById("close-cart");
  if (closeCartButton) closeCartButton.addEventListener("click", closeCart);

  const checkoutButton = document.getElementById("checkout-button");
  if (checkoutButton) checkoutButton.addEventListener("click", openCheckoutModal);

  const closeCheckoutButton = document.getElementById("close-checkout");
  if (closeCheckoutButton) closeCheckoutButton.addEventListener("click", closeCheckoutModal);

  const heroShop = document.getElementById("hero-shop");
  if (heroShop) {
    heroShop.addEventListener("click", () => {
      document.querySelector(".catalog").scrollIntoView({ behavior: "smooth" });
    });
  }

  const heroAdmin = document.getElementById("hero-admin");
  if (heroAdmin) heroAdmin.addEventListener("click", () => {
    window.location.href = "/admin";
  });

  const adminLink = document.getElementById("admin-link");
  if (adminLink) adminLink.addEventListener("click", () => {
    window.location.href = "/admin";
  });

  if (productSearch) {
    productSearch.addEventListener("input", (event) => {
      state.searchTerm = event.target.value;
      renderProducts();
    });
  }

  if (checkoutForm) checkoutForm.addEventListener("submit", submitCheckout);

  const detailButton = document.getElementById("product-detail-add");
  if (detailButton) {
    detailButton.addEventListener("click", () => {
      const productId = Number(detailButton.dataset.productId);
      const product = state.products.find((item) => item.id === productId);
      if (product) addToCart(product);
    });
  }
};

const initProductReviews = async () => {
  const reviewForm = document.getElementById("review-form");
  const reviewList = document.getElementById("review-list");
  const reviewSummary = document.getElementById("review-summary");
  if (!reviewForm || !reviewList || !reviewSummary) return;

  const productId = Number(reviewForm.dataset.productId);

  const loadReviews = async () => {
    const reviews = await fetchJson(`/api/products/${productId}/reviews`);
    if (!reviews.length) {
      reviewList.innerHTML = '<div class="empty-state">No reviews yet. Be the first to share your thoughts.</div>';
      reviewSummary.textContent = '0 reviews';
      return;
    }

    const average = reviews.reduce((sum, review) => sum + Number(review.rating), 0) / reviews.length;
    reviewSummary.textContent = `${reviews.length} review${reviews.length === 1 ? '' : 's'} · ${average.toFixed(1)} average rating`;
    reviewList.innerHTML = reviews
      .map(
        (review) => `
          <div class="review-item">
            <div class="review-header-line">
              <strong>${review.customer_name}</strong>
              <span>⭐ ${review.rating}/5</span>
            </div>
            <div class="review-date">${review.created_at}</div>
            <p>${review.comment || 'No comment provided.'}</p>
          </div>
        `,
      )
      .join("");
  };

  reviewForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(reviewForm);
    const payload = {
      customer_name: formData.get("customer_name"),
      rating: Number(formData.get("rating")),
      comment: formData.get("comment") || "",
    };

    await fetchJson(`/api/products/${productId}/reviews`, {
      method: "POST",
      body: JSON.stringify(payload),
    });

    reviewForm.reset();
    await loadReviews();
  });

  await loadReviews();
};

const initOrderHistoryPage = () => {
  const form = document.getElementById("orders-form");
  const results = document.getElementById("orders-results");
  if (!form || !results) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const email = document.getElementById("order-email").value.trim();
    if (!email) {
      results.innerHTML = '<div class="empty-state">Please enter an email address.</div>';
      return;
    }

    const [orders, loyalty] = await Promise.all([
      fetchJson(`/api/orders/history?email=${encodeURIComponent(email)}`),
      fetchJson(`/api/loyalty?email=${encodeURIComponent(email)}`),
    ]);

    const loyaltyMarkup = `
      <div class="loyalty-banner">
        <strong>Loyalty points:</strong> ${loyalty.points ?? 0}
      </div>
    `;

    if (!orders.length) {
      results.innerHTML = `${loyaltyMarkup}<div class="empty-state">No orders found for this email.</div>`;
      return;
    }

    results.innerHTML = `${loyaltyMarkup}${orders
      .map(
        (order) => `
          <div class="order-history-item">
            <div>
              <strong>Order #${order.id}</strong>
              <div>${order.created_at}</div>
              <div>${order.items?.map((item) => `${item.product_name} x${item.quantity}`).join(', ') || 'No line items.'}</div>
            </div>
            <strong>${formatCurrency(order.total_amount)}</strong>
          </div>
        `,
      )
      .join("")}`;
  });
};

const init = async () => {
  if (document.getElementById("product-grid")) {
    bindHomePage();
    await loadCatalog();
  }

  if (document.getElementById("product-detail-add")) {
    bindHomePage();
    const id = Number(document.getElementById("product-detail-add").dataset.productId);
    const response = await fetchJson(`/api/products/${id}`);
    state.products = [response];
    renderCart();
    await initProductReviews();
  }

  if (document.getElementById("product-form")) {
    await initAdminPage();
  }

  if (document.getElementById("orders-form")) {
    initOrderHistoryPage();
  }
};

init();
