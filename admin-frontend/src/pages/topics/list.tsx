import { useTable, useNavigation } from "@refinedev/core";

export const TopicList = () => {
  const { tableQueryResult } = useTable({
    resource: "topics",
  });

  const { edit, create } = useNavigation();

  const { data, isLoading } = tableQueryResult;

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div style={{ padding: "20px" }}>
      <h1>Topics</h1>
      <button onClick={() => create("topics")}>Create Topic</button>

      <table style={{ width: "100%", marginTop: "20px", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #ddd" }}>
            <th style={{ padding: "10px", textAlign: "left" }}>ID</th>
            <th style={{ padding: "10px", textAlign: "left" }}>Name</th>
            <th style={{ padding: "10px", textAlign: "left" }}>System Prompt</th>
            <th style={{ padding: "10px", textAlign: "left" }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {data?.data.map((topic: any) => (
            <tr key={topic.id} style={{ borderBottom: "1px solid #eee" }}>
              <td style={{ padding: "10px" }}>{topic.id}</td>
              <td style={{ padding: "10px" }}>{topic.name}</td>
              <td style={{ padding: "10px" }}>
                {topic.system_prompt?.substring(0, 50)}...
              </td>
              <td style={{ padding: "10px" }}>
                <button onClick={() => edit("topics", topic.id)}>Edit</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
