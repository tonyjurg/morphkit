(function () {
  function bindSelector() {
    const select = document.getElementById("morphkit-version-select");
    if (!select) {
      return;
    }

    select.addEventListener("change", function (event) {
      const targetSlug = event.target.value;
      const currentPath = window.location.pathname;
      const match = currentPath.match(/^(.*\/)(stable|dev|v\d+\.\d+\.\d+)(\/.*)?$/);

      if (!match) {
        window.location.href = targetSlug + "/";
        return;
      }

      const prefix = match[1];
      const suffix = match[3] || "/";
      window.location.href = prefix + targetSlug + suffix;
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindSelector);
  } else {
    bindSelector();
  }
})();
