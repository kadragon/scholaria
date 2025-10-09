import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Checkbox } from "@/components/ui/checkbox";

interface FacetedFilterOption {
  value: string;
  label: string;
  icon?: React.ComponentType<{ className?: string }>;
}

interface FacetedFilterProps {
  title: string;
  options: FacetedFilterOption[];
  selectedValues: Set<string>;
  onSelectedValuesChange: (values: Set<string>) => void;
}

export function FacetedFilter({
  title,
  options,
  selectedValues,
  onSelectedValuesChange,
}: FacetedFilterProps) {
  const toggleValue = (value: string) => {
    const newValues = new Set(selectedValues);
    if (newValues.has(value)) {
      newValues.delete(value);
    } else {
      newValues.add(value);
    }
    onSelectedValuesChange(newValues);
  };

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline" size="sm" className="h-8 border-dashed">
          {title}
          {selectedValues.size > 0 && (
            <>
              <span className="mx-1">·</span>
              <span className="rounded-sm bg-primary-600 text-white px-1 text-xs">
                {selectedValues.size}
              </span>
            </>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0" align="start">
        <div className="max-h-[300px] overflow-auto p-2 space-y-1">
          {options.map((option) => {
            const isSelected = selectedValues.has(option.value);
            return (
              <div
                key={option.value}
                className="flex items-center space-x-2 cursor-pointer hover:bg-accent rounded-sm p-2"
                onClick={() => toggleValue(option.value)}
              >
                <Checkbox checked={isSelected} />
                {option.icon && (
                  <option.icon className="h-4 w-4 text-muted-foreground" />
                )}
                <span className="text-sm flex-1">{option.label}</span>
              </div>
            );
          })}
        </div>
      </PopoverContent>
    </Popover>
  );
}
