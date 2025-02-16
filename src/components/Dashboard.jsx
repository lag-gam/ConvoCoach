import SpeechInput from "./SpeechInput";
import Feedback from "./Feedback";
import Gamification from "./Gamification";
import Avatar from "./Avatar";

export default function Dashboard() {
  return (
    <div className="p-6 bg-gray-900 text-white min-h-screen flex flex-col items-center">
      <h1 className="text-3xl font-bold">ConvoCoach</h1>
      <SpeechInput />
      <Feedback />
      <Avatar />
      <Gamification />
    </div>
  );
}


