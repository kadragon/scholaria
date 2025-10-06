import { useNavigate } from "react-router-dom";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  FileText,
  MessageSquare,
  BookOpen,
  BarChart3,
  Plus,
} from "lucide-react";

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const CommandPalette = ({ open, onOpenChange }: CommandPaletteProps) => {
  const navigate = useNavigate();

  const runCommand = (command: () => void) => {
    onOpenChange(false);
    command();
  };

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <CommandInput placeholder="명령어 또는 페이지 검색..." />
      <CommandList>
        <CommandEmpty>검색 결과가 없습니다.</CommandEmpty>
        <CommandGroup heading="탐색">
          <CommandItem
            onSelect={() => runCommand(() => navigate("/admin/topics"))}
          >
            <BookOpen className="mr-2 h-4 w-4" />
            <span>토픽 관리</span>
          </CommandItem>
          <CommandItem
            onSelect={() => runCommand(() => navigate("/admin/contexts"))}
          >
            <FileText className="mr-2 h-4 w-4" />
            <span>컨텍스트 관리</span>
          </CommandItem>
          <CommandItem
            onSelect={() => runCommand(() => navigate("/admin/analytics"))}
          >
            <BarChart3 className="mr-2 h-4 w-4" />
            <span>분석 대시보드</span>
          </CommandItem>
          <CommandItem onSelect={() => runCommand(() => navigate("/chat"))}>
            <MessageSquare className="mr-2 h-4 w-4" />
            <span>채팅</span>
          </CommandItem>
        </CommandGroup>
        <CommandGroup heading="작업">
          <CommandItem
            onSelect={() => runCommand(() => navigate("/admin/topics/create"))}
          >
            <Plus className="mr-2 h-4 w-4" />
            <span>토픽 생성</span>
          </CommandItem>
          <CommandItem
            onSelect={() =>
              runCommand(() => navigate("/admin/contexts/create"))
            }
          >
            <Plus className="mr-2 h-4 w-4" />
            <span>컨텍스트 생성</span>
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
};
