import React, { useState, useEffect, useRef } from "react"
import { io } from "socket.io-client"
import { MediaRecorder, register } from "extendable-media-recorder"
import { connect } from "extendable-media-recorder-wav-encoder"

import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import "github-markdown-css/github-markdown.css"
import { Button, FileInput, Modal, Label } from 'flowbite-react'

const URL = "ws://localhost:7256"
await register(await connect())

const AudioRecorder = () => {
	const [isRecording, setIsRecording] = useState(false)
	const [isHandlingFile, setIsHandlingFile] = useState(false)
	const [transcribedText, setTranscribedText] = useState("")
	const socket = useRef(null)
	const audioStreamRef = useRef(null)
	const mediaRecorderRef = useRef(null)

	const connectSocket = () => {
		console.log("Подключение к серверу...")
		socket.current = io(URL, {
			reconnectionAttempts: 5,
			reconnectionDelay: 1000,
			pingInterval: 25000, // Интервал пинга
			pingTimeout: 60000, // Тайм-аут на пинг
		})

		console.log("Socket", socket.current)

		socket.current.on("connect", () => {
			console.log("Подключено к серверу")
		})

		socket.current.on("message", (data) => {
			setTranscribedText((prev) => prev + " " + data)
		})

		socket.current.on("disconnect", () => {
			setIsRecording(false)
			setIsHandlingFile(false)
		})

		socket.current.on("connect_error", (error) => {
			console.error("Ошибка подключения:", error)
		})

		socket.current.on("recognition_result", (data) => {
			setTranscribedText((prev) => prev + data)
		})
	}

	const initConnection = () => {
		console.log("Init connection")
		connectSocket()
		socket.current.emit("receive_start")
	}

	const sendChunk = (audioData) => {
		console.log("Sending bytes", audioData)
		socket.current.emit("audio_chunk", audioData)
	}

	const record_and_send = () => {
		mediaRecorderRef.current = new MediaRecorder(audioStreamRef.current, {
			mimeType: "audio/webm",
		})
		const chunks = []
		mediaRecorderRef.current.ondataavailable = (e) => {
			console.log("Pushing chunk:", e.data)
			sendChunk(new Blob([e.data]))
			chunks.push(e.data)
		}
		mediaRecorderRef.current.onstop = (e) => {
			socket.current.emit("receive_end") // Сообщить о завершении
		}
		mediaRecorderRef.current.start()
	}

	const stopRecording = async () => {
		audioStreamRef.current.getTracks().forEach((track) => track.stop())
		if (mediaRecorderRef.current) {
			mediaRecorderRef.current.stop()
		}
	}

	const startRecording = async () => {
		audioStreamRef.current = await navigator.mediaDevices.getUserMedia({
			audio: true,
		})
		initConnection()
		setIsRecording(true)
		record_and_send()
	}

	const clearText = () => {
		setTranscribedText("")
	}

	const downloadText = () => {
		const blob = new Blob([transcribedText], { type: "text/plain" })
		const url = window.URL.createObjectURL(blob)
		const a = document.createElement("a")
		a.href = url
		a.download = "transcription.md"
		a.click()
	}

	const handleFileUpload = (event) => {
		const CHUNK_SIZE = 64 * 1024 // Размер чанка (64 КБ)

		const file = event.target.files[0]
		if (!file) return
		initConnection()
		setIsHandlingFile(true)

		let offset = 0

		const readChunk = () => {
			if (offset >= file.size) {
				socket.current.emit("receive_end") // Сообщить о завершении
				console.log("File upload complete")
				return
			}

			const chunk = file.slice(offset, offset + CHUNK_SIZE) // Вырезаем чанк
			const reader = new FileReader()

			reader.onload = (e) => {
				sendChunk(new Blob([e.target.result], { type: file.type }))
				offset += CHUNK_SIZE
				readChunk() // Считать следующий чанк
			}

			reader.readAsArrayBuffer(chunk) // Читаем чанк как ArrayBuffer
		}
		readChunk()
	}

	return (
		<div className="max-w-4xl mx-auto p-6">
			<h1 className="text-3xl font-bold text-center mb-6">
				Audio Recorder & Transcription
			</h1>
			<div className="flex justify-center gap-4 mb-6">
				<Button
					onClick={startRecording}
					disabled={isRecording || isHandlingFile}
					className="w-full sm:w-auto"
				>
					Start Recording
				</Button>
				<Button
					onClick={stopRecording}
					disabled={!isRecording || isHandlingFile}
					className="w-full sm:w-auto"
				>
					Stop Recording
				</Button>
			</div>

			<div>
				<div className="mb-2 block">
					<Label htmlFor="file-upload" value="Audio files" />
				</div>
				<FileInput
					type="file"
					disabled={isRecording || isHandlingFile}
					accept="audio/*"
					onChange={handleFileUpload}
					className="mb-4"
				/>
			</div>

			<div className="mb-6">
				<div className='flex items-center justify-center mb-3 w-full'>
					<h2 className="text-2xl font-semibold">Transcribed Text</h2>
					<div class="ml-3 w-5 h-5 border-4 border-t-transparent border-gray-700 border-solid rounded-full animate-spin" hidden={!isRecording &&!isHandlingFile}></div>
				</div>
				<div className="markdown-body border border-gray-300 rounded-lg p-4 prose prose-sm dark:prose-invert">
					<ReactMarkdown remarkPlugins={[remarkGfm]} children={transcribedText} />
				</div>
			</div>

			<div className="flex justify-center gap-4">
				<Button
					onClick={clearText}
					disabled={isRecording || isHandlingFile}
					className="w-full sm:w-auto"
				>
					Clear Text
				</Button>
				<Button
					onClick={downloadText}
					disabled={isRecording || isHandlingFile}
					className="w-full sm:w-auto"
				>
					Download Text
				</Button>
			</div>
		</div>
	)
}

export default AudioRecorder
