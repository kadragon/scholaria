import { useState, useEffect } from "react";
import { useOne, useUpdate, useNavigation, useList } from "@refinedev/core";
import { useParams } from "react-router";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { MultiSelect } from "@/components/ui/multi-select";

export const ContextEdit = () => {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading } = useOne({
    resource: "contexts",
    id: id!,
  });

  const { mutate: update } = useUpdate();
  const { list } = useNavigation();
  const { toast } = useToast();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [originalContent, setOriginalContent] = useState("");
  const [topicIds, setTopicIds] = useState<string[]>([]);

  const { data: topicsData } = useList({
    resource: "topics",
    pagination: { mode: "off" },
  });

  useEffect(() => {
    if (data?.data) {
      setName(data.data.name);
      setDescription(data.data.description);
      setOriginalContent(data.data.original_content || "");
      if (data.data.topics && Array.isArray(data.data.topics)) {
        setTopicIds(data.data.topics.map((t: { id: number }) => String(t.id)));
      }
    }
  }, [data]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    update(
      {
        resource: "contexts",
        id: id!,
        values: {
          name,
          description,
          original_content: originalContent || undefined,
          topic_ids: topicIds.map((id) => parseInt(id)),
        },
      },
      {
        onSuccess: () => {
          toast({
            title: "업데이트 성공",
            description: "컨텍스트가 성공적으로 업데이트되었습니다.",
          });
          list("contexts");
        },
        onError: (error) => {
          toast({
            variant: "destructive",
            title: "업데이트 실패",
            description:
              error.message || "컨텍스트 업데이트 중 오류가 발생했습니다.",
          });
        },
      },
    );
  };

  if (isLoading) {
    return <div className="p-6">로딩 중...</div>;
  }

  return (
    <div className="p-6">
      <Card>
        <CardHeader>
          <CardTitle>컨텍스트 편집: {data?.data.name}</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="name">이름</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div>
              <Label htmlFor="description">설명</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            {data?.data.context_type === "MARKDOWN" && (
              <div>
                <Label htmlFor="content">내용</Label>
                <Textarea
                  id="content"
                  value={originalContent}
                  onChange={(e) => setOriginalContent(e.target.value)}
                  rows={10}
                />
              </div>
            )}

            <div>
              <Label>연결된 토픽</Label>
              <MultiSelect
                options={
                  topicsData?.data?.map((topic) => ({
                    label: topic.name,
                    value: String(topic.id),
                  })) || []
                }
                selected={topicIds}
                onChange={setTopicIds}
                placeholder="토픽 선택..."
                emptyMessage="토픽이 없습니다."
              />
            </div>

            <div className="flex gap-2">
              <Button type="submit">저장</Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => list("contexts")}
              >
                취소
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};
