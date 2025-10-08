import { useState, useMemo } from "react";
import { apiClient } from "../../lib/apiClient";
import { useTable, useNavigation, useDelete, useList, useUpdate } from "@refinedev/core";
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
import { DataTableToolbar } from "@/components/ui/data-table-toolbar";
import { FacetedFilter } from "@/components/ui/faceted-filter";
import { FileText, FileQuestion, FileCode } from "lucide-react";
import { InlineEditCell } from "@/components/InlineEditCell";
import { TableSkeleton } from "@/components/TableSkeleton";

const contextTypeOptions = [
  { value: "PDF", label: "PDF", icon: FileText },
  { value: "FAQ", label: "FAQ", icon: FileQuestion },
  { value: "MARKDOWN", label: "Markdown", icon: FileCode },
];

const statusOptions = [
  { value: "PENDING", label: "대기 중" },
  { value: "PROCESSING", label: "처리 중" },
  { value: "COMPLETED", label: "완료" },
  { value: "FAILED", label: "실패" },
];

export const ContextList = () => {
  const { tableQueryResult } = useTable({
    resource: "contexts",
  });

  const { data: topicsData } = useList({
    resource: "topics",
  });

  const { edit, create, show } = useNavigation();
  const { mutate: deleteContext } = useDelete();
  const { mutate: updateContext } = useUpdate();
  const { toast } = useToast();

  const { data, isLoading } = tableQueryResult;

  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [assignDialogOpen, setAssignDialogOpen] = useState(false);
  const [selectedTopicId, setSelectedTopicId] = useState<string>("");
  const [isAssigning, setIsAssigning] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState(false);

  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState<Set<string>>(new Set());
  const [statusFilter, setStatusFilter] = useState<Set<string>>(new Set());

  const filteredData = useMemo(() => {
    if (!data?.data) return [];

    return data.data.filter((context) => {
      const matchesSearch = searchQuery === "" ||
        context.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        context.description?.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesType = typeFilter.size === 0 ||
        typeFilter.has(context.context_type);

      const matchesStatus = statusFilter.size === 0 ||
        statusFilter.has(context.processing_status);

      return matchesSearch && matchesType && matchesStatus;
    });
  }, [data?.data, searchQuery, typeFilter, statusFilter]);

  const handleResetFilters = () => {
    setSearchQuery("");
    setTypeFilter(new Set());
    setStatusFilter(new Set());
  };

  const handleUpdateName = (id: number, newName: string) => {
    updateContext(
      {
        resource: "contexts",
        id,
        values: { name: newName },
      },
      {
        onSuccess: () => {
          toast({
            title: "성공",
            description: "컨텍스트 이름이 업데이트되었습니다.",
          });
          tableQueryResult.refetch();
        },
        onError: () => {
          toast({
            title: "오류",
            description: "컨텍스트 이름 업데이트에 실패했습니다.",
            variant: "destructive",
          });
        },
      }
    );
  };

  if (isLoading) {
    return (
      <div className="p-8 space-y-6">
        <div className="mb-6">
          <div className="h-9 bg-gray-200 animate-pulse rounded w-40 mb-2" />
          <div className="h-5 bg-gray-200 animate-pulse rounded w-72" />
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <TableSkeleton rows={8} columns={7} />
        </div>
      </div>
    );
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
      const response = await apiClient.post("/admin/bulk/assign-context-to-topic", {
        topic_id: parseInt(selectedTopicId),
        context_ids: Array.from(selectedIds),
      });

      const result = response.data;
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
      const response = await apiClient.post("/admin/bulk/regenerate-embeddings", {
        context_ids: Array.from(selectedIds),
      });

      const result = response.data;
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
    filteredData.length > 0 && selectedIds.size === filteredData.length;

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
          <DataTableToolbar
            searchValue={searchQuery}
            onSearchChange={setSearchQuery}
            searchPlaceholder="컨텍스트 검색..."
            isFiltered={searchQuery !== "" || typeFilter.size > 0 || statusFilter.size > 0}
            onReset={handleResetFilters}
            filters={
              <>
                <FacetedFilter
                  title="타입"
                  options={contextTypeOptions}
                  selectedValues={typeFilter}
                  onSelectedValuesChange={setTypeFilter}
                />
                <FacetedFilter
                  title="상태"
                  options={statusOptions}
                  selectedValues={statusFilter}
                  onSelectedValuesChange={setStatusFilter}
                />
              </>
            }
          />
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
              {filteredData.map((context) => (
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
                  <TableCell>
                    {typeof context.id === 'number' ? (
                      <InlineEditCell
                        value={context.name}
                        onSave={(newName) => handleUpdateName(context.id as number, newName)}
                      />
                    ) : (
                      context.name
                    )}
                  </TableCell>
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
