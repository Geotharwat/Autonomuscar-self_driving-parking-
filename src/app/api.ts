type Action = "stop" | "drive" | "park" | "control";

export async function invokeAction(action: Action, ...args: any[]) {
  const response = await fetch(`/api/action`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      action,
      args: args?.length > 0 ? args : undefined,
    }),
  });
  return response.text();
}

export async function invokeActionSignaled(
  signal: AbortSignal,
  action: Action,
  ...args: any[]
) {
  const response = await fetch(`/api/action`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    signal,
    body: JSON.stringify({
      action,
      args: args?.length > 0 ? args : undefined,
    }),
  });
  return response.text();
}
