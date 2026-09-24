import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/live",
  outputDir: "../tmp/live-results",
  timeout: 180_000,
  workers: 1,
  use: {
    channel: process.env.PLAYWRIGHT_CHANNEL, baseURL: "http://localhost:3000", viewport: { width: 1440, height: 1000 }, trace: "off" },
});
