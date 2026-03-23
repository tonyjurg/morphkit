(function () {
  function insertSelector(versions) {
    const anchor =
      document.querySelector(".wy-side-nav-search") ||
      document.querySelector(".wy-nav-side");

    if (!anchor || !versions.length) {
      return;
    }

    const currentPath = window.location.pathname;
    const container = document.createElement("div");
    container.className = "morphkit-version-selector";

    const label = document.createElement("label");
    label.setAttribute("for", "morphkit-version-select");
    label.textContent = "Version";

    const select = document.createElement("select");
    select.id = "morphkit-version-select";

    versions.forEach((entry) => {
      const option = document.createElement("option");
      option.value = entry.url;
      option.textContent = entry.title;
      if (currentPath.indexOf("/" + entry.slug + "/") !== -1) {
        option.selected = true;
      }
      select.appendChild(option);
    });

    select.addEventListener("change", function (event) {
      const target = new URL(event.target.value, window.location.href);
      window.location.href = target.href;
    });

    container.appendChild(label);
    container.appendChild(select);
    anchor.appendChild(container);
  }

  function boot() {
    if (typeof DOCUMENTATION_OPTIONS === "undefined") {
      return;
    }

    const manifestUrl = new URL(
      DOCUMENTATION_OPTIONS.URL_ROOT + "_static/versions.json",
      window.location.href
    );

    fetch(manifestUrl)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Unable to load version manifest");
        }
        return response.json();
      })
      .then((payload) => insertSelector(payload.versions || []))
      .catch(() => {});
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
