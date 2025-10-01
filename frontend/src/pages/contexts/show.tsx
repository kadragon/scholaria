import { useState, useEffect } from "react";
import { useOne, useNavigation } from "@refinedev/core";
import { useParams } from "react-router-dom";
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

interface ContextItem {
  id: number;
  title: string;
  content: string;
  context_id: number;
  created_at: string;
  updated_at: string;
}

export const ContextShow = () => {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading } = useOne({
    resource: "contexts",
    id: id!,
  });

  const { list, edit } = useNavigation();
  const [items, setItems] = useState<ContextItem[]>([]);
  const [itemsLoading, setItemsLoading] = useState(true);

  useEffect(() => {
    const fetchItems = async () => {
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/contexts/${id}/items`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          },
        );
        if (response.ok) {
          const data = await response.json();
          setItems(data);
        }
      } catch (error) {
        console.error("Failed to fetch items:", error);
      } finally {
        setItemsLoading(false);
      }
    };

    if (id) {
      fetchItems();
    }
  }, [id]);

  if (isLoading) {
    return <div className="p-6">Loading...</div>;
  }

  const context = data?.data;

  return (
    <div className="p-6 space-y-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Context Details</CardTitle>
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => context?.id && edit("contexts", context.id)}
            >
              Edit
            </Button>
            <Button variant="outline" onClick={() => list("contexts")}>
              Back to List
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold">Name</h3>
            <p>{context?.name}</p>
          </div>
          <div>
            <h3 className="font-semibold">Description</h3>
            <p>{context?.description || "N/A"}</p>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <h3 className="font-semibold">Type</h3>
              <p>{context?.context_type}</p>
            </div>
            <div>
              <h3 className="font-semibold">Chunk Count</h3>
              <p>{context?.chunk_count}</p>
            </div>
            <div>
              <h3 className="font-semibold">Status</h3>
              <p>{context?.processing_status}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Chunks ({items.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {itemsLoading ? (
            <div>Loading chunks...</div>
          ) : items.length === 0 ? (
            <div className="text-gray-500">No chunks available</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[100px]">ID</TableHead>
                  <TableHead className="w-[200px]">Title</TableHead>
                  <TableHead>Content Preview</TableHead>
                  <TableHead className="w-[180px]">Created</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.id}</TableCell>
                    <TableCell className="font-medium">{item.title}</TableCell>
                    <TableCell className="truncate max-w-md">
                      {item.content.substring(0, 100)}
                      {item.content.length > 100 ? "..." : ""}
                    </TableCell>
                    <TableCell className="text-sm text-gray-500">
                      {new Date(item.created_at).toLocaleDateString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
