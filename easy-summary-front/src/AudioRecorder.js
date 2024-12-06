import React, { useState, useEffect, useRef } from "react"
import { io } from "socket.io-client"

import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import "github-markdown-css/github-markdown.css"
import { Button, FileInput, Modal, Label } from 'flowbite-react'
import { FaMicrophone, FaStop, FaTrashAlt, FaDownload } from 'react-icons/fa'

const URL = "ws://localhost:7256"

const AudioRecorder = () => {
	const [disableElement, setDisableElement] = useState({
		start: false,
		stop: true,
		file: false,
		clear: false,
		download: false,
		loading: true
	})
	const [transcribedText, setTranscribedText] = useState("")
	const socket = useRef(null)
	const audioStreamRef = useRef(null)
	const mediaRecorderRef = useRef(null)
	const fileInputRef = useRef(null)

	const connectSocket = () => {
		console.log("Подключение к серверу...")
		socket.current = io(URL, {
			reconnectionAttempts: 5,
			reconnectionDelay: 1000,
			pingInterval: 25000, // Интервал пинга
			pingTimeout: 120000, // Тайм-аут на пинг
		})

		console.log("Socket", socket.current)

		socket.current.on("connect", () => {
			console.log("Подключено к серверу")
		})

		socket.current.on("message", (data) => {
			setTranscribedText((prev) => prev + " " + data)
		})

		socket.current.on("disconnect", () => {
			setDisableElement({
				start: false,
				stop: true,
				file: false,
				clear: false,
				download: false,
				loading: true
			})
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
		setDisableElement({
			start: true,
			stop: true,
			file: true,
			clear: false,
			download: false,
			loading: false
		})
		audioStreamRef.current.getTracks().forEach((track) => track.stop())
		if (mediaRecorderRef.current) {
			mediaRecorderRef.current.stop()
		}
	}

	const startRecording = async () => {
		setDisableElement({
			start: true,
			stop: false,
			file: true,
			clear: false,
			download: false,
			loading: true
		})
		audioStreamRef.current = await navigator.mediaDevices.getUserMedia({
			audio: true,
		})
		initConnection()
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
		setDisableElement({
			start: true,
			stop: true,
			file: true,
			clear: false,
			download: false,
			loading: false
		})
		const CHUNK_SIZE = 64 * 1024 // Размер чанка (64 КБ)

		const file = event.target.files[0]
		if (!file) return
		initConnection()

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
			<h1 className="text-2xl font-bold text-center mb-6">
				Audio Recorder & Transcription
			</h1>
			<div className="flex justify-center gap-4 mb-6">
				<Button
					outline
					gradientDuoTone="redToYellow"
					onClick={startRecording}
					disabled={disableElement.start}
					className="w-full sm:w-auto focus:ring-0"
				>
					<div className='w-full h-full flex items-center'>
						<FaMicrophone className="mr-3 h-4 w-4" />
						Start Recording
					</div>
				</Button>
				<Button
					outline
					color="gray"
					onClick={stopRecording}
					disabled={disableElement.stop}
					className="w-full sm:w-auto focus:ring-0 border-gray-300"
				>
					<div className='w-full h-full flex items-center'>
						<FaStop className="mr-3 h-4 w-4" />
						Stop Recording
					</div>
				</Button>
			</div>

			<div>
				<div className="mb-2 block">
					<Label htmlFor="file-upload" value="Audio file" />
				</div>
				<FileInput
					ref={fileInputRef.current}
					type="file"
					disabled={disableElement.file}
					accept="audio/*"
					onChange={handleFileUpload}
					className="mb-4"
				/>
			</div>

			<div className='flex h-[30px] items-center justify-center w-full'>
				<div className="ml-3 w-5 h-5 border-4 border-t-transparent border-gray-700 border-solid rounded-full animate-spin" hidden={disableElement.loading}></div>
				<div hidden={disableElement.loading} className='ml-3 text-sm italic'>
					Обрабатываю текст...
				</div>
				<div className="flex ml-auto justify-center gap-4">
					<Button
						outline
						size="xs"
						color="gray"
						onClick={downloadText}
						disabled={disableElement.download}
						className="sm:w-auto border-gray-300 focus:ring-0 rounded-b-none border-b-0"
					>
						<div className='w-full h-full flex items-center'>
							<FaDownload className="mr-2 h-3 w-3" />
							Download
						</div>
					</Button>
					<Button
						outline
						size="xs"
						color="gray"
						onClick={clearText}
						disabled={disableElement.clear}
						className="h-full w-full sm:w-auto border-gray-300 focus:ring-0 rounded-b-none border-b-0"
					>
						<div className='w-full h-full flex items-center'>
							<FaTrashAlt className="mr-2 h-3 w-3" />
							Clear Text
						</div>
					</Button>
				</div>
			</div>

			<div className="mb-6">
				<div className="markdown-body border border-gray-300 rounded-lg rounded-tr-none p-4 prose prose-sm dark:prose-invert">
					<ReactMarkdown remarkPlugins={[remarkGfm]} children={transcribedText} />
				</div>
			</div>

		</div>
	)
}

export default AudioRecorder
