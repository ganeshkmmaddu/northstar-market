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
              <button class="add-to-cart" type="button" data-product-id="${product.id}">Add to cart</button>
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

    alert(`Order #${result.id} placed successfully!`);
    state.cart = [];
    saveCart();
    renderCart();
    closeCheckoutModal();
    checkoutForm.reset();
  } catch (error) {
    alert(error.message);
  }
};

const initAdminPage = async () => {
  const form = document.getElementById("product-form");
  const categorySelect = document.getElementById("product-category");
  const productList = document.getElementById("admin-product-list");
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
  });

  document.getElementById("reset-form").addEventListener("click", () => {
    form.reset();
    productIdInput.value = "";
  });

  await loadCategoryOptions();
  await renderAdminProducts();
};

const bindHomePage = () => {
  cartToggle.addEventListener("click", () => {
    if (cartPanel.classList.contains("open")) closeCart();
    else openCart();
  });

  document.getElementById("close-cart").addEventListener("click", closeCart);
  document.getElementById("checkout-button").addEventListener("click", openCheckoutModal);
  document.getElementById("close-checkout").addEventListener("click", closeCheckoutModal);
  document.getElementById("hero-shop").addEventListener("click", () => {
    document.querySelector(".catalog").scrollIntoView({ behavior: "smooth" });
  });
  document.getElementById("hero-admin").addEventListener("click", () => {
    window.location.href = "/admin";
  });
  document.getElementById("admin-link").addEventListener("click", () => {
    window.location.href = "/admin";
  });

  productSearch.addEventListener("input", (event) => {
    state.searchTerm = event.target.value;
    renderProducts();
  });

  checkoutForm.addEventListener("submit", submitCheckout);
};

const init = async () => {
  if (document.getElementById("product-grid")) {
    bindHomePage();
    await loadCatalog();
  }

  if (document.getElementById("product-form")) {
    await initAdminPage();
  }
};

init();
