import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const client = axios.create({
  baseURL: `${BASE_URL}/api`,
  timeout: 60000,
});

export async function askQuestion(question, conversationId) {
  const { data } = await client.post("/query", {
    question,
    conversation_id: conversationId || null,
  });
  return data;
}
