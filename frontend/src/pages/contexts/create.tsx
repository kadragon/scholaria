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
          <CardTitle>Create Context</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div>
              <Label htmlFor="description">Description</Label>
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
                  <Label htmlFor="markdown">Markdown Content</Label>
                  <Textarea
                    id="markdown"
                    value={originalContent}
                    onChange={(e) => setOriginalContent(e.target.value)}
                    rows={10}
                    placeholder="# Your markdown content here..."
                  />
                </div>
              </TabsContent>

              <TabsContent value="PDF" className="space-y-4 mt-4">
                <div>
                  <Label htmlFor="pdf">PDF File</Label>
                  <Input id="pdf" type="file" accept=".pdf" disabled />
                  <p className="text-sm text-muted-foreground mt-2">
                    PDF upload will be implemented in next phase
                  </p>
                </div>
              </TabsContent>

              <TabsContent value="FAQ" className="space-y-4 mt-4">
                <p className="text-sm text-muted-foreground">
                  FAQ context will be created. Q&A pairs can be added after
                  creation.
                </p>
              </TabsContent>
            </Tabs>

            <div className="flex gap-2">
              <Button type="submit">Create</Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => list("contexts")}
              >
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};
