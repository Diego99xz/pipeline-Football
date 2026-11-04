function applySeasonFilter(select) {
  const panel = select.closest(".panel");
  if (!panel) return;

  const season = select.value;
  panel.querySelectorAll("[data-season]").forEach((item) => {
    item.hidden = season !== "all" && item.dataset.season !== season;
  });
}

document.querySelectorAll("select[data-filter]").forEach((select) => {
  select.addEventListener("change", () => applySeasonFilter(select));
  applySeasonFilter(select);
});

document.querySelector("#refresh-demo")?.addEventListener("click", () => {
  document.querySelectorAll("select[data-filter]").forEach((select) => {
    const defaultValue = select.dataset.default || select.options[0].value;
    select.value = defaultValue;
    applySeasonFilter(select);
  });
});
