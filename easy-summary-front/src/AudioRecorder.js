import React, { useState, useEffect, useRef } from 'react'
import useWebSocket from './Socket'

const AudioRecorder = () => {
	const isRecording = useRef(false)
	const [transcribedText, setTranscribedText] = useState('')
	const sendInterval = useRef(null)

	const audioStreamRef = useRef(null)
	const mediaRecorderRef = useRef(null)

	const onMessage = (event) => {
		const data = event.data
		setTranscribedText((prev) => prev + " " + data) // Добавление транскрибированного текста
	}

	const socketRef = useWebSocket(onMessage)


	const record_and_send = () => {
		mediaRecorderRef.current = new MediaRecorder(audioStreamRef.current, { mimeType: 'audio/ogg;codecs=opus' })
		const chunks = []

		// Собираем чанк данных
		mediaRecorderRef.current.ondataavailable = e => {
			console.log("Pushing chunk:", e.data)
			chunks.push(e.data)
		}

		mediaRecorderRef.current.onstop = e => {
			console.log("Sending chunks:", chunks)
			sendAudioToServer(new Blob(chunks))
		}

		// Обработка ошибок
		mediaRecorderRef.current.onerror = (error) => {
			console.error("Recording error:", error)
			isRecording.current = false
		}

		// Запуск записи
		mediaRecorderRef.current.start()

		// Останавливаем запись через 1 секунду
		setTimeout(() => {
			mediaRecorderRef.current.stop()

			// После остановки записи запускаем следующую запись
			console.log("Is recording:", isRecording)
			if (isRecording.current) {
				console.log("Next recording")
				record_and_send()
			}
		}, 5000)
	}

	const startRecording = async () => {
		audioStreamRef.current = await navigator.mediaDevices.getUserMedia({ audio: true })
		isRecording.current = true
		record_and_send()
	}

	const stopRecording = async () => {
		if (mediaRecorderRef.current) {
			console.log("After clicking stop button")
			clearInterval(sendInterval.current)
			mediaRecorderRef.current.stop()
			isRecording.current = false
		}
		audioStreamRef.current.getTracks().forEach(track => track.stop())
	}

	const sendAudioToServer = (audioData) => {
		if (socketRef.current.readyState === WebSocket.OPEN) {
			console.log("bytes", audioData)
			socketRef.current.send(audioData) // Отправка аудио на сервер
		}
	}

	const clearText = () => {
		setTranscribedText('')
	}

	const downloadText = () => {
		const blob = new Blob([transcribedText], { type: 'text/plain' })
		const url = URL.createObjectURL(blob)
		const a = document.createElement('a')
		a.href = url
		a.download = 'transcription.md'
		a.click()
	}

	return (
		<div className="max-w-4xl mx-auto p-6">
			<h1 className="text-3xl font-bold text-center mb-6">Audio Recorder & Transcription</h1>

			<div className="flex justify-center gap-4 mb-6">
				<button
					onClick={startRecording}
					disabled={isRecording.current}
					className="px-6 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-blue-300"
				>
					Start Recording
				</button>
				<button
					onClick={stopRecording}
					disabled={!isRecording.current}
					className="px-6 py-2 bg-red-500 text-white font-semibold rounded-lg hover:bg-red-700 disabled:bg-red-300"
				>
					Stop Recording
				</button>
			</div>

			<div className="mb-6">
				<h2 className="text-2xl font-semibold mb-3">Transcribed Text</h2>
				<div className="p-4 border border-gray-300 rounded-lg bg-gray-50 whitespace-pre-wrap">
					<div className="prose prose-sm dark:prose-invert">{transcribedText}</div>
				</div>
			</div>

			<div className="flex justify-center gap-4">
				<button
					onClick={clearText}
					className="px-6 py-2 bg-gray-500 text-white font-semibold rounded-lg hover:bg-gray-700"
				>
					Clear Text
				</button>
				<button
					onClick={downloadText}
					className="px-6 py-2 bg-indigo-500 text-white font-semibold rounded-lg hover:bg-indigo-700"
				>
					Download Text
				</button>
			</div>
		</div>
	)
}

export default AudioRecorder
