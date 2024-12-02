import React, { useState, useEffect, useRef } from 'react'
import { io } from 'socket.io-client'
import { MediaRecorder, register } from 'extendable-media-recorder'
import { connect } from 'extendable-media-recorder-wav-encoder';

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import 'github-markdown-css/github-markdown.css'

const URL = 'ws://localhost:7256'
await register(await connect());

const AudioRecorder = () => {
	const isRecording = useRef(false)
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
			setTranscribedText(prev => prev + data)
		})
	}

	const record_and_send = () => {
		mediaRecorderRef.current = new MediaRecorder(audioStreamRef.current, { mimeType: 'audio/webm' })
		const chunks = []
		// Собираем чанк данных
		mediaRecorderRef.current.ondataavailable = e => {
			console.log("Pushing chunk:", e.data)
			chunks.push(e.data)
		}
		mediaRecorderRef.current.onstop = e => {
			console.log("Sending chunks:", chunks)
			sendAudio(new Blob(chunks))
		}
		// Обработка ошибок
		// mediaRecorderRef.current.onerror = (error) => {
		// 	console.error("Recording error:", error)
		// 	isRecording.current = false
		// }
		// Запуск записи
		mediaRecorderRef.current.start()
		// Останавливаем запись через 1 секунду
		setTimeout(() => {
			mediaRecorderRef.current.stop()
			if (isRecording.current) {
				console.log("Next recording")
				record_and_send()
			}
		}, 5000)
	}

	const disconnectSocket = () => {
		if (socket.current) {
			socket.current.disconnect()
			console.log('Отключено от сервера')
			socket.current = null
		}
	}

	const stopRecording = async () => {
		audioStreamRef.current.getTracks().forEach(track => track.stop())
		if (mediaRecorderRef.current) {
			mediaRecorderRef.current.stop()
			isRecording.current = false
			disconnectSocket()
		}
	}

	const startRecognition = () => {
		console.log("Staring recognition")
		socket.current.emit('recognition_start')
	}

	const sendAudio = (audioData) => {
		console.log("Sending bytes", audioData)
		if (socket.current)
			socket.current.emit('recognition', audioData)
	}

	const startRecording = async () => {
		audioStreamRef.current = await navigator.mediaDevices.getUserMedia({ audio: true })
		connectSocket()
		startRecognition()
		isRecording.current = true
		record_and_send()
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
					className="px-6 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-blue-300"
				>
					Start Recording
				</button>
				<button
					onClick={stopRecording}
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
