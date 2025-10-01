import { useState } from "react";
import { useCreate, useNavigation } from "@refinedev/core";

export const TopicCreate = () => {
  const { mutate, isLoading } = useCreate();
  const { list } = useNavigation();

  const [name, setName] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutate(
      {
        resource: "topics",
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

  return (
    <div style={{ padding: "20px" }}>
      <h1>Create Topic</h1>
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
          {isLoading ? "Creating..." : "Create"}
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
