import { useState } from "react";
import { useCreate, useNavigation } from "@refinedev/core";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export const TopicCreate = () => {
  const { mutate, isLoading } = useCreate();
  const { list } = useNavigation();
  const { toast } = useToast();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutate(
      {
        resource: "topics",
        values: {
          name,
          description,
          system_prompt: systemPrompt,
        },
      },
      {
        onSuccess: () => {
          toast({
            title: "생성 성공",
            description: "토픽이 성공적으로 생성되었습니다.",
          });
          list("topics");
        },
        onError: (error) => {
          toast({
            variant: "destructive",
            title: "생성 실패",
            description: error.message || "토픽 생성 중 오류가 발생했습니다.",
          });
        },
      },
    );
  };

  return (
    <div className="p-6">
      <Card>
        <CardHeader>
          <CardTitle>토픽 생성</CardTitle>
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
                {isLoading ? "생성 중..." : "생성"}
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
