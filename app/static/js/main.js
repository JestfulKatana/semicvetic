const navToggle = document.querySelector("[data-nav-toggle]");
const mobileMenu = document.querySelector("[data-mobile-menu]");
const mobileMenuCloseBtn = document.querySelector("[data-mobile-menu-close]");
const mobileMenuLinks = mobileMenu ? mobileMenu.querySelectorAll("a") : [];

function openMobileMenu() {
  if (!mobileMenu) return;
  document.body.classList.add("is-menu-open");
  mobileMenu.classList.add("is-open");
  mobileMenu.inert = false;
  mobileMenu.setAttribute("aria-hidden", "false");
  document.querySelectorAll(".site-header, main, .site-footer").forEach((node) => { node.inert = true; });
  mobileMenuCloseBtn?.focus();
  if (navToggle) navToggle.setAttribute("aria-expanded", "true");
}

function closeMobileMenu() {
  if (!mobileMenu) return;
  document.body.classList.remove("is-menu-open");
  mobileMenu.classList.remove("is-open");
  document.querySelectorAll(".site-header, main, .site-footer").forEach((node) => { node.inert = false; });
  navToggle?.focus({ preventScroll: true });
  mobileMenu.inert = true;
  mobileMenu.setAttribute("aria-hidden", "true");
  if (navToggle) navToggle.setAttribute("aria-expanded", "false");
}

if (navToggle && mobileMenu) {
  navToggle.addEventListener("click", () => {
    if (mobileMenu.classList.contains("is-open")) {
      closeMobileMenu();
    } else {
      openMobileMenu();
    }
  });
}

if (mobileMenuCloseBtn) {
  mobileMenuCloseBtn.addEventListener("click", closeMobileMenu);
}

mobileMenuLinks.forEach((link) => {
  link.addEventListener("click", closeMobileMenu);
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Tab" && mobileMenu?.classList.contains("is-open")) {
    const focusable = [...mobileMenu.querySelectorAll("a[href], button:not([disabled])")].filter((node) => node.getClientRects().length);
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  }
  if (event.key === "Escape" && mobileMenu && mobileMenu.classList.contains("is-open")) {
    closeMobileMenu();
  }
});

function initProgramFilters() {
  const filterBar = document.querySelector("[data-program-filters]");
  const list = document.querySelector("[data-program-list]");
  const emptyNode = document.querySelector("[data-filter-empty]");
  if (!filterBar || !list) return;

  const requestedAge = new URLSearchParams(location.search).get("age");
  const validAges = [...filterBar.querySelectorAll("[data-filter-age]")].map((node) => node.dataset.filterAge);
  const state = { age: validAges.includes(requestedAge) ? requestedAge : "all", price: "all" };
  const parseAge = (value) => {
    if (value === "all") return null;
    const [min, max] = value.split("-").map(Number);
    return { min, max };
  };

  const applyFilter = () => {
    const ageRange = parseAge(state.age);
    let visible = 0;
    list.querySelectorAll(".program-line, .program-card").forEach((card) => {
      const ageMin = Number(card.dataset.ageMin || 0);
      const ageMax = Number(card.dataset.ageMax || 18);
      const priceUnit = (card.dataset.priceUnit || "").toLowerCase();
      let show = true;
      if (ageRange) {
        show = show && ageMax >= ageRange.min && ageMin <= ageRange.max;
      }
      if (state.price !== "all") {
        show = show && priceUnit === state.price;
      }
      card.hidden = !show;
      if (show) visible += 1;
    });
    if (emptyNode) emptyNode.hidden = visible !== 0;
  };

  filterBar.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const ageVal = chip.dataset.filterAge;
      const priceVal = chip.dataset.filterPrice;
      if (ageVal !== undefined) {
        state.age = ageVal;
        filterBar.querySelectorAll("[data-filter-age]").forEach((node) => { node.classList.toggle("is-active", node === chip); node.setAttribute("aria-pressed", String(node === chip)); });
      } else if (priceVal !== undefined) {
        state.price = state.price === priceVal ? "all" : priceVal;
        filterBar.querySelectorAll("[data-filter-price]").forEach((node) => {
          node.classList.toggle("is-active", node.dataset.filterPrice === state.price);
          node.setAttribute("aria-pressed", String(node.dataset.filterPrice === state.price));
        });
      }
      const url = new URL(location.href);
      if (state.age === "all") url.searchParams.delete("age"); else url.searchParams.set("age", state.age);
      history.replaceState(null, "", url);
      applyFilter();
    });
  });
  filterBar.querySelectorAll("[data-filter-age]").forEach((node) => {
    const active = node.dataset.filterAge === state.age;
    node.classList.toggle("is-active", active);
    node.setAttribute("aria-pressed", String(active));
  });
  applyFilter();
}

function initScrollState() {
  const threshold = 400;
  const update = () => {
    const scrolled = window.scrollY > threshold;
    document.body.classList.toggle("is-scrolled", scrolled);
  };
  update();
  window.addEventListener("scroll", update, { passive: true });
}

function initStickyCtaAnchor() {
  // Если на странице нет #lead-form — sticky-cta должна вести на #contact-panel.
  const hasLeadForm = !!document.getElementById("lead-form");
  if (hasLeadForm) return;
  const fallback = document.getElementById("contact-panel") ? "#contact-panel" : null;
  if (!fallback) return;
  document.querySelectorAll(".sticky-cta-action[href='#lead-form']").forEach((el) => {
    el.setAttribute("href", fallback);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initProgramFilters();
  initScrollState();
  initStickyCtaAnchor();
});

document.querySelectorAll("[data-lead-form]").forEach((form) => {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (form.getAttribute("aria-busy") === "true") return;
    const statusNode = form.querySelector("[data-form-status]");
    const submit = form.querySelector('[type="submit"]');
    const originalLabel = submit?.textContent;
    form.setAttribute("aria-busy", "true");
    if (submit) { submit.disabled = true; submit.textContent = "Отправляем…"; }
    const payload = Object.fromEntries(new FormData(form).entries());

    if (statusNode) {
      statusNode.textContent = "Отправляем…";
      statusNode.dataset.state = "pending";
    }

    try {
      const response = await fetch("/api/lead", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const isJson = response.headers.get("content-type")?.includes("application/json");
      const result = isJson ? await response.json() : {};
      if (!isJson) throw new Error("Не удалось отправить заявку. Попробуйте ещё раз или позвоните нам.");
      if (!response.ok || !result.ok) {
        throw new Error(result.message || "Не удалось отправить форму");
      }
      form.reset();
      if (statusNode) {
        statusNode.textContent = result.message;
        statusNode.dataset.state = "success";
      }
      if (typeof ym !== 'undefined') {
        ym(window._ymId || 0, 'reachGoal', 'goal_lead_submit');
      }
    } catch (error) {
      if (statusNode) {
        statusNode.textContent = error instanceof TypeError
          ? "Нет соединения. Проверьте интернет и попробуйте ещё раз — введённые данные сохранены."
          : error.message || "Не удалось отправить заявку. Попробуйте ещё раз.";
        statusNode.dataset.state = "error";
      }
    } finally {
      form.removeAttribute("aria-busy");
      if (submit) { submit.disabled = false; submit.textContent = originalLabel; }
    }
  });
});

// Native sharing with a copy-link fallback on desktop.
document.querySelectorAll("[data-share]").forEach((button) => {
  button.addEventListener("click", async () => {
    const status = button.parentElement.querySelector("[data-share-status]");
    try {
      if (navigator.share) await navigator.share({ title: document.title, url: location.href });
      else { await navigator.clipboard.writeText(location.href); if (status) status.textContent = "Ссылка скопирована"; button.textContent = "Ссылка скопирована"; }
    } catch (error) {
      if (error.name !== "AbortError" && status) status.textContent = "Скопируйте адрес страницы из строки браузера.";
    }
  });
});

(function initReviewsCarousel() {
  const tracks = document.querySelectorAll("[data-reviews-track]");
  tracks.forEach((track) => {
    const section = track.closest(".reviews-section");
    if (!section) return;
    const prevBtn = section.querySelector("[data-reviews-prev]");
    const nextBtn = section.querySelector("[data-reviews-next]");
    if (!prevBtn || !nextBtn) return;

    const stepSize = () => {
      const card = track.querySelector(".review-card");
      if (!card) return track.clientWidth;
      const style = window.getComputedStyle(track);
      const gap = parseFloat(style.columnGap || style.gap || "0") || 0;
      return card.getBoundingClientRect().width + gap;
    };

    const updateState = () => {
      const maxScroll = track.scrollWidth - track.clientWidth - 1;
      prevBtn.disabled = track.scrollLeft <= 0;
      nextBtn.disabled = track.scrollLeft >= maxScroll;
    };

    prevBtn.addEventListener("click", () => {
      track.scrollBy({ left: -stepSize(), behavior: "smooth" });
    });
    nextBtn.addEventListener("click", () => {
      track.scrollBy({ left: stepSize(), behavior: "smooth" });
    });
    track.addEventListener("scroll", updateState, { passive: true });
    window.addEventListener("resize", updateState);
    updateState();
  });
})();

// === home-cta-v2: чипы-даты + апдейт текста submit ===
(function () {
  const root = document.querySelector(".home-cta-v2");
  if (!root) return;
  const days = root.querySelectorAll(".home-cta-v2-day");
  if (!days.length) return;
  const submitBtn = root.querySelector("[data-cta-submit]");
  const slotInput = root.querySelector("[data-cta-slot-selected]");

  const DOW = ["вс", "пн", "вт", "ср", "чт", "пт", "сб"];
  const MON = ["янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"];

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  let activeLabel = "";

  function pad(n) { return String(n).padStart(2, "0"); }
  function iso(d) { return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); }
  function fmt(d) { return DOW[d.getDay()] + " " + d.getDate() + " " + MON[d.getMonth()]; }

  days.forEach((label, idx) => {
    const d = new Date(today);
    d.setDate(today.getDate() + idx);
    const input = label.querySelector("input");
    const dow = label.querySelector(".dow");
    const dnum = label.querySelector(".dnum");
    const dmon = label.querySelector(".dmon");
    if (input) input.value = iso(d);
    if (dow) dow.textContent = DOW[d.getDay()];
    if (dnum) dnum.textContent = String(d.getDate());
    if (dmon) dmon.textContent = MON[d.getMonth()];
    label.dataset.ctaDayLabel = fmt(d);
    if (label.classList.contains("is-active")) {
      activeLabel = fmt(d);
    }
  });

  function refresh() {
    if (submitBtn) submitBtn.textContent = "Записаться на " + activeLabel;
    if (slotInput) slotInput.value = activeLabel;
  }
  refresh();

  days.forEach((label) => {
    label.addEventListener("click", () => {
      days.forEach((x) => x.classList.remove("is-active"));
      label.classList.add("is-active");
      const input = label.querySelector("input");
      if (input) input.checked = true;
      activeLabel = label.dataset.ctaDayLabel || activeLabel;
      refresh();
    });
  });
})();
