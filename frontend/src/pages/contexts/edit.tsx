import { useState, useEffect } from "react";
import { useOne, useUpdate, useNavigation } from "@refinedev/core";
import { useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export const ContextEdit = () => {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading } = useOne({
    resource: "contexts",
    id: id!,
  });

  const { mutate: update } = useUpdate();
  const { list } = useNavigation();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [originalContent, setOriginalContent] = useState("");

  useEffect(() => {
    if (data?.data) {
      setName(data.data.name);
      setDescription(data.data.description);
      setOriginalContent(data.data.original_content || "");
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
        },
      },
      {
        onSuccess: () => {
          list("contexts");
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
