import { useState, useEffect } from "react";
import { useOne, useNavigation } from "@refinedev/core";
import { useParams } from "react-router-dom";
import { useCallback } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { GripVertical } from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001/api";

const axiosInstance = axios.create();

axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/admin/login";
    }
    return Promise.reject(error);
  }
);

interface ContextItem {
  id: number;
  title: string;
  content: string;
  context_id: number;
  order_index: number;
  created_at: string;
  updated_at: string;
}

interface SortableRowProps {
  item: ContextItem;
  onEdit: (item: ContextItem) => void;
}

function SortableRow({ item, onEdit }: SortableRowProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: item.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <TableRow ref={setNodeRef} style={style}>
      <TableCell>
        <div {...attributes} {...listeners} className="cursor-grab active:cursor-grabbing">
          <GripVertical className="h-5 w-5 text-gray-400" />
        </div>
      </TableCell>
      <TableCell>{item.id}</TableCell>
      <TableCell className="font-medium">{item.title}</TableCell>
      <TableCell className="max-w-md">
        <div className="line-clamp-3 whitespace-pre-wrap">
          {item.content}
        </div>
      </TableCell>
      <TableCell className="text-sm text-gray-500">
        {new Date(item.created_at).toLocaleDateString()}
      </TableCell>
      <TableCell>
        <Button variant="outline" size="sm" onClick={() => onEdit(item)}>
          편집
        </Button>
      </TableCell>
    </TableRow>
  );
}

export const ContextShow = () => {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading } = useOne({
    resource: "contexts",
    id: id!,
  });

  const { list, edit } = useNavigation();
  const { toast } = useToast();
  const [items, setItems] = useState<ContextItem[]>([]);
  const [itemsLoading, setItemsLoading] = useState(true);
  const [editingItem, setEditingItem] = useState<ContextItem | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editContent, setEditContent] = useState("");
  const [saving, setSaving] = useState(false);
  const [addQADialogOpen, setAddQADialogOpen] = useState(false);
  const [qaTitle, setQATitle] = useState("");
  const [qaContent, setQAContent] = useState("");
  const [addingQA, setAddingQA] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const fetchItems = useCallback(async () => {
    try {
      const response = await axiosInstance.get(`${API_URL}/contexts/${id}/items`);
      const sortedData = response.data.sort((a: ContextItem, b: ContextItem) =>
        a.order_index - b.order_index
      );
      setItems(sortedData);
    } catch (error) {
      console.error("Failed to fetch items:", error);
    } finally {
      setItemsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (id) {
      fetchItems();
    }
  }, [id, fetchItems]);

  const handleEditClick = (item: ContextItem) => {
    setEditingItem(item);
    setEditContent(item.content);
    setEditDialogOpen(true);
  };

  const handleSaveEdit = async () => {
    if (!editingItem) return;

    setSaving(true);
    try {
      await axiosInstance.patch(
        `${API_URL}/contexts/${id}/items/${editingItem.id}`,
        { content: editContent }
      );

      setEditDialogOpen(false);
      setEditingItem(null);
      setEditContent("");
      fetchItems();
      toast({
        title: "저장 성공",
        description: "청크가 업데이트되었습니다.",
      });
    } catch (error) {
      console.error("Error updating item:", error);
      toast({
        title: "저장 실패",
        description: "청크 업데이트에 실패했습니다.",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleAddQA = async () => {
    if (!qaTitle.trim() || !qaContent.trim()) {
      toast({
        title: "입력 필요",
        description: "질문과 답변을 모두 입력해주세요.",
        variant: "destructive",
      });
      return;
    }

    setAddingQA(true);
    try {
      await axiosInstance.post(
        `${API_URL}/contexts/${id}/qa`,
        { title: qaTitle, content: qaContent }
      );

      setAddQADialogOpen(false);
      setQATitle("");
      setQAContent("");
      fetchItems();
      toast({
        title: "Q&A 추가 성공",
        description: "Q&A가 추가되었습니다.",
      });
    } catch (error) {
      console.error("Error adding Q&A:", error);
      toast({
        title: "추가 실패",
        description: "Q&A 추가에 실패했습니다.",
        variant: "destructive",
      });
    } finally {
      setAddingQA(false);
    }
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;

    if (!over || active.id === over.id) {
      return;
    }

    const oldIndex = items.findIndex((item) => item.id === active.id);
    const newIndex = items.findIndex((item) => item.id === over.id);

    const newItems = arrayMove(items, oldIndex, newIndex);
    const previousItems = [...items];

    setItems(newItems);

    try {
      const updates = newItems.map((item, index) => ({
        id: item.id,
        order_index: index,
      }));

      const updatePromises = updates
        .filter((update, index) => update.order_index !== previousItems[index]?.order_index)
        .map((update) =>
          axiosInstance.patch(
            `${API_URL}/contexts/${id}/items/${update.id}`,
            { order_index: update.order_index }
          )
        );

      await Promise.all(updatePromises);

      toast({
        title: "순서 변경 완료",
        description: "청크 순서가 업데이트되었습니다.",
      });
    } catch (error) {
      console.error("Error updating order:", error);
      setItems(previousItems);
      toast({
        title: "순서 변경 실패",
        description: "청크 순서 업데이트에 실패했습니다.",
        variant: "destructive",
      });
    }
  };

  if (isLoading) {
    return <div className="p-6">로딩 중...</div>;
  }

  const context = data?.data;

  return (
    <div className="p-6 space-y-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>컨텍스트 상세</CardTitle>
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => context?.id && edit("contexts", context.id)}
            >
              편집
            </Button>
            <Button variant="outline" onClick={() => list("contexts")}>
              목록으로
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold">이름</h3>
            <p>{context?.name}</p>
          </div>
          <div>
            <h3 className="font-semibold">설명</h3>
            <p>{context?.description || "없음"}</p>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <h3 className="font-semibold">타입</h3>
              <p>{context?.context_type}</p>
            </div>
            <div>
              <h3 className="font-semibold">청크 수</h3>
              <p>{context?.chunk_count}</p>
            </div>
            <div>
              <h3 className="font-semibold">상태</h3>
              <p>{context?.processing_status}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>청크 목록 ({items.length})</CardTitle>
          {context?.context_type === "FAQ" && (
            <Button onClick={() => setAddQADialogOpen(true)}>
              Q&A 추가
            </Button>
          )}
        </CardHeader>
        <CardContent>
          {itemsLoading ? (
            <div>청크 로딩 중...</div>
          ) : items.length === 0 ? (
            <div className="text-gray-500">청크가 없습니다</div>
          ) : (
            <DndContext
              sensors={sensors}
              collisionDetection={closestCenter}
              onDragEnd={handleDragEnd}
            >
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[50px]"></TableHead>
                    <TableHead className="w-[100px]">ID</TableHead>
                    <TableHead className="w-[200px]">제목</TableHead>
                    <TableHead>내용 미리보기</TableHead>
                    <TableHead className="w-[180px]">생성일</TableHead>
                    <TableHead className="w-[100px]">작업</TableHead>
                  </TableRow>
                </TableHeader>
                <SortableContext
                  items={items.map((item) => item.id)}
                  strategy={verticalListSortingStrategy}
                >
                  <TableBody>
                    {items.map((item) => (
                      <SortableRow
                        key={item.id}
                        item={item}
                        onEdit={handleEditClick}
                      />
                    ))}
                  </TableBody>
                </SortableContext>
              </Table>
            </DndContext>
          )}
        </CardContent>
      </Card>

      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>청크 편집</DialogTitle>
            <DialogDescription>
              청크 내용을 수정합니다. 저장 시 embedding이 재생성됩니다.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="edit-content">내용</Label>
              <Textarea
                id="edit-content"
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                rows={10}
                className="resize-y"
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setEditDialogOpen(false)}
              disabled={saving}
            >
              취소
            </Button>
            <Button onClick={handleSaveEdit} disabled={saving}>
              {saving ? "저장 중..." : "저장"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={addQADialogOpen} onOpenChange={setAddQADialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Q&A 추가</DialogTitle>
            <DialogDescription>
              FAQ 컨텍스트에 질문과 답변을 추가합니다.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="qa-title">질문 (Question)</Label>
              <Textarea
                id="qa-title"
                value={qaTitle}
                onChange={(e) => setQATitle(e.target.value)}
                rows={2}
                placeholder="질문을 입력하세요..."
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="qa-content">답변 (Answer)</Label>
              <Textarea
                id="qa-content"
                value={qaContent}
                onChange={(e) => setQAContent(e.target.value)}
                rows={8}
                className="resize-y"
                placeholder="답변을 입력하세요..."
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setAddQADialogOpen(false);
                setQATitle("");
                setQAContent("");
              }}
              disabled={addingQA}
            >
              취소
            </Button>
            <Button onClick={handleAddQA} disabled={addingQA}>
              {addingQA ? "추가 중..." : "추가"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
