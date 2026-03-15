const navToggle = document.querySelector("[data-nav-toggle]");
const nav = document.querySelector("[data-nav]");

if (navToggle && nav) {
  navToggle.addEventListener("click", () => {
    nav.classList.toggle("is-open");
  });
}

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
