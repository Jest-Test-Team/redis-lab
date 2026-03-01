import { getGatewayWsUrl, getGatewayApiUrl } from "@/lib/gateway-url";

const originalEnv = process.env;
const originalWindow = typeof globalThis !== "undefined" ? (globalThis as any).window : undefined;

describe("getGatewayWsUrl", () => {
  afterEach(() => {
    process.env = { ...originalEnv };
    (globalThis as any).window = originalWindow;
  });

  it("returns NEXT_PUBLIC_GATEWAY_WS when set", () => {
    process.env.NEXT_PUBLIC_GATEWAY_WS = "wss://tunnel.example.com/ws";
    expect(getGatewayWsUrl()).toBe("wss://tunnel.example.com/ws");
  });

  it("returns ws://localhost:8080/ws when hostname is localhost", () => {
    delete process.env.NEXT_PUBLIC_GATEWAY_WS;
    (globalThis as any).window = {
      location: { hostname: "localhost", protocol: "http:", host: "localhost:3000" },
    };
    expect(getGatewayWsUrl()).toBe("ws://localhost:8080/ws");
  });

  it("returns same-origin /ws when not localhost", () => {
    delete process.env.NEXT_PUBLIC_GATEWAY_WS;
    (globalThis as any).window = {
      location: { hostname: "vercel.app", protocol: "https:", host: "mirage.vercel.app" },
    };
    expect(getGatewayWsUrl()).toBe("wss://mirage.vercel.app/ws");
  });
});

describe("getGatewayApiUrl", () => {
  afterEach(() => {
    process.env = { ...originalEnv };
    (globalThis as any).window = originalWindow;
  });

  it("returns NEXT_PUBLIC_GATEWAY_API when set", () => {
    process.env.NEXT_PUBLIC_GATEWAY_API = "https://tunnel.example.com";
    expect(getGatewayApiUrl()).toBe("https://tunnel.example.com");
  });

  it("returns http://localhost:8080 when hostname is localhost", () => {
    delete process.env.NEXT_PUBLIC_GATEWAY_API;
    (globalThis as any).window = {
      location: { hostname: "localhost", origin: "http://localhost:3000" },
    };
    expect(getGatewayApiUrl()).toBe("http://localhost:8080");
  });

  it("returns window.origin when not localhost", () => {
    delete process.env.NEXT_PUBLIC_GATEWAY_API;
    (globalThis as any).window = {
      location: { hostname: "vercel.app", origin: "https://mirage.vercel.app" },
    };
    expect(getGatewayApiUrl()).toBe("https://mirage.vercel.app");
  });
});
