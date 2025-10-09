import { useState, useMemo } from "react";
import { apiClient } from "../../lib/apiClient";
import { useTable, useNavigation, useDelete, useUpdate } from "@refinedev/core";
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
import { DataTableToolbar } from "@/components/ui/data-table-toolbar";
import { FacetedFilter } from "@/components/ui/faceted-filter";
import { InlineEditCell } from "@/components/InlineEditCell";
import { TableSkeleton } from "@/components/TableSkeleton";

const contextCountOptions = [
  { value: "has", label: "컨텍스트 있음" },
  { value: "none", label: "컨텍스트 없음" },
];

export const TopicList = () => {
  const { tableQueryResult } = useTable({
    resource: "topics",
  });

  const { edit, create } = useNavigation();
  const { toast } = useToast();
  const { mutate: deleteTopic } = useDelete();
  const { mutate: updateTopic } = useUpdate();

  const { data, isLoading } = tableQueryResult;

  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [updatePromptDialogOpen, setUpdatePromptDialogOpen] = useState(false);
  const [systemPrompt, setSystemPrompt] = useState("");
  const [isUpdating, setIsUpdating] = useState(false);

  const [searchQuery, setSearchQuery] = useState("");
  const [contextCountFilter, setContextCountFilter] = useState<Set<string>>(
    new Set(),
  );

  const filteredData = useMemo(() => {
    if (!data?.data) return [];

    return data.data.filter((topic) => {
      const matchesSearch =
        searchQuery === "" ||
        topic.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        topic.system_prompt?.toLowerCase().includes(searchQuery.toLowerCase());

      const hasContexts = (topic.contexts_count || 0) > 0;
      const matchesContextCount =
        contextCountFilter.size === 0 ||
        (contextCountFilter.has("has") && hasContexts) ||
        (contextCountFilter.has("none") && !hasContexts);

      return matchesSearch && matchesContextCount;
    });
  }, [data?.data, searchQuery, contextCountFilter]);

  const handleResetFilters = () => {
    setSearchQuery("");
    setContextCountFilter(new Set());
  };

  const handleUpdateName = (id: number, newName: string) => {
    updateTopic(
      {
        resource: "topics",
        id,
        values: { name: newName },
      },
      {
        onSuccess: () => {
          toast({
            title: "성공",
            description: "토픽 이름이 업데이트되었습니다.",
          });
          tableQueryResult.refetch();
        },
        onError: () => {
          toast({
            title: "오류",
            description: "토픽 이름 업데이트에 실패했습니다.",
            variant: "destructive",
          });
        },
      },
    );
  };

  const handleUpdateSlug = (id: number, newSlug: string) => {
    updateTopic(
      {
        resource: "topics",
        id,
        values: { slug: newSlug },
      },
      {
        onSuccess: () => {
          toast({
            title: "성공",
            description: "토픽 슬러그가 업데이트되었습니다.",
          });
          tableQueryResult.refetch();
        },
        onError: () => {
          toast({
            title: "오류",
            description: "토픽 슬러그 업데이트에 실패했습니다.",
            variant: "destructive",
          });
        },
      },
    );
  };

  if (isLoading) {
    return (
      <div className="p-8 space-y-6">
        <div className="mb-6">
          <div className="h-9 bg-gray-200 animate-pulse rounded w-32 mb-2" />
          <div className="h-5 bg-gray-200 animate-pulse rounded w-64" />
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <TableSkeleton rows={8} columns={6} />
        </div>
      </div>
    );
  }

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      const ids =
        data?.data
          .map((t) => t.id)
          .filter((id): id is number => id !== undefined) || [];
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

  const handleUpdateSystemPrompt = async () => {
    if (!systemPrompt.trim() || selectedIds.size === 0) return;

    setIsUpdating(true);
    try {
      const response = await apiClient.post(
        "/admin/bulk/update-system-prompt",
        {
          topic_ids: Array.from(selectedIds),
          system_prompt: systemPrompt,
        },
      );

      const result = response.data;
      toast({
        title: "성공",
        description: `${result.updated_count}개 토픽이 업데이트되었습니다.`,
      });

      setUpdatePromptDialogOpen(false);
      setSelectedIds(new Set());
      setSystemPrompt("");
      tableQueryResult.refetch();
    } catch {
      toast({
        title: "오류",
        description: "시스템 프롬프트 업데이트에 실패했습니다.",
        variant: "destructive",
      });
    } finally {
      setIsUpdating(false);
    }
  };

  const allSelected =
    filteredData.length > 0 && selectedIds.size === filteredData.length;

  return (
    <div className="p-8 space-y-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-secondary-900 mb-2">
          토픽 관리
        </h1>
        <p className="text-secondary-600">
          대화 주제별 토픽을 생성하고 관리합니다
        </p>
      </div>
      <Card className="shadow-lg">
        <CardHeader className="flex flex-row items-center justify-between bg-gradient-to-r from-secondary-50 to-white border-b-2 border-secondary-100">
          <CardTitle className="text-xl font-bold text-secondary-800">
            토픽 목록
          </CardTitle>
          <div className="flex gap-2">
            {selectedIds.size > 0 && (
              <Button
                variant="outline"
                onClick={() => setUpdatePromptDialogOpen(true)}
              >
                시스템 프롬프트 업데이트 ({selectedIds.size})
              </Button>
            )}
            <Button onClick={() => create("topics")}>토픽 생성</Button>
          </div>
        </CardHeader>
        <CardContent>
          <DataTableToolbar
            searchValue={searchQuery}
            onSearchChange={setSearchQuery}
            searchPlaceholder="토픽 검색..."
            isFiltered={searchQuery !== "" || contextCountFilter.size > 0}
            onReset={handleResetFilters}
            filters={
              <FacetedFilter
                title="컨텍스트 수"
                options={contextCountOptions}
                selectedValues={contextCountFilter}
                onSelectedValuesChange={setContextCountFilter}
              />
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
                <TableHead>슬러그</TableHead>
                <TableHead>시스템 프롬프트</TableHead>
                <TableHead>컨텍스트 수</TableHead>
                <TableHead>작업</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredData.map((topic) => (
                <TableRow key={topic.id}>
                  <TableCell>
                    <Checkbox
                      checked={
                        topic.id !== undefined &&
                        typeof topic.id === "number" &&
                        selectedIds.has(topic.id)
                      }
                      onCheckedChange={(checked) => {
                        if (typeof topic.id === "number") {
                          handleSelectOne(topic.id, checked as boolean);
                        }
                      }}
                    />
                  </TableCell>
                  <TableCell>{topic.id}</TableCell>
                  <TableCell>
                    {typeof topic.id === "number" ? (
                      <InlineEditCell
                        value={topic.name}
                        onSave={(newName) =>
                          handleUpdateName(topic.id as number, newName)
                        }
                      />
                    ) : (
                      topic.name
                    )}
                  </TableCell>
                  <TableCell>
                    {typeof topic.id === "number" ? (
                      <InlineEditCell
                        value={topic.slug}
                        onSave={(newSlug) =>
                          handleUpdateSlug(topic.id as number, newSlug)
                        }
                      />
                    ) : (
                      topic.slug
                    )}
                  </TableCell>
                  <TableCell className="max-w-xs truncate">
                    {topic.system_prompt}
                  </TableCell>
                  <TableCell>{topic.contexts_count || 0}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          if (typeof topic.id === "number") {
                            edit("topics", topic.id);
                          }
                        }}
                      >
                        편집
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => {
                          if (
                            typeof topic.id === "number" &&
                            confirm(`"${topic.name}" 토픽을 삭제하시겠습니까?`)
                          ) {
                            deleteTopic(
                              {
                                resource: "topics",
                                id: topic.id,
                              },
                              {
                                onSuccess: () => {
                                  toast({
                                    title: "성공",
                                    description: "토픽이 삭제되었습니다.",
                                  });
                                  tableQueryResult.refetch();
                                },
                              },
                            );
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

      <Dialog
        open={updatePromptDialogOpen}
        onOpenChange={setUpdatePromptDialogOpen}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>시스템 프롬프트 업데이트</DialogTitle>
            <DialogDescription>
              선택한 {selectedIds.size}개 토픽의 시스템 프롬프트를
              업데이트합니다.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-4">
            <div className="space-y-2">
              <Label htmlFor="system-prompt">시스템 프롬프트</Label>
              <Tabs defaultValue="kr" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="kr">한국어</TabsTrigger>
                  <TabsTrigger value="en">영어</TabsTrigger>
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
              취소
            </Button>
            <Button
              onClick={handleUpdateSystemPrompt}
              disabled={!systemPrompt.trim() || isUpdating}
            >
              {isUpdating ? "업데이트 중..." : "업데이트"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
