import { ThemeProvider } from "../ThemeProvider";
import { ThemeToggle } from "../ThemeToggle";

export default function ThemeToggleExample() {
  return (
    <ThemeProvider>
      <div className="flex h-24 items-center justify-center gap-4">
        <span className="text-sm text-muted-foreground">Toggle theme:</span>
        <ThemeToggle />
      </div>
    </ThemeProvider>
  );
}
