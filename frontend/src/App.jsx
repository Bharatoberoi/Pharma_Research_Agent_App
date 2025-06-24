import { useState } from "react";

function App() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    setResponse("");

    const res = await fetch("http://localhost:8000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });

    const data = await res.json();
    if (!data.task_id) {
      setResponse("Error submitting query.");
      setLoading(false);
      return;
    }

    const taskId = data.task_id;
    pollForResult(taskId);
  };

  const pollForResult = async (taskId) => {
    const interval = setInterval(async () => {
      const res = await fetch(`http://localhost:8000/result/${taskId}`);
      const data = await res.json();
      if (data.response) {
        clearInterval(interval);
        setResponse(data.response);
        setLoading(false);
      }
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center p-6">
      <h1 className="text-3xl font-bold mb-4 text-blue-700">Pharma Research Agent</h1>
      <textarea
        className="w-full max-w-2xl p-4 border rounded shadow-md"
        rows="5"
        placeholder="Ask about latest developments (e.g., 'CAR-T updates June 2025')"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button
        className="mt-4 bg-blue-600 text-white px-6 py-2 rounded shadow hover:bg-blue-700"
        onClick={handleSubmit}
        disabled={loading}
      >
        {loading ? "Researching..." : "Ask Agent"}
      </button>
      {response && (
        <div className="mt-6 bg-white p-4 rounded shadow w-full max-w-2xl">
          <h2 className="text-xl font-semibold mb-2">🧠 Agent Response:</h2>
          <pre className="whitespace-pre-wrap">{response}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
