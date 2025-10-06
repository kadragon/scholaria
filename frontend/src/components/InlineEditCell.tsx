import { useState, useRef, useEffect } from "react";
import { Input } from "@/components/ui/input";

interface InlineEditCellProps {
  value: string;
  onSave: (newValue: string) => void;
  className?: string;
}

export const InlineEditCell = ({
  value,
  onSave,
  className,
}: InlineEditCellProps) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(value);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleSave = () => {
    const trimmedValue = editValue.trim();
    if (trimmedValue && trimmedValue !== value) {
      onSave(trimmedValue);
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditValue(value);
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSave();
    } else if (e.key === "Escape") {
      handleCancel();
    }
  };

  if (isEditing) {
    return (
      <Input
        ref={inputRef}
        value={editValue}
        onChange={(e) => setEditValue(e.target.value)}
        onBlur={handleSave}
        onKeyDown={handleKeyDown}
        className="h-8 w-full"
      />
    );
  }

  return (
    <div
      onDoubleClick={() => setIsEditing(true)}
      className={`cursor-pointer hover:bg-secondary-50 rounded px-2 py-1 ${className}`}
      title="더블클릭하여 편집"
    >
      {value}
    </div>
  );
};
