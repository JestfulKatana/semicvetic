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

function initReviewsCarousel() {
  document.querySelectorAll("[data-reviews-carousel]").forEach((root) => {
    const slides = Array.from(root.querySelectorAll("[data-review-slide]"));
    const dots = Array.from(root.querySelectorAll("[data-review-dot]"));
    const prevBtn = root.querySelector("[data-review-prev]");
    const nextBtn = root.querySelector("[data-review-next]");
    if (slides.length <= 1) return;

    let index = 0;
    let timer = null;

    const render = () => {
      slides.forEach((slide, i) => {
        const active = i === index;
        slide.classList.toggle("is-active", active);
        slide.setAttribute("aria-hidden", active ? "false" : "true");
      });
      dots.forEach((dot, i) => dot.classList.toggle("is-active", i === index));
    };

    const go = (delta) => {
      index = (index + delta + slides.length) % slides.length;
      render();
    };

    const goTo = (i) => {
      index = ((i % slides.length) + slides.length) % slides.length;
      render();
    };

    const resetTimer = () => {
      if (timer) clearInterval(timer);
      timer = setInterval(() => go(1), 7000);
    };

    prevBtn && prevBtn.addEventListener("click", () => { go(-1); resetTimer(); });
    nextBtn && nextBtn.addEventListener("click", () => { go(1); resetTimer(); });
    dots.forEach((dot) => {
      dot.addEventListener("click", () => {
        goTo(Number(dot.dataset.reviewDot) || 0);
        resetTimer();
      });
    });

    root.addEventListener("mouseenter", () => timer && clearInterval(timer));
    root.addEventListener("mouseleave", resetTimer);

    render();
    resetTimer();
  });
}

function initRevealOnScroll() {
  if (!("IntersectionObserver" in window)) return;
  const vh = window.innerHeight || 800;
  const targets = Array.from(document.querySelectorAll(".section"));
  // Hide only sections that are initially below the viewport
  targets.forEach((el) => {
    const rect = el.getBoundingClientRect();
    if (rect.top > vh * 0.85) {
      el.classList.add("will-reveal");
    } else {
      el.classList.add("is-revealed");
    }
  });
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-revealed");
        entry.target.classList.remove("will-reveal");
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: "0px 0px -40px 0px" });
  targets.forEach((el) => {
    if (el.classList.contains("will-reveal")) io.observe(el);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initProgramFilters();
  initTeacherFilters();
  initReviewsCarousel();
  initRevealOnScroll();
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
    } catch (error) {
      if (statusNode) {
        statusNode.textContent = error.message || "Ошибка отправки";
      }
    }
  });
});
