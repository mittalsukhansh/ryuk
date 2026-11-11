/* Real Next -> FastAPI -> services -> SQLite -> mocked provider. No live payment. */
import { chromium } from "playwright";
import assert from "node:assert/strict";
import { mkdirSync } from "node:fs";
const base = process.env.RYUK_E2E_URL || "http://localhost:3100";
const backend = process.env.RYUK_E2E_BACKEND || "http://127.0.0.1:8100";
const shots = process.env.RYUK_SCREENSHOT_DIR || "/tmp/ryuk-browser";
const SDK = `window.paypal={Buttons(options){let host;return{async render(element){host=element;const b=document.createElement('button');b.textContent='PayPal Sandbox · test buyer';b.style.cssText='width:100%;padding:14px;background:#eee;color:#111;border:0';b.onclick=async()=>{try{const id=await options.createOrder();await window.approveFixtureOrder(id);await options.onApprove();}catch(e){options.onError(e)}};host.appendChild(b)},async close(){if(host)host.replaceChildren()}}}};`;
(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH || "/usr/bin/chromium",
    headless: true,
    args: ["--no-sandbox"],
  });
  let assertions = 0;
  try {
    const context = await browser.newContext({
      viewport: { width: 1440, height: 1000 },
    });
    const page = await context.newPage();
    page.setDefaultTimeout(15000);
    const failures = [];
    page.on("pageerror", (e) => failures.push(e.message));
    let mode = "success";
    await page.exposeFunction("approveFixtureOrder", async (id) => {
      const response = await context.request.post(
        `${backend}/__test__/approve/${id}?mode=${mode}`,
      );
      assert(response.ok());
    });
    await page.route("https://www.paypal.com/sdk/js*", (route) =>
      route.fulfill({ contentType: "application/javascript", body: SDK }),
    );
    async function reset() {
      const response = await context.request.post(`${backend}/__test__/reset`);
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
      await page.locator(".approval-modal[open]").waitFor();
      assert.match(await page.locator(".approval-modal").textContent(), /Original request/);
      assertions++;
      await page.getByRole("button", { name: /APPROVE EXACT TERMS/ }).click();
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
    assert.match(await page.locator(".payment-result").textContent(), /320.00/);
    assertions++;
    assert.match(
      await page.locator(".audit-log").textContent(),
      /BUDGET_SETTLED/,
    );
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
    await page.getByRole("button", { name: /REVIEW EXACT TERMS/ }).click();
    await page.getByRole("button", { name: /APPROVE EXACT TERMS/ }).click();
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
    await page.getByRole("button", { name: /CHECK BACKEND STATUS/ }).click();
    await page.getByRole("heading", { name: "Payment confirmed." }).waitFor();
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
