import { useState, useEffect } from "react";
import Gamification from "./Gamification";
import io from "socket.io-client"; // Connect to backend (if needed)

const socket = io("http://localhost:5000"); // Replace with backend URL

export default function Dashboard() {
  const [feedback, setFeedback] = useState("Start speaking...");

  useEffect(() => {
    socket.on("speechFeedback", (data) => {
      setFeedback(data.message);
    });

    return () => {
      socket.off("speechFeedback");
    };
  }, []);

  return (
    <div className="p-6 bg-gray-900 text-white min-h-screen flex flex-col items-center">
      <h2 className="text-xl font-bold">Real-Time Feedback</h2>
      <p className="mt-2 text-lg">{feedback}</p>
      <Gamification />
    </div>
  );
}

