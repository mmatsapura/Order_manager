import type { ReactNode } from "react";
import { QueryProvider } from "@/providers/QueryProvider";

export function AppProviders({ children }: { children: ReactNode }) {
  return <QueryProvider>{children}</QueryProvider>;
}
// Set global client on the top of app to access it from anywhere