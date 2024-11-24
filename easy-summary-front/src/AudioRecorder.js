import React, { useState, useEffect, useRef } from 'react'
import { io } from 'socket.io-client'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import 'github-markdown-css/github-markdown.css'

const URL = 'ws://localhost:7256'

const AudioRecorder = () => {
	const [isRecording, setIsRecording] = useState(false)
	const [transcribedText, setTranscribedText] = useState('')

	const socket = useRef(null)

	const audioStreamRef = useRef(null)
	const mediaRecorderRef = useRef(null)

	const connectSocket = () => {
		console.log('Подключение к серверу...')
		socket.current = io(URL, {
			reconnectionAttempts: 5, // Количество попыток переподключения
			reconnectionDelay: 1000, // Задержка между попытками переподключения
		})

		console.log("Socket", socket.current)

		socket.current.on('connect', () => {
			console.log('Подключено к серверу')
		})

		socket.current.on('message', (data) => {
			setTranscribedText((prev) => prev + " " + data) // Добавление транскрибированного текста
		})

		socket.current.on('connect_error', (error) => {
			console.error('Ошибка подключения:', error)
		})

		socket.current.on('recognition_result', (data) => {
			setTranscribedText(prevText => prevText + data)
		})
	}

	const disconnectSocket = () => {
		if (socket.current) {
			socket.current.disconnect()
			console.log('Отключено от сервера')
			socket.current = null
		}
	}

	const stopRecording = async () => {
		if (mediaRecorderRef.current) {
			mediaRecorderRef.current.stop()
			disconnectSocket()
			setIsRecording(false)
		}
		audioStreamRef.current.getTracks().forEach(track => track.stop())
	}

	const startRecognition = () => {
		console.log("Staring recognition")
		socket.current.emit('recognition_start')
	}

	const sendChunk = (audioData) => {
		console.log("Sending bytes", audioData)
		socket.current.emit('recognition_chunk', audioData)
	}

	const startRecording = async () => {
		connectSocket()
		startRecognition()
		setIsRecording(true)
		audioStreamRef.current = await navigator.mediaDevices.getUserMedia({ audio: true })
		mediaRecorderRef.current = new MediaRecorder(audioStreamRef.current, { mimeType: 'audio/ogg;codecs=opus' })
		const chunks = []

		// Собираем чанк данных
		mediaRecorderRef.current.ondataavailable = e => {
			// console.log("Pushing chunk:", e.data)
			chunks.push(e.data)
			sendChunk(e.data)
		}

		// Обработка ошибок
		mediaRecorderRef.current.onerror = (error) => {
			console.error("Recording error:", error)
			setIsRecording(false)
		}

		// Запуск записи
		mediaRecorderRef.current.start(1000)
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
					disabled={isRecording}
					className="px-6 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-blue-300"
				>
					Start Recording
				</button>
				<button
					onClick={stopRecording}
					disabled={!isRecording}
					className="px-6 py-2 bg-red-500 text-white font-semibold rounded-lg hover:bg-red-700 disabled:bg-red-300"
				>
					Stop Recording
				</button>
			</div>

			<div className="mb-6">
				<h2 className="mark text-2xl font-semibold mb-3">Transcribed Text</h2>
				<div className="markdown-body border border-gray-300 rounded-lg p-4 prose prose-sm dark:prose-invert">
					<ReactMarkdown
						remarkPlugins={[remarkGfm]}
						children={transcribedText} />
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
