import { useEffect, useRef, useState } from "react";
import { useNavigation } from "@refinedev/core";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001/api";

const directAxios = axios.create();
const MAX_FILE_SIZE_MB = 100;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

export const ContextCreate = () => {
  const { list } = useNavigation();
  const { toast } = useToast();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [contextType, setContextType] = useState<"MARKDOWN" | "PDF" | "FAQ" | "WEBSCRAPER">(
    "MARKDOWN",
  );
  const [originalContent, setOriginalContent] = useState("");
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [webUrl, setWebUrl] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [processingStatus, setProcessingStatus] = useState<string | null>(null);
  const pollingIntervalRef = useRef<number | null>(null);

  const pollContextStatus = async (contextId: number) => {
    const token = localStorage.getItem("token");
    const maxAttempts = 60;
    let attempts = 0;

    pollingIntervalRef.current = setInterval(async () => {
      attempts++;

      if (attempts > maxAttempts) {
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
        }
        setProcessingStatus(null);
        setIsSubmitting(false);
        toast({
          title: "처리 시간 초과",
          description: "처리가 너무 오래 걸립니다. 나중에 다시 확인해주세요.",
          variant: "destructive",
        });
        return;
      }

      try {
        const response = await directAxios.get(`${API_URL}/contexts/${contextId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        const status = response.data.processing_status;
        setProcessingStatus(status);

        if (status === "COMPLETED") {
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
          }
          setProcessingStatus(null);
          setIsSubmitting(false);
          const descriptionText = contextType === "PDF"
            ? "PDF 파싱 및 청킹이 완료되었습니다."
            : "웹 페이지 스크래핑 및 청킹이 완료되었습니다.";
          toast({
            title: "컨텍스트 생성 성공",
            description: descriptionText,
          });
          list("contexts");
        } else if (status === "FAILED") {
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
          }
          setProcessingStatus(null);
          setIsSubmitting(false);
          const errorDescText = contextType === "PDF"
            ? "PDF 파싱 중 오류가 발생했습니다."
            : "웹 페이지 스크래핑 중 오류가 발생했습니다.";
          toast({
            title: "처리 실패",
            description: errorDescText,
            variant: "destructive",
          });
        }
      } catch (error) {
        console.error("Polling error:", error);
      }
    }, 1000);
  };

  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (contextType === "PDF" && !pdfFile) {
      toast({
        title: "파일 필요",
        description: "PDF 컨텍스트를 생성하려면 PDF 파일을 선택해야 합니다.",
        variant: "destructive",
      });
      return;
    }
    if (contextType === "MARKDOWN" && !originalContent.trim()) {
      toast({
        title: "내용 필요",
        description: "Markdown 컨텍스트를 생성하려면 내용을 입력해야 합니다.",
        variant: "destructive",
      });
      return;
    }
    if (contextType === "WEBSCRAPER" && !webUrl.trim()) {
      toast({
        title: "URL 필요",
        description: "웹 스크래핑 컨텍스트를 생성하려면 URL을 입력해야 합니다.",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);

    try {
      const formData = new FormData();
      formData.append("name", name);
      formData.append("description", description);
      formData.append("context_type", contextType);

      if (contextType === "PDF" && pdfFile) {
        formData.append("file", pdfFile);
      } else if (contextType === "MARKDOWN" && originalContent) {
        formData.append("original_content", originalContent);
      } else if (contextType === "WEBSCRAPER" && webUrl) {
        formData.append("url", webUrl);
      }

      const token = localStorage.getItem("token");
      const response = await directAxios.post(`${API_URL}/contexts`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (contextType === "PDF" || contextType === "WEBSCRAPER") {
        const contextId = response.data.id;
        setProcessingStatus("PENDING");
        pollContextStatus(contextId);
      } else {
        toast({
          title: "컨텍스트 생성 성공",
          description: "컨텍스트가 생성되었습니다.",
        });
        list("contexts");
        setIsSubmitting(false);
      }
    } catch (error: unknown) {
      let errorMessage = "컨텍스트 생성에 실패했습니다.";
      const detail = (error as { response?: { data?: { detail?: any } } })?.response?.data?.detail;

      if (typeof detail === "string") {
        errorMessage = detail;
      } else if (Array.isArray(detail)) {
        errorMessage = detail.map((err: any) => err.msg || JSON.stringify(err)).join(", ");
      }

      toast({
        title: "오류",
        description: errorMessage,
        variant: "destructive",
      });
      setIsSubmitting(false);
      setProcessingStatus(null);
    }
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
                setContextType(v as "MARKDOWN" | "PDF" | "FAQ" | "WEBSCRAPER")
              }
            >
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="MARKDOWN">Markdown</TabsTrigger>
                <TabsTrigger value="PDF">PDF</TabsTrigger>
                <TabsTrigger value="FAQ">FAQ</TabsTrigger>
                <TabsTrigger value="WEBSCRAPER">Web URL</TabsTrigger>
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
                  <Input
                    id="pdf"
                    type="file"
                    accept=".pdf"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) {
                        if (file.size > MAX_FILE_SIZE_BYTES) {
                          toast({
                            title: "파일 크기 초과",
                            description: `파일 크기는 ${MAX_FILE_SIZE_MB}MB를 초과할 수 없습니다.`,
                            variant: "destructive",
                          });
                          e.target.value = "";
                          return;
                        }
                        setPdfFile(file);
                      }
                    }}
                  />
                  <p className="text-sm text-muted-foreground mt-2">
                    PDF 파일을 업로드하면 자동으로 파싱 및 청킹됩니다. (최대 {MAX_FILE_SIZE_MB}MB)
                  </p>
                </div>
              </TabsContent>

              <TabsContent value="FAQ" className="space-y-4 mt-4">
                <p className="text-sm text-muted-foreground">
                  FAQ 컨텍스트가 생성됩니다. Q&A 쌍은 생성 후 추가할 수 있습니다.
                </p>
              </TabsContent>

              <TabsContent value="WEBSCRAPER" className="space-y-4 mt-4">
                <div>
                  <Label htmlFor="webUrl">웹 페이지 URL</Label>
                  <Input
                    id="webUrl"
                    type="url"
                    value={webUrl}
                    onChange={(e) => setWebUrl(e.target.value)}
                    placeholder="https://example.com"
                  />
                  <p className="text-sm text-muted-foreground mt-2">
                    웹 페이지를 자동으로 스크래핑하여 내용을 추출하고 청킹합니다.
                  </p>
                </div>
              </TabsContent>
            </Tabs>

            <div className="flex gap-2">
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting
                  ? processingStatus === "PENDING"
                    ? contextType === "PDF" ? "PDF 파싱 중..." : "웹 스크래핑 중..."
                    : "생성 중..."
                  : "생성"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => list("contexts")}
                disabled={isSubmitting}
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
