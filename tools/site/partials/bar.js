  // Remember the language picked from a menu, so the English homepage can send a returning
  // visitor to it; close the language dropdown when clicking elsewhere.
  (function () {
    document.querySelectorAll("a[data-lang]").forEach(function (a) {
      a.addEventListener("click", function () { try { localStorage.setItem("lang", a.getAttribute("data-lang")); } catch (e) {} });
    });
    document.addEventListener("click", function (e) {
      var d = document.querySelector(".lang[open]");
      if (d && !d.contains(e.target)) d.removeAttribute("open");
    });
  })();

  // The bar: floats as a pill once the page scrolls; on narrow screens the menu button opens
  // the panel with the links, the languages and the download button.
  (function () {
    var bar = document.querySelector(".bar"), btn = bar.querySelector(".burger"), lang = bar.querySelector(".lang");
    function onScroll() { bar.classList.toggle("float", window.scrollY > 12); }
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    function setOpen(open) {
      bar.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.setAttribute("aria-label", open ? btn.dataset.close : btn.dataset.open);
    }
    btn.addEventListener("click", function () { setOpen(!bar.classList.contains("open")); });
    bar.querySelectorAll(".menu a").forEach(function (a) { a.addEventListener("click", function () { setOpen(false); }); });
    document.addEventListener("click", function (e) { if (!bar.contains(e.target)) setOpen(false); });
    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      if (bar.classList.contains("open")) { setOpen(false); btn.focus(); }
      if (lang.open) { lang.open = false; lang.querySelector("summary").focus(); }
    });
    // Back on a wide screen the panel is gone, so it should not reopen by itself later.
    matchMedia("(min-width: 960px)").addEventListener("change", function (m) { if (m.matches) setOpen(false); });
  })();
