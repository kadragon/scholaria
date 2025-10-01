import { useTable, useNavigation, useDelete } from "@refinedev/core";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export const ContextList = () => {
  const { tableQueryResult } = useTable({
    resource: "contexts",
  });

  const { edit, create } = useNavigation();
  const { mutate: deleteContext } = useDelete();

  const { data, isLoading } = tableQueryResult;

  if (isLoading) {
    return <div className="p-6">Loading...</div>;
  }

  return (
    <div className="p-6 space-y-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Contexts</CardTitle>
          <Button onClick={() => create("contexts")}>Create Context</Button>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Chunk Count</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data?.data.map((context) => (
                <TableRow key={context.id}>
                  <TableCell>{context.id}</TableCell>
                  <TableCell>{context.name}</TableCell>
                  <TableCell>{context.context_type}</TableCell>
                  <TableCell>{context.chunk_count}</TableCell>
                  <TableCell>{context.processing_status}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          context.id && edit("contexts", context.id)
                        }
                      >
                        Edit
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => {
                          if (context.id) {
                            deleteContext({
                              resource: "contexts",
                              id: context.id,
                            });
                          }
                        }}
                      >
                        Delete
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};
