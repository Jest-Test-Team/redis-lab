import { renderHook, act, waitFor } from "@testing-library/react";
import { useWs } from "@/hooks/useWs";
import { LocaleProvider } from "@/contexts/LocaleContext";

function wrapper({ children }: { children: React.ReactNode }) {
  return <LocaleProvider>{children}</LocaleProvider>;
}

describe("useWs", () => {
  let mockWs: { onopen: () => void; onmessage: (e: { data: string }) => void; onclose: () => void; close: () => void };
  let MockWS: jest.Mock;

  beforeEach(() => {
    mockWs = {
      onopen: () => {},
      onmessage: () => {},
      onclose: () => {},
      close: jest.fn(),
    };
    MockWS = jest.fn().mockImplementation(() => mockWs);
    (global as any).WebSocket = MockWS;
  });

  afterEach(() => {
    (global as any).WebSocket = undefined;
  });

  it("sets connected to true when WebSocket opens", async () => {
    const { result } = renderHook(() => useWs("ws://test/ws"), { wrapper });

    expect(result.current.connected).toBe(false);

    act(() => {
      mockWs.onopen();
    });

    await waitFor(() => {
      expect(result.current.connected).toBe(true);
    });
  });

  it("updates lastEvent and virtualId on identity_refreshed message", async () => {
    const { result } = renderHook(() => useWs("ws://test/ws"), { wrapper });

    act(() => {
      mockWs.onopen();
    });

    act(() => {
      mockWs.onmessage({
        data: JSON.stringify({
          type: "identity_refreshed",
          payload: { virtualId: "vid_abc123", expiresAtMs: 12345 },
          ts: 1,
        }),
      });
    });

    await waitFor(() => {
      expect(result.current.lastEvent?.type).toBe("identity_refreshed");
      expect(result.current.virtualId).toBe("vid_abc123");
    });
  });

  it("does nothing when url is empty", () => {
    const { result } = renderHook(() => useWs(""), { wrapper });
    expect(MockWS).not.toHaveBeenCalled();
    expect(result.current.connected).toBe(false);
  });
});
