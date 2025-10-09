import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Cross2Icon } from "@radix-ui/react-icons";

interface DataTableToolbarProps {
  searchValue: string;
  onSearchChange: (value: string) => void;
  filters?: React.ReactNode;
  isFiltered: boolean;
  onReset: () => void;
  searchPlaceholder?: string;
}

export function DataTableToolbar({
  searchValue,
  onSearchChange,
  filters,
  isFiltered,
  onReset,
  searchPlaceholder = "검색...",
}: DataTableToolbarProps) {
  return (
    <div className="flex items-center justify-between gap-2 py-4">
      <div className="flex flex-1 items-center gap-2">
        <Input
          placeholder={searchPlaceholder}
          value={searchValue}
          onChange={(e) => onSearchChange(e.target.value)}
          className="h-8 w-[200px] lg:w-[300px]"
        />
        {filters}
      </div>
      {isFiltered && (
        <Button variant="ghost" onClick={onReset} className="h-8 px-2 lg:px-3">
          초기화
          <Cross2Icon className="ml-2 h-4 w-4" />
        </Button>
      )}
    </div>
  );
}
