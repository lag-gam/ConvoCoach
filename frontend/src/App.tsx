"use client"

import { useState, useRef, useEffect } from "react"
import { Mic, MicOff, Video, VideoOff, Loader } from "lucide-react"

const avatars = [
  {
    name: "Default Avatar",
    url: "https://media.licdn.com/dms/image/v2/D5603AQFQemGbPTJW5w/profile-displayphoto-shrink_200_200/profile-displayphoto-shrink_200_200/0/1723056712090?e=2147483647&v=beta&t=a6e5a0TMt4R3_FQgyjjbz1eayWz3WvE9NWSRjnpChWI",
  },
  { name: "Avatar 2", url: "https://static.planetminecraft.com/files/resource_media/screenshot/1428/stevepmc7855107.jpg" },
  { name: "Avatar 3", url: "https://example.com/avatar3.png" },
]

const prompts = [
  "Introduce yourself and your background",
  "Describe your ideal work environment",
  "Explain a challenging situation you've overcome",
  "Discuss your long-term career goals",
  "Share a recent accomplishment you're proud of",
]

export default function ConvoCoach() {
  const [recording, setRecording] = useState(false)
  const [videoUrl, setVideoUrl] = useState("")
  const [aiResponse, setAiResponse] = useState("")
  const [loading, setLoading] = useState(false)
  const [selectedAvatar, setSelectedAvatar] = useState(avatars[0].url)
  const [selectedPrompt, setSelectedPrompt] = useState("")
  const [webcamActive, setWebcamActive] = useState(false)
  const mediaRecorder = useRef(null)
  const audioChunks = useRef([])
  const videoRef = useRef(null)

  useEffect(() => {
    if (webcamActive) {
      startWebcam()
    } else {
      stopWebcam()
    }
  }, [webcamActive])

  const startWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
    } catch (err) {
      console.error("Error accessing webcam:", err)
    }
  }

  const stopWebcam = () => {
    if (videoRef.current?.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks()
      tracks.forEach((track) => track.stop())
      videoRef.current.srcObject = null
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorder.current = new MediaRecorder(stream)
      mediaRecorder.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data)
      }
      mediaRecorder.current.onstop = processRecording
      mediaRecorder.current.start()
      setRecording(true)
    } catch (err) {
      console.error("Error accessing microphone:", err)
    }
  }

  const stopRecording = () => {
    if (mediaRecorder.current) {
      mediaRecorder.current.stop()
      setRecording(false)
    }
  }

  const processRecording = async () => {
    setLoading(true)
    try {
      const audioBlob = new Blob(audioChunks.current, { type: "audio/wav" })
      const formData = new FormData()
      formData.append("audio", audioBlob, "recording.wav")
      formData.append("source_url", selectedAvatar)
      formData.append("prompt", selectedPrompt)

      const response = await fetch("http://127.0.0.1:5000/generate-video", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      if (data.error) {
        console.error("Error from server:", data.error)
        setAiResponse("Error generating response. Try again.")
        return
      }

      setAiResponse(data.ai_response)
      setVideoUrl(data.video_url)
    } catch (error) {
      console.error("Fetch error:", error)
      setAiResponse("Connection failed. Check server and try again.")
    } finally {
      setLoading(false)
      audioChunks.current = []
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-500 to-pink-500 p-8">
      <div className="container space-y-8">
        <h1 className="text-4xl font-bold text-white text-center">ConvoCoach</h1>

        {/* Practice Settings */}
        <div className="card">
          <h2 className="text-2xl font-semibold mb-4">Practice Settings</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Choose Your Speaker:
              </label>
              <select
                className="w-full p-2 border rounded-lg"
                value={selectedAvatar}
                onChange={(e) => setSelectedAvatar(e.target.value)}
              >
                {avatars.map((avatar, index) => (
                  <option key={index} value={avatar.url}>
                    {avatar.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select a Prompt:
              </label>
              <select
                className="w-full p-2 border rounded-lg"
                value={selectedPrompt}
                onChange={(e) => setSelectedPrompt(e.target.value)}
              >
                <option value="">Choose a prompt...</option>
                {prompts.map((prompt, index) => (
                  <option key={index} value={prompt}>
                    {prompt}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Flexbox container for Webcam and AI Assistant */}
        <div className="flex-section">
          {/* Webcam Section */}
          <div className="flex-1 card">
            <h3 className="text-xl font-semibold mb-2 text-[#1e3a8a]">Your Webcam</h3>
            <div className="video-container">
              {webcamActive ? (
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-auto object-contain"
                />
              ) : (
                <div className="flex items-center justify-center p-4">
                  <p className="text-gray-500">Webcam is off</p>
                </div>
              )}
              <button
                onClick={() => setWebcamActive(!webcamActive)}
                className="absolute top-2 right-2 bg-white p-2 rounded-full shadow hover:bg-blue-50 transition-colors"
              >
                {webcamActive ? (
                  <VideoOff size={20} className="text-[#1e3a8a]" />
                ) : (
                  <Video size={20} className="text-[#1e3a8a]" />
                )}
              </button>
            </div>
          </div>

          {/* AI Assistant Section */}
<div className="flex-1 card">
  <h3 className="text-xl font-semibold mb-2 text-[#1e3a8a]">AI Assistant</h3>
  <div className="video-container">
    {videoUrl ? (
      <video key={videoUrl} autoPlay controls className="w-full h-auto object-contain">
        <source src={videoUrl} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
    ) : (
      <div className="flex items-center justify-center p-4">
        <img
          src={selectedAvatar}
          alt="Selected avatar"
          className="w-full h-auto object-contain"
        />
      </div>
    )}
  </div>
</div>
</div>

        {/* Record / Stop Button */}
        <div className="flex justify-center">
          <button
            onClick={recording ? stopRecording : startRecording}
            className={`flex items-center gap-2 ${
              recording ? "bg-red-600 hover:bg-red-700" : "bg-blue-600 hover:bg-blue-700"
            } text-white px-6 py-3 rounded-lg transition duration-300`}
            disabled={!selectedPrompt || loading}
          >
            {recording ? (
              <>
                <MicOff size={20} />
                Stop Recording
              </>
            ) : (
              <>
                <Mic size={20} />
                Start Conversation
              </>
            )}
          </button>
        </div>

        {/* Loading Spinner */}
        {loading && (
          <div className="card text-center p-8">
            <Loader className="animate-spin text-blue-600 mx-auto" size={32} />
            <p className="mt-2 text-gray-600">Generating response...</p>
          </div>
        )}

        {/* AI Feedback */}
        {aiResponse && (
          <div className="card">
            <h3 className="text-xl font-semibold mb-2">AI Feedback:</h3>
            <p className="text-gray-800">{aiResponse}</p>
          </div>
        )}
      </div>
    </div>
  )
}
