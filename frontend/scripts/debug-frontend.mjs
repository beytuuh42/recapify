import { chromium } from '@playwright/test';

const appUrl = process.env.FRONTEND_DEBUG_URL || 'http://localhost:4200/';
const prompt = process.argv.slice(2).join(' ') || process.env.FRONTEND_DEBUG_PROMPT || '';
const timeoutMs = Number(process.env.FRONTEND_DEBUG_TIMEOUT_MS || (prompt ? 60000 : 10000));

const problems = [];
let summaryRevealCompleted = false;

function write(kind, payload) {
  console.log(JSON.stringify({
    timestamp: new Date().toISOString(),
    kind,
    ...payload,
  }));
}

function recordProblem(kind, payload) {
  problems.push({ kind, ...payload });
  write(kind, payload);
}

function isIgnoredConsoleError(text) {
  return /WebSocket connection to 'ws:\/\/localhost:\d+\/' failed: Connection closed before receiving a handshake response/.test(text);
}

async function consoleValues(message) {
  const values = [];

  for (const arg of message.args()) {
    try {
      values.push(await arg.jsonValue());
    } catch {
      values.push(await arg.toString());
    }
  }

  return values;
}

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();

page.on('console', async (message) => {
  const text = message.text();
  const payload = {
    level: message.type(),
    text,
    values: await consoleValues(message),
  };

  if (text.includes('Summary reveal completed')) {
    summaryRevealCompleted = true;
  }

  if (message.type() === 'error' && !isIgnoredConsoleError(text)) {
    recordProblem('browser-console-error', payload);
    return;
  }

  write('browser-console', payload);
});

page.on('pageerror', (error) => {
  recordProblem('browser-page-error', {
    message: error.message,
    stack: error.stack,
  });
});

page.on('requestfailed', (request) => {
  recordProblem('browser-request-failed', {
    method: request.method(),
    url: request.url(),
    failure: request.failure()?.errorText,
  });
});

page.on('response', (response) => {
  const status = response.status();

  if (status >= 400) {
    recordProblem('browser-http-error', {
      status,
      method: response.request().method(),
      url: response.url(),
    });
  }
});

try {
  write('debug-started', { appUrl, hasPrompt: Boolean(prompt), timeoutMs });

  await page.goto(appUrl, { waitUntil: 'domcontentloaded', timeout: timeoutMs });
  write('page-loaded', { url: page.url(), title: await page.title() });

  if (prompt) {
    await page.getByPlaceholder('Type a message...', { exact: true }).fill(prompt, { timeout: timeoutMs });
    await page.getByRole('button', { name: 'Send', exact: true }).click({ timeout: timeoutMs });
    write('prompt-submitted', { promptLength: prompt.length });

    const startedAt = Date.now();
    while (!summaryRevealCompleted && Date.now() - startedAt < timeoutMs) {
      await page.waitForTimeout(250);
    }

    if (!summaryRevealCompleted) {
      recordProblem('debug-timeout', {
        message: 'Timed out before summary reveal completed',
        timeoutMs,
      });
    }
  } else {
    await page.waitForTimeout(timeoutMs);
  }
} finally {
  await browser.close();
}

write('debug-completed', { problemCount: problems.length });

if (problems.length > 0) {
  process.exitCode = 1;
}
