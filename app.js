"use strict";
/* Publish only links you are legally authorised to share. HTTPS only. */
const BUNDLE_LINKS = Object.freeze({
    1: "https://1024terabox.com/s/1ZIc39rpZ067AuHdll_2WLA",
    2: "https://1024terabox.com/s/1Uvm-lbRlZwIuLjWRaffprg",
    3: "https://1024terabox.com/s/1H_VXYWAC-qZt3qx2Nw6uKA",
    4: "https://1024terabox.com/s/11dfl5OFqPgac7tBoUsjnzQ",
    5: "https://1024terabox.com/s/1KxskEvHhaMfLyA-OOgBdHQ",
    6: "https://1024terabox.com/s/1A-oWGLIvH90DPWyqGAY1Jw",
    7: "https://1024terabox.com/s/1oKaOWVfDkMkrigERpURgUg",
    8: "https://1024terabox.com/s/1EjY0eZkY2JFDyJpKihZcIw",
    9: "https://1024terabox.com/s/13JMO9tr6W1vGDH4DCAIkPg",
    10: "https://1024terabox.com/s/1sJbqyVgz5GcW6kmvWWG9Yg"
});
/* Extra bundles shown in the "Show more links" dialog. */
const EXTRA_BUNDLE_LINKS = Object.freeze([
    Object.freeze({
        id: 11,
        url: "https://1024terabox.com/s/16iY4wSyZuoro4mUngPHTVg",
        demo: false
    }),
    Object.freeze({
        id: 12,
        url: "https://1024terabox.com/s/11-THaHvBDzfp22RyqtmKyw",
        demo: false
    }),
    Object.freeze({
        id: 13,
        url: "https://1024terabox.com/s/1GzqzS8ziGd4Qp8viQPn6og",
        demo: false
    }),
    Object.freeze({
        id: 14,
        url: "https://1024terabox.com/s/1Mt7JOsuiLPKAXiDU2sEiDQ",
        demo: false
    }),
    Object.freeze({
        id: 15,
        url: "https://1024terabox.com/s/1a9tTKMvhIWwzP8EpsrqXmQ",
        demo: false
    }),
    Object.freeze({
        id: 16,
        url: "https://1024terabox.com/s/1v9eZAZgIpYIgqt7Vpm0UXA",
        demo: false
    }),
    Object.freeze({
        id: 17,
        url: "https://1024terabox.com/s/1Sq7L1Lf3D3pZ4o88iSIpkw",
        demo: false
    }),
    Object.freeze({
        id: 18,
        url: "https://1024terabox.com/s/1cB-F-H4TIc2zkmyHAr8kkw",
        demo: false
    }),
    Object.freeze({
        id: 19,
        url: "https://1024terabox.com/s/1g_HttUwPaNeJCEeoTL8TUQ",
        demo: false
    }),
    Object.freeze({
        id: 20,
        url: "https://1024terabox.com/s/1QkVlJjsOJixlH7zweY2igw",
        demo: false
    })
]);
function getValidatedHttpsUrl(value) {
    if (typeof value !== "string") {
        return null;
    }
    const normalizedValue = value.trim();
    if (normalizedValue === "") {
        return null;
    }
    try {
        const url = new URL(normalizedValue);
        if (url.protocol !== "https:" || !url.hostname) {
            return null;
        }
        return url.href;
    } catch {
        return null;
    }
}
function enableBundle(link, destination, bundleNumber) {
    const description = link.querySelector("small");
    link.href = destination;
    link.target = "_blank";
    link.rel = "noopener noreferrer external nofollow";
    link.classList.remove("is-disabled");
    link.removeAttribute("aria-disabled");
    link.setAttribute(
        "aria-label",
        `Open TeraBox bundle ${bundleNumber} in a new tab`
    );
    if (description) {
        description.textContent = "TERABOX COLLECTION";
    }
}
function keepBundleUnavailable(link, bundleNumber) {
    const description = link.querySelector("small");
    link.removeAttribute("href");
    link.removeAttribute("target");
    link.removeAttribute("rel");
    link.classList.add("is-disabled");
    link.setAttribute("aria-disabled", "true");
    link.setAttribute(
        "aria-label",
        `TeraBox bundle ${bundleNumber} is currently unavailable`
    );
    if (description) {
        description.textContent = "CURRENTLY UNAVAILABLE";
    }
}
function configurePrimaryBundleLinks() {
    const links = document.querySelectorAll(
        ".bundle-grid [data-bundle]"
    );
    const status = document.getElementById("bundle-status");
    let availableCount = 0;
    links.forEach((link) => {
        const bundleNumber = link.dataset.bundle;
        const configuredValue = BUNDLE_LINKS[bundleNumber];
        const destination = getValidatedHttpsUrl(configuredValue);
        if (destination) {
            enableBundle(link, destination, bundleNumber);
            availableCount += 1;
            return;
        }
        keepBundleUnavailable(link, bundleNumber);
    });
    if (!status) {
        return;
    }
    if (availableCount === 0) {
        status.textContent =
            "Bundle links are currently being updated.";
        status.classList.add("is-unavailable");
        return;
    }
    const extraCount = EXTRA_BUNDLE_LINKS.filter((bundle) => {
        return !bundle.demo && getValidatedHttpsUrl(bundle.url) !== null;
    }).length;
    const extraNote = extraCount > 0
        ? ` ${extraCount} more inside Show More Links.`
        : "";
    status.textContent =
        `${availableCount} of ${links.length} main bundles are available.${extraNote}`;
    status.classList.remove("is-unavailable");
}
function createExtraBundleElement(bundle) {
    const destination = getValidatedHttpsUrl(bundle.url);
    const link = document.createElement("a");
    const liveDot = document.createElement("span");
    const icon = document.createElement("span");
    const copy = document.createElement("span");
    const title = document.createElement("strong");
    const description = document.createElement("small");
    link.className = "bundle-button extra-bundle-button";
    link.dataset.extraBundle = String(bundle.id);
    liveDot.className = "live-dot";
    liveDot.setAttribute("aria-hidden", "true");
    icon.className = "bundle-icon";
    icon.setAttribute("aria-hidden", "true");
    icon.textContent = String(bundle.id).padStart(2, "0");
    copy.className = "bundle-copy";
    title.textContent = `VIEW BUNDLE ${bundle.id}`;
    description.textContent = bundle.demo
        ? "DEMO PLACEHOLDER"
        : "TERABOX COLLECTION";
    copy.append(title, description);
    link.append(liveDot, icon, copy);
    if (!destination) {
        keepBundleUnavailable(link, bundle.id);
        return link;
    }
    link.href = destination;
    link.target = "_blank";
    link.rel = "noopener noreferrer external nofollow";
    link.setAttribute(
        "aria-label",
        bundle.demo
            ? `Open demo placeholder for bundle ${bundle.id} in a new tab`
            : `Open TeraBox bundle ${bundle.id} in a new tab`
    );
    if (bundle.demo) {
        link.classList.add("is-demo");
    }
    return link;
}
/*
 * The "Show more links" button is added at startup, but the dialog and its
 * extra bundle elements are only built on the first click. This keeps the
 * initial DOM small and the first render fast.
 */
function createMoreLinksInterface() {
    const visibleExtraBundles = EXTRA_BUNDLE_LINKS.filter((bundle) => {
        return !bundle.demo && getValidatedHttpsUrl(bundle.url) !== null;
    });
    if (visibleExtraBundles.length === 0) {
        return;
    }
    const bundleSection = document.getElementById("bundles");
    const primaryGrid = bundleSection?.querySelector(".bundle-grid");
    if (!bundleSection || !primaryGrid) {
        return;
    }
    if (document.getElementById("show-more-links")) {
        return;
    }
    const count = visibleExtraBundles.length;
    const controls = document.createElement("div");
    const showButton = document.createElement("button");
    const reducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    );
    controls.className = "more-links-controls";
    showButton.className = "more-links-button";
    showButton.id = "show-more-links";
    showButton.type = "button";
    showButton.setAttribute("aria-haspopup", "dialog");
    showButton.setAttribute("aria-expanded", "false");
    showButton.innerHTML = `
        <span class="more-links-symbol" aria-hidden="true">＋</span>
        <span>
            <strong>SHOW MORE LINKS</strong>
            <small>OPEN ${count} EXTRA BUNDLES</small>
        </span>
        <span class="more-links-arrow" aria-hidden="true">↗</span>
    `;
    controls.append(showButton);
    primaryGrid.insertAdjacentElement("afterend", controls);
    let dialog = null;
    let topCloseButton = null;
    let isClosing = false;
    let scrollMain = null;
    let scrollBody = null;
    let scrollHint = null;
    let scrollHintText = null;
    /* Shows how many extra links are still hidden below the visible area. */
    function updateScrollHint() {
        if (!dialog || !dialog.open || !scrollBody || !scrollHint) {
            return;
        }
        const limit = scrollBody.getBoundingClientRect().bottom - 8;
        const items = scrollBody.querySelectorAll(".extra-bundle-button");
        let remaining = 0;
        items.forEach((item) => {
            if (item.getBoundingClientRect().bottom > limit) {
                remaining += 1;
            }
        });
        scrollHint.hidden = remaining === 0;
        scrollMain.classList.toggle("has-more", remaining > 0);
        if (remaining > 0) {
            const label = remaining === 1
                ? "1 MORE LINK BELOW"
                : `${remaining} MORE LINKS BELOW`;
            scrollHintText.textContent = label;
            scrollHint.setAttribute(
                "aria-label",
                `Scroll down to see ${remaining} more bundle ${remaining === 1 ? "link" : "links"}`
            );
        }
    }
    function buildDialog() {
        dialog = document.createElement("dialog");
        dialog.className = "extra-dialog";
        dialog.id = "extra-bundles-dialog";
        dialog.setAttribute("aria-labelledby", "extra-bundles-title");
        dialog.setAttribute("aria-describedby", "extra-bundles-description");
        dialog.innerHTML = `
            <div class="extra-dialog-panel">
                <header class="extra-dialog-header">
                    <button
                        class="extra-dialog-x"
                        id="extra-dialog-x"
                        type="button"
                        aria-label="Close the extra bundle links"
                    >
                        <span aria-hidden="true">×</span>
                    </button>
                    <div class="extra-bundles-heading">
                        <span class="extra-bundles-eyebrow">ADDITIONAL COLLECTION</span>
                        <h3 id="extra-bundles-title" tabindex="-1">${count} EXTRA BUNDLE LINKS</h3>
                        <p id="extra-bundles-description">
                            More bundle links from the same directory.
                            Scroll down to see all ${count} links.
                        </p>
                    </div>
                </header>
                <div class="extra-dialog-main" id="extra-dialog-main">
                    <div class="extra-dialog-body">
                        <div
                            class="bundle-grid extra-bundle-grid"
                            aria-label="Additional video bundle links"
                        ></div>
                    </div>
                    <div class="extra-scroll-fade" aria-hidden="true"></div>
                    <button
                        class="extra-scroll-hint"
                        id="extra-scroll-hint"
                        type="button"
                        hidden
                    >
                        <span class="extra-scroll-hint-arrow" aria-hidden="true">&darr;</span>
                        <span id="extra-scroll-hint-text">SCROLL FOR MORE LINKS</span>
                    </button>
                </div>
                <footer class="extra-dialog-footer">
                    <a
                        class="extra-dialog-play"
                        href="https://play.google.com/store/apps/details?id=com.dubox.drive"
                        target="_blank"
                        rel="noopener noreferrer external"
                        aria-label="Download the official TeraBox app on Google Play (opens in a new tab)"
                    >
                        <span class="extra-dialog-play-icon" aria-hidden="true">
                            <svg viewBox="0 0 24 24" width="24" height="24" focusable="false">
                                <polygon points="4,2.2 12,12 4,21.8" fill="#00C3FF"/>
                                <polygon points="4,2.2 12,12 15.5,9.03" fill="#00F076"/>
                                <polygon points="4,21.8 12,12 15.5,14.97" fill="#FF3A44"/>
                                <polygon points="12,12 15.5,9.03 20.5,12 15.5,14.97" fill="#FFD500"/>
                            </svg>
                        </span>
                        <span class="extra-dialog-play-copy">
                            <small>DOWNLOAD THE OFFICIAL APP</small>
                            <strong>TeraBox on Google Play</strong>
                        </span>
                        <span class="extra-dialog-play-arrow" aria-hidden="true">↗</span>
                    </a>
                </footer>
            </div>
        `;
        const extraGrid = dialog.querySelector(".extra-bundle-grid");
        visibleExtraBundles.forEach((bundle) => {
            extraGrid.append(createExtraBundleElement(bundle));
        });
        document.body.append(dialog);
        showButton.setAttribute("aria-controls", dialog.id);
        scrollMain = dialog.querySelector("#extra-dialog-main");
        scrollBody = dialog.querySelector(".extra-dialog-body");
        scrollHint = dialog.querySelector("#extra-scroll-hint");
        scrollHintText = dialog.querySelector("#extra-scroll-hint-text");
        scrollBody.addEventListener("scroll", updateScrollHint, {
            passive: true
        });
        scrollHint.addEventListener("click", () => {
            scrollBody.scrollBy({
                top: Math.max(120, Math.round(scrollBody.clientHeight * 0.75)),
                behavior: reducedMotion.matches ? "auto" : "smooth"
            });
        });
        window.addEventListener("resize", updateScrollHint);
        topCloseButton = dialog.querySelector("#extra-dialog-x");
        topCloseButton.addEventListener("click", closeExtraBundles);
        dialog.addEventListener("click", (event) => {
            if (event.target === dialog) {
                closeExtraBundles();
            }
        });
        dialog.addEventListener("close", handleClosed);
    }
    function openExtraBundles() {
        if (!dialog) {
            buildDialog();
        }
        if (dialog.open) {
            return;
        }
        isClosing = false;
        dialog.classList.remove("is-closing");
        if (typeof dialog.showModal === "function") {
            dialog.showModal();
        } else {
            dialog.setAttribute("open", "");
        }
        document.body.classList.add("dialog-is-open");
        showButton.setAttribute("aria-expanded", "true");
        const body = dialog.querySelector(".extra-dialog-body");
        if (body) {
            body.scrollTop = 0;
        }
        if (topCloseButton instanceof HTMLButtonElement) {
            topCloseButton.focus({
                preventScroll: true
            });
        }
        window.requestAnimationFrame(updateScrollHint);
    }
    function finishClosing() {
        dialog.classList.remove("is-closing");
        isClosing = false;
        if (dialog.open && typeof dialog.close === "function") {
            dialog.close();
        } else {
            dialog.removeAttribute("open");
            handleClosed();
        }
    }
    function closeExtraBundles() {
        if (!dialog || !dialog.open || isClosing) {
            return;
        }
        if (reducedMotion.matches) {
            finishClosing();
            return;
        }
        isClosing = true;
        dialog.classList.add("is-closing");
        window.setTimeout(finishClosing, 190);
    }
    function handleClosed() {
        document.body.classList.remove("dialog-is-open");
        showButton.setAttribute("aria-expanded", "false");
        showButton.focus({
            preventScroll: true
        });
    }
    showButton.addEventListener("click", openExtraBundles);
}
function secureExternalLinks() {
    const links = document.querySelectorAll('a[target="_blank"]');
    links.forEach((link) => {
        const relValues = new Set(
            (link.getAttribute("rel") || "")
                .split(/\s+/)
                .filter(Boolean)
        );
        relValues.add("noopener");
        relValues.add("noreferrer");
        relValues.add("external");
        link.setAttribute(
            "rel",
            Array.from(relValues).join(" ")
        );
    });
}
function updateCopyrightYear() {
    const yearElement = document.getElementById("current-year");
    if (!yearElement) {
        return;
    }
    const currentYear = new Date().getFullYear();
    yearElement.textContent = String(
        Math.max(2026, currentYear)
    );
}
function configureDarkBrowserTheme() {
    const themeColor = document.querySelector(
        'meta[name="theme-color"]'
    );
    const colorScheme = document.querySelector(
        'meta[name="color-scheme"]'
    );
    if (themeColor) {
        themeColor.setAttribute("content", "#050505");
    }
    if (colorScheme) {
        colorScheme.setAttribute("content", "dark");
    }
    document.documentElement.style.colorScheme = "dark";
}
function configureAccessGuide() {
    const launcher = document.getElementById("help-launcher");
    const dialog = document.getElementById(
        "access-guide-dialog"
    );
    const closeButton = document.getElementById(
        "access-dialog-close"
    );
    const doneButton = document.getElementById(
        "access-dialog-done"
    );
    if (
        !(launcher instanceof HTMLButtonElement) ||
        !(dialog instanceof HTMLDialogElement)
    ) {
        return;
    }
    let shouldRestoreLauncherFocus = false;
    function openGuide() {
        shouldRestoreLauncherFocus = true;
        if (typeof dialog.showModal === "function") {
            dialog.showModal();
        } else {
            dialog.setAttribute("open", "");
        }
        document.body.classList.add("dialog-is-open");
        if (closeButton instanceof HTMLButtonElement) {
            closeButton.focus();
        }
    }
    function closeGuide(options = {}) {
        const {
            scrollToBundles = false
        } = options;
        if (dialog.open && typeof dialog.close === "function") {
            dialog.close();
        } else {
            dialog.removeAttribute("open");
            document.body.classList.remove("dialog-is-open");
            if (shouldRestoreLauncherFocus) {
                launcher.focus();
            }
        }
        if (scrollToBundles) {
            const bundles = document.getElementById("bundles");
            if (bundles) {
                window.setTimeout(() => {
                    bundles.scrollIntoView({
                        behavior: window.matchMedia(
                            "(prefers-reduced-motion: reduce)"
                        ).matches
                            ? "auto"
                            : "smooth",
                        block: "start"
                    });
                }, 50);
            }
        }
    }
    launcher.addEventListener("click", openGuide);
    if (closeButton) {
        closeButton.addEventListener("click", () => {
            closeGuide();
        });
    }
    if (doneButton) {
        doneButton.addEventListener("click", () => {
            closeGuide({
                scrollToBundles: true
            });
        });
    }
    dialog.addEventListener("click", (event) => {
        if (event.target === dialog) {
            closeGuide();
        }
    });
    dialog.addEventListener("cancel", () => {
        document.body.classList.remove("dialog-is-open");
    });
    dialog.addEventListener("close", () => {
        document.body.classList.remove("dialog-is-open");
        if (shouldRestoreLauncherFocus) {
            launcher.focus({
                preventScroll: true
            });
        }
        shouldRestoreLauncherFocus = false;
    });
}
/*
 * Adsterra's publisher code is embedded directly in index.html so each slot
 * runs in the body beside its own placement markup. This watcher only manages
 * empty-slot presentation; it never injects, rewrites, or races ad scripts.
 */
const AD_SCRIPT_LOAD_TIMEOUT_MS = 30000;
const AD_SLOT_RENDER_GRACE_MS = 20000;
function configureAdSlots() {
    const slots = document.querySelectorAll("[data-ad-slot]");
    slots.forEach((slot) => {
        const frame = slot.querySelector(".ad-frame");
        if (!frame) {
            return;
        }
        let timer = 0;
        let noFillConfirmed = false;
        function hasRenderedAd() {
            const candidates = frame.querySelectorAll(
                "iframe, img, video, a"
            );
            return Array.prototype.some.call(candidates, (node) => {
                const bounds = node.getBoundingClientRect();
                return bounds.width >= 50 && bounds.height >= 30;
            });
        }
        function showSlot() {
            slot.classList.remove("is-pending");
            slot.classList.add("is-ready");
            slot.removeAttribute("inert");
            slot.removeAttribute("aria-hidden");
        }
        function hideSlot() {
            slot.classList.add("is-pending");
            slot.classList.remove("is-ready");
            slot.setAttribute("inert", "");
            slot.setAttribute("aria-hidden", "true");
        }
        function applyState() {
            timer = 0;
            if (hasRenderedAd()) {
                showSlot();
                return;
            }
            if (noFillConfirmed) {
                hideSlot();
            }
        }
        function scheduleCheck() {
            if (timer) {
                return;
            }
            timer = window.setTimeout(applyState, 120);
        }
        const adScripts = frame.querySelectorAll("script[data-adsterra]");
        let loadTimer = 0;
        adScripts.forEach((script) => {
            script.addEventListener("error", () => {
                console.warn(
                    "[ads] Adsterra script failed for slot '" +
                    slot.dataset.adSlot +
                    "'."
                );
                noFillConfirmed = true;
                scheduleCheck();
            }, {
                once: true
            });
            script.addEventListener("load", () => {
                window.clearTimeout(loadTimer);
                if (!hasRenderedAd()) {
                    window.setTimeout(() => {
                        noFillConfirmed = true;
                        scheduleCheck();
                    }, AD_SLOT_RENDER_GRACE_MS);
                }
            }, {
                once: true
            });
        });
        if (typeof MutationObserver === "function") {
            new MutationObserver(scheduleCheck).observe(frame, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: ["style", "class", "hidden", "width", "height"]
            });
        }
        if (typeof ResizeObserver === "function") {
            new ResizeObserver(scheduleCheck).observe(frame);
        }
        /* Catch code that rendered before this monitor was initialized. */
        scheduleCheck();
        /*
         * Some browser extensions block a script without a useful error event.
         * Keep the slot available for slow responses, then collapse it only if
         * no visible creative has appeared after the load timeout.
         */
        if (adScripts.length) {
            loadTimer = window.setTimeout(() => {
                if (!hasRenderedAd()) {
                    console.warn(
                        "[ads] No creative rendered for slot '" +
                        slot.dataset.adSlot +
                        "' within " + AD_SCRIPT_LOAD_TIMEOUT_MS + "ms."
                    );
                }
                noFillConfirmed = true;
                scheduleCheck();
            }, AD_SCRIPT_LOAD_TIMEOUT_MS);
        } else {
            window.setTimeout(() => {
                noFillConfirmed = true;
                scheduleCheck();
            }, AD_SLOT_RENDER_GRACE_MS);
        }
    });
}
let coreInitialized = false;
let remainingInitialized = false;
function initializeCore() {
    if (coreInitialized) {
        return;
    }
    coreInitialized = true;
    configureDarkBrowserTheme();
    configurePrimaryBundleLinks();
    createMoreLinksInterface();
    secureExternalLinks();
}
function initializeRemaining() {
    if (remainingInitialized) {
        return;
    }
    remainingInitialized = true;
    initializeCore();
    secureExternalLinks();
    updateCopyrightYear();
    configureAccessGuide();
    configureAdSlots();
}
function initializeApplication() {
    if (document.querySelector('[data-bundle="10"]')) {
        initializeCore();
    }
    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            initializeRemaining,
            {
                once: true
            }
        );
    } else {
        initializeRemaining();
    }
}
initializeApplication();
/* APP_SCRIPT_COMPLETE */
