/** @type {import('jest').Config} */
const config = {
  testEnvironment: "jsdom",
  preset: "ts-jest",
  roots: ["<rootDir>"],
  testMatch: ["**/__tests__/**/*.test.ts", "**/__tests__/**/*.test.tsx"],
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/$1",
  },
  setupFilesAfterEnv: ["<rootDir>/__tests__/setup.ts"],
};
module.exports = config;
