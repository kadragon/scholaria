import { useState } from "react";
import { useTable, useNavigation, useDelete, useList } from "@refinedev/core";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";

export const ContextList = () => {
  const { tableQueryResult } = useTable({
    resource: "contexts",
  });

  const { data: topicsData } = useList({
    resource: "topics",
  });

  const { edit, create, show } = useNavigation();
  const { mutate: deleteContext } = useDelete();
  const { toast } = useToast();

  const { data, isLoading } = tableQueryResult;

  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [assignDialogOpen, setAssignDialogOpen] = useState(false);
  const [selectedTopicId, setSelectedTopicId] = useState<string>("");
  const [isAssigning, setIsAssigning] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState(false);

  if (isLoading) {
    return <div className="p-6">Loading...</div>;
  }

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      const ids = data?.data.map((c) => c.id).filter((id): id is number => id !== undefined) || [];
      setSelectedIds(new Set(ids));
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

  const handleAssignToTopic = async () => {
    if (!selectedTopicId || selectedIds.size === 0) return;

    setIsAssigning(true);
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/admin/bulk/assign-context-to-topic`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({
            topic_id: parseInt(selectedTopicId),
            context_ids: Array.from(selectedIds),
          }),
        },
      );

      if (!response.ok) throw new Error("Failed to assign contexts");

      const result = await response.json();
      toast({
        title: "Success",
        description: `${result.assigned_count} contexts assigned to topic`,
      });

      setAssignDialogOpen(false);
      setSelectedIds(new Set());
      setSelectedTopicId("");
    } catch {
      toast({
        title: "Error",
        description: "Failed to assign contexts to topic",
        variant: "destructive",
      });
    } finally {
      setIsAssigning(false);
    }
  };

  const handleRegenerateEmbeddings = async () => {
    if (selectedIds.size === 0) return;

    setIsRegenerating(true);
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/admin/bulk/regenerate-embeddings`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({
            context_ids: Array.from(selectedIds),
          }),
        },
      );

      if (!response.ok) throw new Error("Failed to regenerate embeddings");

      const result = await response.json();
      toast({
        title: "Success",
        description: `${result.queued_count} contexts queued for embedding regeneration`,
      });

      setSelectedIds(new Set());
    } catch {
      toast({
        title: "Error",
        description: "Failed to regenerate embeddings",
        variant: "destructive",
      });
    } finally {
      setIsRegenerating(false);
    }
  };

  const allSelected =
    (data?.data?.length ?? 0) > 0 && selectedIds.size === (data?.data?.length ?? 0);

  return (
    <div className="p-6 space-y-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Contexts</CardTitle>
          <div className="flex gap-2">
            {selectedIds.size > 0 && (
              <>
                <Button
                  variant="outline"
                  onClick={() => setAssignDialogOpen(true)}
                >
                  Assign to Topic ({selectedIds.size})
                </Button>
                <Button
                  variant="outline"
                  onClick={handleRegenerateEmbeddings}
                  disabled={isRegenerating}
                >
                  {isRegenerating ? "Regenerating..." : "Regenerate Embeddings"}
                </Button>
              </>
            )}
            <Button onClick={() => create("contexts")}>Create Context</Button>
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
                <TableHead>Type</TableHead>
                <TableHead>Chunk Count</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data?.data.map((context) => (
                <TableRow key={context.id}>
                  <TableCell>
                    <Checkbox
                      checked={context.id !== undefined && typeof context.id === 'number' && selectedIds.has(context.id)}
                      onCheckedChange={(checked) => {
                        if (typeof context.id === 'number') {
                          handleSelectOne(context.id, checked as boolean);
                        }
                      }}
                    />
                  </TableCell>
                  <TableCell>{context.id}</TableCell>
                  <TableCell>{context.name}</TableCell>
                  <TableCell>{context.context_type}</TableCell>
                  <TableCell>{context.chunk_count}</TableCell>
                  <TableCell>{context.processing_status}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          if (typeof context.id === 'number') {
                            show("contexts", context.id);
                          }
                        }}
                      >
                        View
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          if (typeof context.id === 'number') {
                            edit("contexts", context.id);
                          }
                        }}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => {
                          if (context.id) {
                            deleteContext({
                              resource: "contexts",
                              id: context.id,
                            });
                          }
                        }}
                      >
                        Delete
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Dialog open={assignDialogOpen} onOpenChange={setAssignDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Assign Contexts to Topic</DialogTitle>
            <DialogDescription>
              Select a topic to assign {selectedIds.size} selected context(s).
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Select value={selectedTopicId} onValueChange={setSelectedTopicId}>
              <SelectTrigger>
                <SelectValue placeholder="Select a topic" />
              </SelectTrigger>
              <SelectContent>
                {topicsData?.data.map((topic) => (
                  topic.id !== undefined && (
                    <SelectItem key={topic.id} value={topic.id.toString()}>
                      {topic.name}
                    </SelectItem>
                  )
                ))}
              </SelectContent>
            </Select>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setAssignDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={handleAssignToTopic}
              disabled={!selectedTopicId || isAssigning}
            >
              {isAssigning ? "Assigning..." : "Assign"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
