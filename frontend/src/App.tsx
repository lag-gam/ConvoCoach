import { useState, useRef } from 'react'
import { Mic, MicOff, Video, Loader } from 'lucide-react'

export default function ConvoCoach() {
  const [recording, setRecording] = useState(false)
  const [videoUrl, setVideoUrl] = useState('')
  const [aiResponse, setAiResponse] = useState('')
  const [loading, setLoading] = useState(false)
  const mediaRecorder = useRef<MediaRecorder | null>(null)
  const audioChunks = useRef<Blob[]>([])

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
      console.error('Error accessing microphone:', err)
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
      const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' })
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.wav')
  
      const response = await fetch("http://127.0.0.1:5000/generate-video", {
        method: "POST",
        body: formData,
      })
  
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
  
      const data = await response.json()
  
      if (data.error) {
        console.error('Error from server:', data.error)
        setAiResponse("Error generating response. Try again.")
        return
      }
  
      setAiResponse(data.ai_response)
      setVideoUrl(data.video_url)
      
    } catch (error) {
      console.error('Fetch error:', error)
      setAiResponse("Connection failed. Check server and try again.")
    } finally {
      setLoading(false)
      audioChunks.current = []
    }
  }
  

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="bg-white rounded-lg shadow-lg p-4">
          <div className="mt-4 flex justify-center gap-4">
            <button
              onClick={recording ? stopRecording : startRecording}
              className="flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
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
        </div>

        {loading && (
          <div className="text-center p-8">
            <Loader className="animate-spin text-blue-600" size={32} />
            <p className="mt-2 text-gray-600">Generating response...</p>
          </div>
        )}

        {aiResponse && (
          <div className="bg-white rounded-lg shadow-lg p-4">
            <p className="text-gray-800">{aiResponse}</p>
          </div>
        )}
        
        {videoUrl && (
  <div className="bg-white rounded-lg shadow-lg p-4">
    <h3 className="text-lg font-semibold">AI Video Response</h3>
    <video 
      key={videoUrl}  // Force re-render when URL changes
      controls 
      width="50%"
      autoplay
    >
      <source src={videoUrl} type="video/mp4" />
      Your browser does not support the video tag.
    </video>
  </div>
)}

      </div>
    </div>
  )
}
