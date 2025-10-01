import { useState } from "react";
import { useTable, useNavigation } from "@refinedev/core";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";

export const TopicList = () => {
  const { tableQueryResult } = useTable({
    resource: "topics",
  });

  const { edit, create } = useNavigation();
  const { toast } = useToast();

  const { data, isLoading } = tableQueryResult;

  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [updatePromptDialogOpen, setUpdatePromptDialogOpen] = useState(false);
  const [systemPrompt, setSystemPrompt] = useState("");
  const [isUpdating, setIsUpdating] = useState(false);

  if (isLoading) {
    return <div className="p-6">Loading...</div>;
  }

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedIds(new Set(data?.data.map((t) => t.id) || []));
    } else {
      setSelectedIds(new Set());
    }
  };

  const handleSelectOne = (id: number, checked: boolean) => {
    const newSelected = new Set(selectedIds);
    if (checked) {
      newSelected.add(id);
    } else {
      newSelected.delete(id);
    }
    setSelectedIds(newSelected);
  };

  const handleUpdateSystemPrompt = async () => {
    if (!systemPrompt.trim() || selectedIds.size === 0) return;

    setIsUpdating(true);
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/admin/bulk/update-system-prompt`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({
            topic_ids: Array.from(selectedIds),
            system_prompt: systemPrompt,
          }),
        },
      );

      if (!response.ok) throw new Error("Failed to update system prompts");

      const result = await response.json();
      toast({
        title: "Success",
        description: `${result.updated_count} topics updated`,
      });

      setUpdatePromptDialogOpen(false);
      setSelectedIds(new Set());
      setSystemPrompt("");
      tableQueryResult.refetch();
    } catch {
      toast({
        title: "Error",
        description: "Failed to update system prompts",
        variant: "destructive",
      });
    } finally {
      setIsUpdating(false);
    }
  };

  const allSelected =
    data?.data.length > 0 && selectedIds.size === data?.data.length;

  return (
    <div className="p-6 space-y-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Topics</CardTitle>
          <div className="flex gap-2">
            {selectedIds.size > 0 && (
              <Button
                variant="outline"
                onClick={() => setUpdatePromptDialogOpen(true)}
              >
                Update System Prompt ({selectedIds.size})
              </Button>
            )}
            <Button onClick={() => create("topics")}>Create Topic</Button>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">
                  <Checkbox
                    checked={allSelected}
                    onCheckedChange={handleSelectAll}
                  />
                </TableHead>
                <TableHead>ID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>System Prompt</TableHead>
                <TableHead>Contexts</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data?.data.map((topic) => (
                <TableRow key={topic.id}>
                  <TableCell>
                    <Checkbox
                      checked={selectedIds.has(topic.id)}
                      onCheckedChange={(checked) =>
                        handleSelectOne(topic.id, checked as boolean)
                      }
                    />
                  </TableCell>
                  <TableCell>{topic.id}</TableCell>
                  <TableCell>{topic.name}</TableCell>
                  <TableCell className="max-w-xs truncate">
                    {topic.system_prompt}
                  </TableCell>
                  <TableCell>{topic.contexts_count || 0}</TableCell>
                  <TableCell>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => topic.id && edit("topics", topic.id)}
                    >
                      Edit
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Dialog
        open={updatePromptDialogOpen}
        onOpenChange={setUpdatePromptDialogOpen}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Update System Prompt</DialogTitle>
            <DialogDescription>
              Update the system prompt for {selectedIds.size} selected topic(s).
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-4">
            <div className="space-y-2">
              <Label htmlFor="system-prompt">System Prompt</Label>
              <Tabs defaultValue="kr" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="kr">Korean</TabsTrigger>
                  <TabsTrigger value="en">English</TabsTrigger>
                </TabsList>
                <TabsContent value="kr">
                  <textarea
                    id="system-prompt"
                    className="w-full min-h-[200px] p-3 border rounded-md"
                    placeholder="당신은 도움이 되는 AI 어시스턴트입니다..."
                    value={systemPrompt}
                    onChange={(e) => setSystemPrompt(e.target.value)}
                  />
                </TabsContent>
                <TabsContent value="en">
                  <textarea
                    id="system-prompt-en"
                    className="w-full min-h-[200px] p-3 border rounded-md"
                    placeholder="You are a helpful AI assistant..."
                    value={systemPrompt}
                    onChange={(e) => setSystemPrompt(e.target.value)}
                  />
                </TabsContent>
              </Tabs>
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setUpdatePromptDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={handleUpdateSystemPrompt}
              disabled={!systemPrompt.trim() || isUpdating}
            >
              {isUpdating ? "Updating..." : "Update"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
