/** @type {import('jest').Config} */
const nextJest = require("next/jest");
const createJestConfig = nextJest({ dir: __dirname });
const config = {
  testEnvironment: "jsdom",
  testMatch: ["**/__tests__/**/*.test.ts", "**/__tests__/**/*.test.tsx"],
  setupFilesAfterEnv: ["<rootDir>/__tests__/setup.ts"],
};
module.exports = createJestConfig(config);
