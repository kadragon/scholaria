import { useState } from "react";
import { useCreate, useNavigation } from "@refinedev/core";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export const ContextCreate = () => {
  const { mutate: create } = useCreate();
  const { list } = useNavigation();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [contextType, setContextType] = useState<"MARKDOWN" | "PDF" | "FAQ">(
    "MARKDOWN",
  );
  const [originalContent, setOriginalContent] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    create(
      {
        resource: "contexts",
        values: {
          name,
          description,
          context_type: contextType,
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

  return (
    <div className="p-6">
      <Card>
        <CardHeader>
          <CardTitle>컨텍스트 생성</CardTitle>
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

            <Tabs
              value={contextType}
              onValueChange={(v) =>
                setContextType(v as "MARKDOWN" | "PDF" | "FAQ")
              }
            >
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="MARKDOWN">Markdown</TabsTrigger>
                <TabsTrigger value="PDF">PDF</TabsTrigger>
                <TabsTrigger value="FAQ">FAQ</TabsTrigger>
              </TabsList>

              <TabsContent value="MARKDOWN" className="space-y-4 mt-4">
                <div>
                  <Label htmlFor="markdown">Markdown 내용</Label>
                  <Textarea
                    id="markdown"
                    value={originalContent}
                    onChange={(e) => setOriginalContent(e.target.value)}
                    rows={10}
                    placeholder="# 마크다운 내용을 입력하세요..."
                  />
                </div>
              </TabsContent>

              <TabsContent value="PDF" className="space-y-4 mt-4">
                <div>
                  <Label htmlFor="pdf">PDF 파일</Label>
                  <Input id="pdf" type="file" accept=".pdf" disabled />
                  <p className="text-sm text-muted-foreground mt-2">
                    PDF 업로드는 다음 단계에서 구현될 예정입니다.
                  </p>
                </div>
              </TabsContent>

              <TabsContent value="FAQ" className="space-y-4 mt-4">
                <p className="text-sm text-muted-foreground">
                  FAQ 컨텍스트가 생성됩니다. Q&A 쌍은 생성 후 추가할 수 있습니다.
                </p>
              </TabsContent>
            </Tabs>

            <div className="flex gap-2">
              <Button type="submit">생성</Button>
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
