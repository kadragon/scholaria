import { useTheme } from "../hooks/useTheme";
import { Button } from "./ui/button";

export const ThemeToggle = () => {
  const { theme, setTheme } = useTheme();

  const handleToggle = () => {
    const cycle: Record<typeof theme, typeof theme> = {
      light: "dark",
      dark: "system",
      system: "light",
    };
    setTheme(cycle[theme]);
  };

  const getIcon = () => {
    const icons: Record<typeof theme, string> = {
      light: "☀️",
      dark: "🌙",
      system: "🖥️",
    };
    return icons[theme];
  };

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={handleToggle}
      aria-label="테마 전환"
    >
      {getIcon()}
    </Button>
  );
};
