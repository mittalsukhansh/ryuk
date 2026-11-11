/* Real Next -> FastAPI -> services -> SQLite -> mocked provider. No live payment. */
import { chromium } from "playwright";
import assert from "node:assert/strict";
import { mkdirSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
const base = process.env.RYUK_E2E_URL || "http://localhost:3100";
const backend = process.env.RYUK_E2E_BACKEND || "http://127.0.0.1:8100";
const shots = process.env.RYUK_SCREENSHOT_DIR || join(tmpdir(), "ryuk-browser");
const SDK = `window.__sdkEarlyClose=0;window.__sdkPending=0;window.paypal={Buttons(options){let host,inCallback=false;return{async render(element){host=element;const b=document.createElement('button');b.textContent='PayPal Sandbox · test buyer';b.style.cssText='width:100%;padding:14px;background:#eee;color:#111;border:0';b.onclick=async()=>{inCallback=true;window.__sdkPending++;try{const id=await options.createOrder();const action=await window.approveFixtureOrder(id);if(action==='cancel')await options.onCancel();else await options.onApprove();}catch(e){options.onError(e)}finally{inCallback=false;window.__sdkPending--}};host.appendChild(b)},async close(){if(inCallback)window.__sdkEarlyClose++;if(host)host.replaceChildren()}}}};`;
(async () => {
  const browser = await chromium.launch({
    ...(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {}),
    headless: true,
    args: ["--no-sandbox"],
  });
  let assertions = 0;
  try {
    const context = await browser.newContext({
      viewport: { width: 1440, height: 1000 },
    });
    await context.route("**/*", (route) => {
      const url = route.request().url();
      if (url.startsWith(base + "/") || url.startsWith(backend + "/"))
        return route.continue();
      // PayPal SDK is fulfilled by the page-specific mock below; deny all other external traffic.
      return route.abort();
    });
    const page = await context.newPage();
    page.setDefaultTimeout(15000);
    const failures = [];
    page.on("pageerror", (e) => failures.push(e.message));
    let mode = "success";
    await page.exposeFunction("approveFixtureOrder", async (id) => {
      if (mode === "cancel") return "cancel";
      if (mode === "spoof_callback") return "spoof";
      const response = await context.request.post(
        `${backend}/__test__/approve/${id}?mode=${mode}`,
      );
      assert(response.ok());
      return "approve";
    });
    await page.route("https://www.paypal.com/sdk/js*", (route) =>
      route.fulfill({ contentType: "application/javascript", body: SDK }),
    );
    async function reset() {
      mode = "success";
      const response = await context.request.post(`${backend}/__test__/new-case`);
      assert(response.ok());
      await context.clearCookies();
      await page.goto(base, { waitUntil: "networkidle" });
      await page.getByRole("button", { name: /UNLOCK WORKSPACE/ }).click();
      await page
        .getByLabel("Workspace password")
        .fill("synthetic-browser-password");
      await page.getByRole("button", { name: /^UNLOCK WORKSPACE/ }).click();
      await page.locator("dialog[open]").waitFor({ state: "hidden" });
    }
    async function investigate() {
      await page.getByRole("button", { name: /OPEN INVESTIGATION/ }).click();
      await page.locator(".candidate").first().waitFor();
      assert.equal(await page.locator(".candidate").count(), 3);
    }
    async function approveSelected() {
      await page.getByRole("button", { name: /REVIEW EXACT TERMS/ }).click();
      assert.match(await page.locator(".intent-review").textContent(), /ORIGINAL INSTRUCTION/);
      assert.match(await page.locator(".intent-review").textContent(), /Free Cancellation: true/);
      assertions += 2;
      await page.getByRole("button", { name: /APPROVE EXACT TERMS/ }).click();
      await page.locator(".approval-modal[open]").waitFor({ state: "hidden" });
    }
    await reset();
    mkdirSync(shots, { recursive: true });
    await page.screenshot({
      path: `${shots}/ryuk-command-desktop.png`,
      fullPage: true,
    });
    await investigate();
    assert.match(
      await page.locator(".parsed-intent").textContent(),
      /Mountain View/,
    );
    assertions++;
    assert.equal(await page.locator(".candidate-top .pass").count(), 0);
    assert.equal(await page.locator(".candidate-top .review").count(), 2);
    assertions++;
    // Backend DENY never mounts a PayPal button.
    await page.locator(".candidate").nth(2).getByRole("button").click();
    await page.getByText("CHECKOUT LOCKED", { exact: true }).waitFor();
    assert.equal(await page.locator(".paypal-slot").count(), 0);
    assertions++;
    await page.locator(".candidate").nth(1).getByRole("button").click();
    await page.getByRole("button", { name: /REVIEW EXACT TERMS/ }).click();
    await page.locator(".approval-modal[open]").waitFor();
    assert.match(
      await page.locator(".approval-modal").textContent(),
      /1,390.00/,
    );
    assertions++;
    await page.getByRole("button", { name: "REJECT", exact: true }).click();
    await page.getByText("CHECKOUT LOCKED", { exact: true }).waitFor();
    assert.equal(await page.locator(".paypal-slot").count(), 0);
    assertions++;
    // A real backend capture response must arrive before confirmation is rendered.
    await reset();
    await investigate();
    await page.locator(".candidate").first().getByRole("button").click();
    await page.getByRole("heading", { name: "Trust the trace." }).waitFor();
    assert.equal(await page.locator(".paypal-slot").count(), 0);
    assertions++;
    await approveSelected();
    await page.screenshot({
      path: `${shots}/ryuk-evidence-desktop.png`,
      fullPage: true,
    });
    let release, reached;
    const gate = new Promise((resolve) => (release = resolve));
    const seen = new Promise((resolve) => (reached = resolve));
    await page.route("**/api/ryuk/checkouts/*/capture", async (route) => {
      assert.equal(route.request().postData(), "{}");
      reached();
      await gate;
      await route.continue();
    });
    await page
      .getByRole("button", { name: "PayPal Sandbox · test buyer" })
      .click();
    await seen;
    assert.equal(
      await page.getByRole("heading", { name: "Payment confirmed." }).count(),
      0,
    );
    assertions++;
    release();
    await page.getByRole("heading", { name: "Payment confirmed." }).waitFor();
    await page.locator(".payment-result").getByText("$320.00", { exact: true }).waitFor();
    assert.match(await page.locator(".payment-result").textContent(), /320.00/);
    assertions++;
    await page.locator(".audit-log").getByText("BUDGET_SETTLED", { exact: true }).waitFor();
    assert.match(
      await page.locator(".audit-log").textContent(),
      /BUDGET_SETTLED/,
    );
    assertions++;
    await page.waitForFunction(() => window.__sdkPending === 0);
    assert.equal(await page.evaluate(() => window.__sdkEarlyClose), 0, "SDK must stay mounted until onApprove resolves");
    assertions++;
    await page.screenshot({
      path: `${shots}/ryuk-result-desktop.png`,
      fullPage: true,
    });
    await page.unroute("**/api/ryuk/checkouts/*/capture");
    // Escalation uses backend consent and then the same actual checkout coordinator.
    await reset();
    await investigate();
    await page.locator(".candidate").nth(1).getByRole("button").click();
    await approveSelected();
    await page
      .getByRole("button", { name: "PayPal Sandbox · test buyer" })
      .click();
    await page.getByRole("heading", { name: "Payment confirmed." }).waitFor();
    assert.match(
      await page.locator(".audit-log").textContent(),
      /APPROVAL_GRANTED/,
    );
    assertions++;
    // Callback + timeout never means paid. Reconcile via GET-backed backend action.
    await reset();
    await investigate();
    await page.locator(".candidate").first().getByRole("button").click();
    await approveSelected();
    mode = "timeout_after_capture";
    await page
      .getByRole("button", { name: "PayPal Sandbox · test buyer" })
      .click();
    await page
      .getByRole("heading", { name: "Confirmation pending." })
      .waitFor();
    assert.equal(
      await page.getByRole("heading", { name: "Payment confirmed." }).count(),
      0,
    );
    assertions++;
    await page.waitForFunction(() => window.__sdkPending === 0);
    assert.equal(await page.evaluate(() => window.__sdkEarlyClose), 0, "SDK must stay mounted until pending capture resolves");
    assertions++;
    // Real proxy boundaries: no arbitrary routes, cross-origin actions, or credential reflection.
    const blocked = await context.request.post(`${base}/api/ryuk/__test__/new-case`);
    assert.equal(blocked.status(), 404);
    assertions++;
    const csrf = await context.request.post(`${base}/api/ryuk/session`, {
      headers: { Origin: "https://evil.test" }, data: { password: "synthetic-sensitive-marker" },
    });
    assert.equal(csrf.status(), 403);
    assertions++;
    const invalid = await context.request.post(`${base}/api/ryuk/session`, {
      headers: { Origin: base },
      data: { password: "wrong", client_secret: "synthetic-sensitive-marker" },
    });
    assert.equal(invalid.status(), 422);
    assert(!((await invalid.text()).includes("synthetic-sensitive-marker")));
    assertions += 2;
    const redirected = await context.request.get(`${base}/api/ryuk/session`, {
      headers: { Cookie: "synthetic_proxy_mode=redirect" },
    });
    assert.equal(redirected.status(), 502);
    const redirectVisits = await context.request.get(`${backend}/__test__/redirect-visits`);
    assert.equal((await redirectVisits.json()).visits, 0);
    assertions += 2;
    const wrongMethod = await context.request.delete(`${base}/api/ryuk/checkouts/unknown`, {
      headers: { Origin: base },
    });
    assert.equal(wrongMethod.status(), 405);
    assertions++;
    await page.getByRole("button", { name: /CHECK BACKEND STATUS/ }).click();
    await page.getByRole("heading", { name: "Payment confirmed." }).waitFor();
    assertions++;
    // A spoofed SDK callback without provider buyer approval must not capture or display paid.
    await reset();
    await investigate();
    await page.locator(".candidate").first().getByRole("button").click();
    await approveSelected();
    mode = "spoof_callback";
    await page.getByRole("button", { name: "PayPal Sandbox · test buyer" }).click();
    await page.locator(".message.error").waitFor();
    assert.equal(await page.getByRole("heading", { name: "Payment confirmed." }).count(), 0);
    assert.match(await page.locator(".payment-result").textContent(), /AWAITING_PAYPAL_BUYER/);
    assertions += 2;
    // Buyer cancellation is local failure, not provider-paid success or a retry.
    await reset();
    await investigate();
    await page.locator(".candidate").first().getByRole("button").click();
    await approveSelected();
    mode = "cancel";
    await page.getByRole("button", { name: "PayPal Sandbox · test buyer" }).click();
    await page.getByRole("heading", { name: "Payment not completed." }).waitFor();
    assert.equal(await page.getByRole("heading", { name: "Payment confirmed." }).count(), 0);
    assertions++;
    await page.waitForFunction(() => window.__sdkPending === 0);
    assert.equal(await page.evaluate(() => window.__sdkEarlyClose), 0, "SDK must stay mounted until buyer cancellation resolves");
    assertions++;
    // Phone fallback and keyboard/dialog usability, no horizontal document overflow.
    await page.setViewportSize({ width: 390, height: 844 });
    await page.screenshot({
      path: `${shots}/ryuk-result-mobile.png`,
      fullPage: true,
    });
    const sizes = await page.evaluate(() => ({
      client: innerWidth,
      scroll: document.documentElement.scrollWidth,
    }));
    assert(sizes.scroll <= sizes.client, JSON.stringify(sizes));
    assertions++;
    const headers = await (await context.request.get(base)).headers();
    assert.equal(headers["x-frame-options"], "DENY"); assertions++;
    assert.match(headers["content-security-policy"], /frame-ancestors 'none'/); assertions++;
    assert.equal(headers["x-content-type-options"], "nosniff"); assertions++;
    assert.equal(await page.evaluate(() => document.cookie.includes("ryuk_session")), false); assertions++;
    const badOrigin = await context.request.post(`${base}/api/ryuk/requests`, {
      headers: { Origin: "https://evil.test" }, data: { query: "untrusted" },
    });
    assert.equal(badOrigin.status(), 403); assertions++;
    const large = await context.request.post(`${base}/api/ryuk/requests`, {
      headers: { Origin: base }, data: "x".repeat(70000),
    });
    assert.equal(large.status(), 413); assertions++;
    assert.equal((await context.request.get(`${base}/api/ryuk/not-allowlisted`)).status(), 404); assertions++;
    const anonymous = await browser.newContext();
    assert.equal((await anonymous.request.post(`${backend}/v1/agent/parse`, {
      headers: { Origin: base }, data: { query: "private model request" },
    })).status(), 401); assertions++;
    await anonymous.close();
    await reset();
    await investigate();
    await page.locator(".candidate").first().getByRole("button").click();
    await page.getByRole("button", { name: /REVIEW EXACT TERMS/ }).click();
    await page.locator(".approval-modal[open]").waitFor();
    const reviewFits = await page.locator(".approval-modal").evaluate(
      (dialog) => dialog.scrollWidth <= dialog.clientWidth,
    );
    assert(reviewFits);
    assertions++;
    await page.screenshot({ path: `${shots}/ryuk-intent-review-mobile.png`, fullPage: true });
    await page.getByRole("button", { name: "REJECT", exact: true }).click();
    await page.getByText("CHECKOUT LOCKED", { exact: true }).waitFor();
    assert.equal(await page.locator(".paypal-slot").count(), 0);
    assertions++;
    assert.equal(failures.length, 0, failures.join("\n"));
    assertions++;
    console.log(
      `PASS: ${assertions} browser assertions; real UI/BFF/backend flow, mocked SDK/provider, desktop/mobile. No live Sandbox acceptance claimed.`,
    );
    await context.close();
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
