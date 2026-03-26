import { describe, it, expect, beforeAll, afterAll, afterEach } from "vitest";
import { renderHook, waitFor, act } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import { useApi } from "../../src/hooks/useApi";
import { useMode } from "../../src/hooks/useMode";

const server = setupServer(
  http.get("/api/v1/mode/", () => HttpResponse.json({ mode: "demo" })),
  http.put("/api/v1/mode/", async ({ request }) => {
    const body = (await request.json()) as { mode: string };
    return HttpResponse.json({ mode: body.mode });
  }),
);

beforeAll(() => server.listen({ onUnhandledRequest: "bypass" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe("useApi", () => {
  it("fetches data and sets loading state", async () => {
    const fetcher = () => Promise.resolve({ value: 42 });
    const { result } = renderHook(() => useApi(fetcher, []));

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual({ value: 42 });
    expect(result.current.error).toBeNull();
  });

  it("handles errors", async () => {
    const fetcher = () => Promise.reject(new Error("fail"));
    const { result } = renderHook(() => useApi(fetcher, []));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error?.message).toBe("fail");
    expect(result.current.data).toBeNull();
  });
});

describe("useMode", () => {
  it("returns current mode from API", async () => {
    const { result } = renderHook(() => useMode());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.mode).toBe("demo");
  });

  it("allows switching mode", async () => {
    const { result } = renderHook(() => useMode());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    await act(async () => {
      await result.current.setMode("live");
    });

    expect(result.current.mode).toBe("live");
  });
});
