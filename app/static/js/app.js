/**
 * MonsoonGuard — Frontend Interactivity
 *
 * Handles form submissions, API calls, dynamic result rendering,
 * mobile navigation, and scroll animations.
 */

"use strict";

/* ----------------------------------------------------------------- */
/*  DOM Ready                                                        */
/* ----------------------------------------------------------------- */
document.addEventListener("DOMContentLoaded", () => {
    initMobileMenu();
    initScrollAnimations();
    initPlanForm();
    initChecklistButton();
    initWeatherForm();
    initTravelForm();
    initDashboardForms();
});

/* ----------------------------------------------------------------- */
/*  Mobile Navigation                                                */
/* ----------------------------------------------------------------- */
function initMobileMenu() {
    const toggle = document.getElementById("menu-toggle");
    const menu = document.getElementById("mobile-menu");
    if (!toggle || !menu) return;

    toggle.addEventListener("click", () => {
        const isOpen = menu.classList.toggle("is-open");
        toggle.setAttribute("aria-expanded", String(isOpen));
        menu.setAttribute("aria-hidden", String(!isOpen));
    });

    // Close menu when a link is clicked
    menu.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => {
            menu.classList.remove("is-open");
            toggle.setAttribute("aria-expanded", "false");
            menu.setAttribute("aria-hidden", "true");
        });
    });
}

/* ----------------------------------------------------------------- */
/*  Scroll Animations (Intersection Observer)                        */
/* ----------------------------------------------------------------- */
function initScrollAnimations() {
    const elements = document.querySelectorAll(
        ".feature-card, .stats__card, .weather-check__card, .about__title"
    );

    if (!elements.length) return;

    elements.forEach((el) => el.classList.add("animate-on-scroll"));

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
    );

    elements.forEach((el) => observer.observe(el));
}

/* ----------------------------------------------------------------- */
/*  API Helper                                                       */
/* ----------------------------------------------------------------- */

/**
 * Make a fetch request and return parsed JSON.
 *
 * @param {string} url - The API endpoint URL.
 * @param {object} [options] - Fetch options (method, body, etc.).
 * @returns {Promise<object>} Parsed JSON response.
 */
async function apiCall(url, options = {}) {
    const defaults = {
        headers: { "Content-Type": "application/json" },
    };
    const config = { ...defaults, ...options };

    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || `Request failed (${response.status})`);
    }

    return data;
}

/**
 * Show a loading state on a button.
 *
 * @param {HTMLButtonElement} button - The button to modify.
 * @param {boolean} loading - Whether to show loading state.
 */
function setButtonLoading(button, loading) {
    if (loading) {
        button.dataset.originalText = button.textContent;
        button.textContent = "Loading...";
    } else {
        if (button.dataset.originalText) {
            button.textContent = button.dataset.originalText;
        }
    }
    button.disabled = loading;
    button.setAttribute("aria-busy", String(loading));
}

/* ----------------------------------------------------------------- */
/*  Plan Form (Landing Page)                                         */
/* ----------------------------------------------------------------- */
function initPlanForm() {
    const form = document.getElementById("plan-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const btn = document.getElementById("generate-plan-btn");

        const payload = {
            location: form.querySelector("#location").value.trim(),
            family_size: parseInt(form.querySelector("#family_size").value, 10),
            special_needs: form.querySelector("#special_needs").value.trim(),
            language: form.querySelector("#language").value,
        };

        setButtonLoading(btn, true);

        try {
            const result = await apiCall("/api/preparedness/plan", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            renderPlan(result.data);
        } catch (err) {
            renderError(err.message);
        } finally {
            setButtonLoading(btn, false);
        }
    });
}

/* ----------------------------------------------------------------- */
/*  Checklist Button                                                 */
/* ----------------------------------------------------------------- */
function initChecklistButton() {
    const btn = document.getElementById("generate-checklist-btn");
    const form = document.getElementById("plan-form");
    if (!btn || !form) return;

    btn.addEventListener("click", async () => {
        const payload = {
            location: form.querySelector("#location").value.trim(),
            family_size: parseInt(form.querySelector("#family_size").value, 10),
            special_needs: form.querySelector("#special_needs").value.trim(),
            language: form.querySelector("#language").value,
        };

        if (!payload.location) {
            renderError("Please enter a location first.");
            return;
        }

        btn.disabled = true;
        btn.textContent = "Generating...";

        try {
            const result = await apiCall("/api/preparedness/checklist", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            renderChecklist(result.data);
        } catch (err) {
            renderError(err.message);
        } finally {
            btn.disabled = false;
            btn.textContent = "Generate Emergency Checklist";
        }
    });
}

/* ----------------------------------------------------------------- */
/*  Weather Form (Landing Page)                                      */
/* ----------------------------------------------------------------- */
function initWeatherForm() {
    const form = document.getElementById("weather-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const location = form.querySelector("#weather-location").value.trim();
        if (!location) return;

        const resultDiv = document.getElementById("weather-result");

        try {
            const result = await apiCall(
                `/api/weather/advisory/${encodeURIComponent(location)}`
            );
            renderWeather(result.data, resultDiv);
        } catch (err) {
            resultDiv.innerHTML = `<div class="error-message" role="alert">${escapeHtml(err.message)}</div>`;
            resultDiv.hidden = false;
        }
    });
}

/* ----------------------------------------------------------------- */
/*  Travel Form (Landing Page)                                       */
/* ----------------------------------------------------------------- */
function initTravelForm() {
    const form = document.getElementById("travel-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const origin = form.querySelector("#travel-origin").value.trim();
        const dest = form.querySelector("#travel-destination").value.trim();
        if (!origin || !dest) return;

        const resultDiv = document.getElementById("travel-result");

        try {
            const result = await apiCall(
                `/api/weather/travel/${encodeURIComponent(origin)}/${encodeURIComponent(dest)}`
            );
            renderTravel(result.data, resultDiv);
        } catch (err) {
            resultDiv.innerHTML = `<div class="error-message" role="alert">${escapeHtml(err.message)}</div>`;
            resultDiv.hidden = false;
        }
    });
}

/* ----------------------------------------------------------------- */
/*  Dashboard Forms                                                  */
/* ----------------------------------------------------------------- */
function initDashboardForms() {
    // Dashboard Plan Form
    const planForm = document.getElementById("dash-plan-form");
    if (planForm) {
        planForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                location: planForm.querySelector("#dash-location").value.trim(),
                family_size: parseInt(planForm.querySelector("#dash-family-size").value, 10),
                special_needs: planForm.querySelector("#dash-needs").value.trim(),
                language: planForm.querySelector("#dash-language").value,
            };

            const resultDiv = document.getElementById("dash-plan-result");
            try {
                const result = await apiCall("/api/preparedness/plan", {
                    method: "POST",
                    body: JSON.stringify(payload),
                });
                resultDiv.innerHTML = buildPlanHTML(result.data);
                resultDiv.hidden = false;
            } catch (err) {
                resultDiv.innerHTML = `<div class="error-message" role="alert">${escapeHtml(err.message)}</div>`;
                resultDiv.hidden = false;
            }
        });
    }

    // Dashboard Weather Form
    const weatherForm = document.getElementById("dash-weather-form");
    if (weatherForm) {
        weatherForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const city = weatherForm.querySelector("#dash-weather-city").value.trim();
            const resultDiv = document.getElementById("dash-weather-result");

            try {
                const result = await apiCall(`/api/weather/advisory/${encodeURIComponent(city)}`);
                renderWeather(result.data, resultDiv);
            } catch (err) {
                resultDiv.innerHTML = `<div class="error-message" role="alert">${escapeHtml(err.message)}</div>`;
                resultDiv.hidden = false;
            }
        });
    }

    // Dashboard Travel Form
    const travelForm = document.getElementById("dash-travel-form");
    if (travelForm) {
        travelForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const from = travelForm.querySelector("#dash-travel-from").value.trim();
            const to = travelForm.querySelector("#dash-travel-to").value.trim();
            const resultDiv = document.getElementById("dash-travel-result");

            try {
                const result = await apiCall(`/api/weather/travel/${encodeURIComponent(from)}/${encodeURIComponent(to)}`);
                renderTravel(result.data, resultDiv);
            } catch (err) {
                resultDiv.innerHTML = `<div class="error-message" role="alert">${escapeHtml(err.message)}</div>`;
                resultDiv.hidden = false;
            }
        });
    }
}

/* ----------------------------------------------------------------- */
/*  Render Functions                                                 */
/* ----------------------------------------------------------------- */

/**
 * Render a preparedness plan in the demo results panel.
 * @param {object} data - Plan data from the API.
 */
function renderPlan(data) {
    const container = document.getElementById("result-content");
    const placeholder = document.getElementById("results-placeholder");
    if (!container) return;

    container.innerHTML = buildPlanHTML(data);
    container.hidden = false;
    if (placeholder) placeholder.hidden = true;
}

/**
 * Build HTML string for a preparedness plan.
 * @param {object} data - Plan data.
 * @returns {string} HTML string.
 */
function buildPlanHTML(data) {
    let html = `<h2>${escapeHtml(data.title || "Preparedness Plan")}</h2>`;
    html += `<p><strong>Risk Level:</strong> ${escapeHtml((data.risk_level || "moderate").toUpperCase())}</p>`;

    if (data.sections) {
        data.sections.forEach((section) => {
            html += `<h3>${escapeHtml(section.heading)}</h3><ul>`;
            section.items.forEach((item) => {
                html += `<li>${escapeHtml(item)}</li>`;
            });
            html += `</ul>`;
        });
    }

    if (data.emergency_contacts) {
        html += `<h3>Emergency Contacts</h3><ul>`;
        data.emergency_contacts.forEach((contact) => {
            html += `<li>${escapeHtml(contact)}</li>`;
        });
        html += `</ul>`;
    }

    return html;
}

/**
 * Render a checklist in the demo results panel.
 * @param {object} data - Checklist data from the API.
 */
function renderChecklist(data) {
    const container = document.getElementById("result-content");
    const placeholder = document.getElementById("results-placeholder");
    if (!container) return;

    let html = `<h2>${escapeHtml(data.title || "Emergency Checklist")}</h2>`;

    if (data.categories) {
        data.categories.forEach((category) => {
            html += `<h3>${escapeHtml(category.name)}</h3><ul>`;
            category.items.forEach((item) => {
                html += `<li>[${item.priority.toUpperCase()}] ${escapeHtml(item.task)}</li>`;
            });
            html += `</ul>`;
        });
    }

    container.innerHTML = html;
    container.hidden = false;
    if (placeholder) placeholder.hidden = true;
}

/**
 * Render weather data in a target container.
 * @param {object} data - Weather data from the API.
 * @param {HTMLElement} container - Target DOM element.
 */
function renderWeather(data, container) {
    let html = `<h3>${escapeHtml(data.condition || "N/A")} — ${escapeHtml((data.risk_level || "moderate").toUpperCase())}</h3>`;
    html += `<ul>
                <li><strong>Temperature:</strong> ${data.temperature_c || "N/A"}°C</li>
                <li><strong>Humidity:</strong> ${data.humidity_percent || "N/A"}%</li>
                <li><strong>Wind Speed:</strong> ${data.wind_speed_kmh || "N/A"} km/h</li>
                <li><strong>Rainfall:</strong> ${data.rainfall_mm || "N/A"} mm</li>
             </ul>`;
    html += `<p><strong>24h Forecast:</strong> ${escapeHtml(data.forecast_next_24h || "No forecast available.")}</p>`;

    container.innerHTML = html;
    container.hidden = false;
}

/**
 * Render travel advisory data in a target container.
 * @param {object} data - Travel advisory data from the API.
 * @param {HTMLElement} container - Target DOM element.
 */
function renderTravel(data, container) {
    let html = `<h3>${escapeHtml(data.advisory_level || "Unknown")}</h3>`;
    html += `<p><strong>Risk Score:</strong> ${data.combined_risk_score || "N/A"} / 1.00</p>`;

    if (data.precautions && data.precautions.length) {
        html += `<h4>Precautions:</h4><ul>`;
        data.precautions.forEach((p) => {
            html += `<li>${escapeHtml(p)}</li>`;
        });
        html += `</ul>`;
    }

    container.innerHTML = html;
    container.hidden = false;
}

/**
 * Render an error message in the demo results panel.
 * @param {string} message - Error message to display.
 */
function renderError(message) {
    const container = document.getElementById("result-content");
    const placeholder = document.getElementById("results-placeholder");

    if (container) {
        container.innerHTML = `<p style="color: #ffaa00">⚠️ ${escapeHtml(message)}</p>`;
        container.hidden = false;
    }
    if (placeholder) placeholder.hidden = true;
}

/* ----------------------------------------------------------------- */
/*  Security: HTML Escaping                                          */
/* ----------------------------------------------------------------- */

/**
 * Escape HTML special characters to prevent XSS.
 * @param {string} str - Raw string.
 * @returns {string} Escaped string safe for innerHTML.
 */
function escapeHtml(str) {
    if (typeof str !== "string") return String(str);
    const map = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
    };
    return str.replace(/[&<>"']/g, (char) => map[char]);
}
