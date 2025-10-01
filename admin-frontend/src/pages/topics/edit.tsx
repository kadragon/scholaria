import { useEffect, useState } from "react";
import { useOne, useUpdate, useNavigation } from "@refinedev/core";
import { useParams } from "react-router-dom";

export const TopicEdit = () => {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading: isLoadingTopic } = useOne({
    resource: "topics",
    id: id!,
  });
  const { mutate, isLoading } = useUpdate();
  const { list } = useNavigation();

  const [name, setName] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");

  useEffect(() => {
    if (data?.data) {
      setName(data.data.name);
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
          system_prompt: systemPrompt,
        },
      },
      {
        onSuccess: () => {
          list("topics");
        },
      }
    );
  };

  if (isLoadingTopic) {
    return <div>Loading...</div>;
  }

  return (
    <div style={{ padding: "20px" }}>
      <h1>Edit Topic</h1>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px" }}>Name:</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            style={{ width: "100%", padding: "8px" }}
          />
        </div>

        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px" }}>
            System Prompt:
          </label>
          <textarea
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            rows={6}
            style={{ width: "100%", padding: "8px" }}
          />
        </div>

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Updating..." : "Update"}
        </button>
        <button
          type="button"
          onClick={() => list("topics")}
          style={{ marginLeft: "10px" }}
        >
          Cancel
        </button>
      </form>
    </div>
  );
};
