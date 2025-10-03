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
    return <div className="p-6">로딩 중...</div>;
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
        title: "성공",
        description: `${result.assigned_count}개 컨텍스트가 토픽에 할당되었습니다.`,
      });

      setAssignDialogOpen(false);
      setSelectedIds(new Set());
      setSelectedTopicId("");
    } catch {
      toast({
        title: "오류",
        description: "컨텍스트 할당에 실패했습니다.",
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
        title: "성공",
        description: `${result.queued_count}개 컨텍스트의 임베딩 재생성이 대기열에 추가되었습니다.`,
      });

      setSelectedIds(new Set());
    } catch {
      toast({
        title: "오류",
        description: "임베딩 재생성에 실패했습니다.",
        variant: "destructive",
      });
    } finally {
      setIsRegenerating(false);
    }
  };

  const allSelected =
    (data?.data?.length ?? 0) > 0 && selectedIds.size === (data?.data?.length ?? 0);

  return (
    <div className="p-8 space-y-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-secondary-900 mb-2">컨텍스트 관리</h1>
        <p className="text-secondary-600">지식 기반 컨텍스트를 생성하고 관리합니다</p>
      </div>
      <Card className="shadow-lg">
        <CardHeader className="flex flex-row items-center justify-between bg-gradient-to-r from-secondary-50 to-white border-b-2 border-secondary-100">
          <CardTitle className="text-xl font-bold text-secondary-800">컨텍스트 목록</CardTitle>
          <div className="flex gap-2">
            {selectedIds.size > 0 && (
              <>
                <Button
                  variant="outline"
                  onClick={() => setAssignDialogOpen(true)}
                >
                  토픽에 할당 ({selectedIds.size})
                </Button>
                <Button
                  variant="outline"
                  onClick={handleRegenerateEmbeddings}
                  disabled={isRegenerating}
                >
                  {isRegenerating ? "임베딩 재생성 중..." : "임베딩 재생성"}
                </Button>
              </>
            )}
            <Button onClick={() => create("contexts")}>컨텍스트 생성</Button>
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
                <TableHead>이름</TableHead>
                <TableHead>타입</TableHead>
                <TableHead>청크 수</TableHead>
                <TableHead>상태</TableHead>
                <TableHead>작업</TableHead>
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
                        보기
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
                        편집
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
                        삭제
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
            <DialogTitle>컨텍스트를 토픽에 할당</DialogTitle>
            <DialogDescription>
              선택한 {selectedIds.size}개 컨텍스트를 할당할 토픽을 선택하세요.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Select value={selectedTopicId} onValueChange={setSelectedTopicId}>
              <SelectTrigger>
                <SelectValue placeholder="토픽 선택" />
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
              취소
            </Button>
            <Button
              onClick={handleAssignToTopic}
              disabled={!selectedTopicId || isAssigning}
            >
              {isAssigning ? "할당 중..." : "할당"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
