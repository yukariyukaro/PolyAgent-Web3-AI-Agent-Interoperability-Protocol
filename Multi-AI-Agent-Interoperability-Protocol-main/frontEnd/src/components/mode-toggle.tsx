import { useTheme } from "./theme-provider";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";

export function ModeToggle() {
  const { setTheme } = useTheme();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="inline-flex items-center justify-center rounded-md border border-input h-10 w-10 p-0 hover:bg-accent hover:text-accent-foreground">
        {/* 太阳图标 */}
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" 
          viewBox="0 0 24 24"
        >
          <path 
            fill="none" 
            stroke="currentColor" 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth="2" 
            d="M12 16a4 4 0 1 0 0-8a4 4 0 0 0 0 8ZM12 3v1m0 16v1m-8-9H3m16-1h2M5.6 5.6l.7.7m12.1-.7l-.7.7m0 11.4l.7.7m-12.1-.7l-.7.7" 
          />
        </svg>
        
        {/* 月亮图标 */}
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" 
          viewBox="0 0 24 24"
        >
          <path 
            fill="none" 
            stroke="currentColor" 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth="2" 
            d="M12 3a6 6 0 0 0 9 9a9 9 0 1 1-9-9Z" 
          />
        </svg>
        
        <span className="sr-only">切换主题</span>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme("light")}>
          浅色
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")}>
          深色
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("system")}>
          系统
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
} 