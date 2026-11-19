  // Google Analytics for Firebase (project pocket-glance-web), only with the visitor's OK.
  // Until they pick Allow nothing is loaded from Google and no cookie is set. A browser that
  // sends Global Privacy Control counts as No thanks and is not asked. The choice is kept in
  // this browser ("analytics" = yes / no); "Analytics settings" in the footer reopens the notice.
  // Measured: page views, the clicks below (download, language, links, theme), which homepage
  // sections are reached, and page speed (Firebase Performance Monitoring: load times and
  // network requests). On localhost Analytics events go to DebugView only (debug_mode) and
  // Performance Monitoring stays off unless the address has ?perf, so testing stays out of the reports.
  (function () {
    var FIREBASE = "https://www.gstatic.com/firebasejs/10.14.1/";
    var CONFIG = {
      apiKey: "AIzaSyBiRWBfELHR6EouwU6v0NQdUogoRx9AkV8",
      authDomain: "pocket-glance-web.firebaseapp.com",
      projectId: "pocket-glance-web",
      storageBucket: "pocket-glance-web.firebasestorage.app",
      messagingSenderId: "827589870312",
      appId: "1:827589870312:web:4cb8570a142c5d6510bf5d",
      measurementId: "G-KBD05D43D8"
    };
    var KEY = "analytics", LANG = "{{code}}";
    var local = /^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname);
    var box = document.getElementById("consent");
    var perfOn = !local || /[?&]perf(=|&|$)/.test(location.search);
    var sdk = null, analytics = null, perf = null, queue = [], loading = false, on = false;

    function saved() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
    function save(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

    function start() {
      on = true;
      if (analytics) { sdk.setAnalyticsCollectionEnabled(analytics, true); setPerf(true); return; }
      if (loading) return;
      loading = true;
      Promise.all([
        import(FIREBASE + "firebase-app.js"),
        import(FIREBASE + "firebase-analytics.js"),
        perfOn ? import(FIREBASE + "firebase-performance.js") : null
      ]).then(function (m) {
        sdk = m[1];
        // Measurement only: no advertising storage, no Google signals, no ad personalisation.
        sdk.setConsent({ analytics_storage: "granted", ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied" });
        var config = { allow_google_signals: false, allow_ad_personalization_signals: false };
        if (local) config.debug_mode = true;
        var app = m[0].initializeApp(CONFIG);
        analytics = sdk.initializeAnalytics(app, { config: config });
        // Page load timings are read from the browser after the fact, so starting late still counts them.
        if (m[2]) perf = m[2].getPerformance(app);
        sdk.setUserProperties(analytics, { site_language: LANG });
        if (!on) { sdk.setAnalyticsCollectionEnabled(analytics, false); setPerf(false); }
        queue.splice(0).forEach(function (e) { track(e[0], e[1]); });
      }).catch(function () { loading = false; });
    }

    function stop() {
      on = false;
      queue = [];
      if (analytics) sdk.setAnalyticsCollectionEnabled(analytics, false);
      setPerf(false);
      // And the random installation ID Firebase keeps in this browser's IndexedDB.
      try { ["firebase-installations-database", "firebase-heartbeat-database"].forEach(function (n) { indexedDB.deleteDatabase(n); }); } catch (e) {}
      // Remove the cookies Analytics set (_ga, _ga_<id>) on this host and the parent domain.
      var host = location.hostname, parts = host.split(".");
      var domains = ["", host, "." + host];
      if (parts.length > 2) domains.push("." + parts.slice(-3).join("."), "." + parts.slice(-2).join("."));
      document.cookie.split(";").forEach(function (c) {
        var name = c.split("=")[0].trim();
        if (!/^_ga/.test(name)) return;
        domains.forEach(function (d) {
          document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/" + (d ? "; domain=" + d : "");
        });
      });
    }

    function setPerf(v) { if (perf) { perf.dataCollectionEnabled = v; perf.instrumentationEnabled = v; } }

    function track(name, params) {
      if (!on) return;
      if (!analytics) { queue.push([name, params]); return; }
      sdk.logEvent(analytics, name, params);
    }

    // The notice.
    function show() { if (box) box.hidden = false; }
    if (box) box.addEventListener("click", function (e) {
      var b = e.target.closest("[data-consent]");
      if (!b) return;
      var yes = b.getAttribute("data-consent") === "yes";
      save(yes ? "yes" : "no");
      box.hidden = true;
      if (yes) start(); else stop();
    });
    document.querySelectorAll(".consent-open").forEach(function (b) {
      b.addEventListener("click", function () { show(); var f = box && box.querySelector(".yes"); if (f) f.focus(); });
    });
    var choice = saved();
    if (choice === "yes") start();
    else if (choice !== "no" && navigator.globalPrivacyControl !== true) show();

    // Homepage sections reached: once per page view, when the section's top passes the middle of the screen.
    if ("IntersectionObserver" in window) {
      var seen = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting || !on) return;
          track("section_view", { section: e.target.id || "closing" });
          seen.unobserve(e.target);
        });
      }, { rootMargin: "0px 0px -50% 0px" });
      document.querySelectorAll("#features, #private, #pro, .closer").forEach(function (s) { seen.observe(s); });
    }

    // What was clicked, and where: the bar, the phone menu, the footer, or a section of the page.
    function where(el) {
      if (el.closest(".menu")) return "menu";
      if (el.closest(".bar")) return "bar";
      if (el.closest("footer")) return "footer";
      if (el.closest(".end")) return "legal_end";
      var s = el.closest("section[id], .hero, .closer, main");
      return s ? (s.id || (s.classList.contains("hero") ? "hero" : s.classList.contains("closer") ? "closing" : "page")) : "page";
    }
    document.addEventListener("click", function (e) {
      var el = e.target.closest("a, button[data-mode]");
      if (!el || !on) return;
      var at = where(el), href = el.getAttribute("href") || "";
      if (el.matches("button[data-mode]")) {
        track("theme_toggle", { theme: el.getAttribute("data-mode"), link_location: el.closest(".lang") ? "dropdown" : at });
      } else if (/play\.google\.com/.test(href)) {
        track("play_click", { link_location: at });
      } else if (el.hasAttribute("data-lang")) {
        var to = el.getAttribute("data-lang");
        if (to !== LANG) track("language_switch", { from_lang: LANG, to_lang: to, link_location: el.closest(".lang") ? "dropdown" : at });
      } else if (/^mailto:/.test(href)) {
        track("contact_click", { link_location: at });
      } else if (href) {
        track("nav_click", { link_target: href.replace(/^(\.\.\/)+/, ""), link_text: (el.textContent || "").trim().slice(0, 60), link_location: at });
      }
    }, true);
  })();
