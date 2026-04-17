const navToggle = document.querySelector("[data-nav-toggle]");
const nav = document.querySelector("[data-nav]");

if (navToggle && nav) {
  navToggle.addEventListener("click", () => {
    nav.classList.toggle("is-open");
  });
}

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

document.addEventListener("DOMContentLoaded", () => {
  initProgramFilters();
  initTeacherFilters();
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
