import React, { useState } from "react";
import ChatInput from "./components/ChatInput.jsx";
import ChatWindow from "./components/ChatWindow.jsx";
import { askQuestion } from "./api/client.js";

export default function App() {
  const [turns, setTurns] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAsk = async (question) => {
    setLoading(true);
    try {
      const data = await askQuestion(question, conversationId);
      setConversationId(data.conversation_id);
      setTurns((prev) => [...prev, data]);
    } catch (err) {
      setTurns((prev) => [
        ...prev,
        {
          question,
          error: err?.response?.data?.detail || "Something went wrong reaching the agent.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto min-h-screen max-w-3xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">
          Agentic AI Analytics Assistant
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Ask business questions in plain English — the agent plans, writes SQL,
          validates it, self-corrects on error, and explains the results.
        </p>
      </header>

      <div className="mb-6 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <ChatInput onSubmit={handleAsk} loading={loading} />
      </div>

      {turns.length === 0 && !loading ? (
        <div className="rounded-2xl border border-dashed border-slate-300 p-8 text-center text-sm text-slate-400">
          Try one of the suggestions above to get started.
        </div>
      ) : (
        <ChatWindow turns={turns} loading={loading} />
      )}
    </div>
  );
}
