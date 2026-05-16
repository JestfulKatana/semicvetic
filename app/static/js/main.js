const navToggle = document.querySelector("[data-nav-toggle]");
const mobileMenu = document.querySelector("[data-mobile-menu]");
const mobileMenuCloseBtn = document.querySelector("[data-mobile-menu-close]");
const mobileMenuLinks = mobileMenu ? mobileMenu.querySelectorAll("a") : [];

function openMobileMenu() {
  if (!mobileMenu) return;
  document.body.classList.add("is-menu-open");
  mobileMenu.classList.add("is-open");
  mobileMenu.setAttribute("aria-hidden", "false");
  if (navToggle) navToggle.setAttribute("aria-expanded", "true");
}

function closeMobileMenu() {
  if (!mobileMenu) return;
  document.body.classList.remove("is-menu-open");
  mobileMenu.classList.remove("is-open");
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
  if (event.key === "Escape" && mobileMenu && mobileMenu.classList.contains("is-open")) {
    closeMobileMenu();
  }
});

function initProgramFilters() {
  const filterBar = document.querySelector("[data-program-filters]");
  const list = document.querySelector("[data-program-list]");
  const emptyNode = document.querySelector("[data-filter-empty]");
  if (!filterBar || !list) return;

  const state = { age: "all", price: "all" };
  const parseAge = (value) => {
    if (value === "all") return null;
    const [min, max] = value.split("-").map(Number);
    return { min, max };
  };

  const applyFilter = () => {
    const ageRange = parseAge(state.age);
    let visible = 0;
    list.querySelectorAll(".program-line").forEach((card) => {
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
        filterBar.querySelectorAll("[data-filter-age]").forEach((node) => node.classList.toggle("is-active", node === chip));
      } else if (priceVal !== undefined) {
        state.price = state.price === priceVal ? "all" : priceVal;
        filterBar.querySelectorAll("[data-filter-price]").forEach((node) => {
          node.classList.toggle("is-active", node.dataset.filterPrice === state.price);
        });
      }
      applyFilter();
    });
  });
}

function initTeacherFilters() {
  const filterBar = document.querySelector("[data-teacher-filters]");
  const grid = document.querySelector("[data-teacher-grid]");
  const search = document.querySelector("[data-teacher-search]");
  const emptyNode = document.querySelector("[data-teacher-empty]");
  if (!grid) return;

  const state = { cat: "all", q: "" };
  const apply = () => {
    let visible = 0;
    grid.querySelectorAll(".teacher-card").forEach((card) => {
      const cat = (card.dataset.category || "").toLowerCase();
      const text = (card.dataset.search || "").toLowerCase();
      const catOk = state.cat === "all" || cat === state.cat;
      const qOk = !state.q || text.includes(state.q);
      const show = catOk && qOk;
      card.hidden = !show;
      if (show) visible += 1;
    });
    if (emptyNode) emptyNode.hidden = visible !== 0;
  };

  if (filterBar) {
    filterBar.querySelectorAll(".chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        const val = chip.dataset.filterCategory;
        if (val === undefined) return;
        state.cat = val;
        filterBar.querySelectorAll(".chip").forEach((node) => node.classList.toggle("is-active", node === chip));
        apply();
      });
    });
  }

  if (search) {
    search.addEventListener("input", () => {
      state.q = search.value.trim().toLowerCase();
      apply();
    });
  }
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
  initTeacherFilters();
  initScrollState();
  initStickyCtaAnchor();
});

document.querySelectorAll("[data-lead-form]").forEach((form) => {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const statusNode = form.querySelector("[data-form-status]");
    const payload = Object.fromEntries(new FormData(form).entries());

    if (statusNode) {
      statusNode.textContent = "Отправляем...";
    }

    try {
      const response = await fetch("/api/lead", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (!response.ok || !result.ok) {
        throw new Error(result.message || "Не удалось отправить форму");
      }
      form.reset();
      if (statusNode) {
        statusNode.textContent = result.message;
      }
      if (typeof ym !== 'undefined') {
        ym(window._ymId || 0, 'reachGoal', 'goal_lead_submit');
      }
    } catch (error) {
      if (statusNode) {
        statusNode.textContent = error.message || "Ошибка отправки";
      }
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
