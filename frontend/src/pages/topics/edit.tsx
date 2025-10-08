import { useEffect, useState } from "react";
import { useOne, useUpdate, useNavigation, useList } from "@refinedev/core";
import { useParams } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { MultiSelect } from "@/components/ui/multi-select";

export const TopicEdit = () => {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading: isLoadingTopic } = useOne({
    resource: "topics",
    id: id!,
  });
  const { mutate, isLoading } = useUpdate();
  const { list } = useNavigation();
  const { toast } = useToast();

  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [description, setDescription] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [contextIds, setContextIds] = useState<string[]>([]);

  const { data: contextsData } = useList({
    resource: "contexts",
    pagination: { mode: "off" },
  });

  useEffect(() => {
    if (data?.data) {
      setName(data.data.name);
      setSlug(data.data.slug || "");
      setDescription(data.data.description || "");
      setSystemPrompt(data.data.system_prompt || "");
      if (data.data.context_ids && Array.isArray(data.data.context_ids)) {
        setContextIds(data.data.context_ids.map((id: number) => String(id)));
      }
    }
  }, [data]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutate(
      {
        resource: "topics",
        id: id!,
        values: {
          name,
          slug,
          description,
          system_prompt: systemPrompt,
          context_ids: contextIds.map((id) => parseInt(id)),
        },
      },
      {
        onSuccess: () => {
          toast({
            title: "업데이트 성공",
            description: "토픽이 성공적으로 업데이트되었습니다.",
          });
          list("topics");
        },
        onError: (error) => {
          toast({
            variant: "destructive",
            title: "업데이트 실패",
            description: error.message || "토픽 업데이트 중 오류가 발생했습니다.",
          });
        },
      },
    );
  };

  if (isLoadingTopic) {
    return <div className="p-6">로딩 중...</div>;
  }

  return (
    <div className="p-6">
      <Card>
        <CardHeader>
          <CardTitle>토픽 편집: {data?.data.name}</CardTitle>
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
              <Label htmlFor="slug">슬러그</Label>
              <Input
                id="slug"
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                placeholder="topic-slug"
                maxLength={50}
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

            <div>
              <Label htmlFor="systemPrompt">시스템 프롬프트</Label>
              <Textarea
                id="systemPrompt"
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                rows={6}
              />
            </div>

            <div>
              <Label>연결된 컨텍스트</Label>
              <MultiSelect
                options={
                  contextsData?.data?.map((ctx) => ({
                    label: ctx.name,
                    value: String(ctx.id),
                  })) || []
                }
                selected={contextIds}
                onChange={setContextIds}
                placeholder="컨텍스트 선택..."
                emptyMessage="컨텍스트가 없습니다."
              />
            </div>

            <div className="flex gap-2">
              <Button type="submit" disabled={isLoading}>
                {isLoading ? "업데이트 중..." : "업데이트"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => list("topics")}
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
