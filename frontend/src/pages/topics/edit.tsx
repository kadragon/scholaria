import { useEffect, useState } from "react";
import { useOne, useUpdate, useNavigation } from "@refinedev/core";
import { useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export const TopicEdit = () => {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading: isLoadingTopic } = useOne({
    resource: "topics",
    id: id!,
  });
  const { mutate, isLoading } = useUpdate();
  const { list } = useNavigation();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");

  useEffect(() => {
    if (data?.data) {
      setName(data.data.name);
      setDescription(data.data.description || "");
      setSystemPrompt(data.data.system_prompt || "");
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
          description,
          system_prompt: systemPrompt,
        },
      },
      {
        onSuccess: () => {
          list("topics");
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
