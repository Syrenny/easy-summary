import React, { useEffect, useRef } from 'react'

const URL = 'ws://localhost:7256/easy-summary/recognize'

const useWebSocket = (onMessage) => {
	const socketRef = useRef(null) // Хранит ссылку на WebSocket
	const reconnectIntervalRef = useRef(1000) // Начальный интервал для переподключения
	const maxReconnectIntervalRef = useRef(30000) // Максимальный интервал переподключения
	const reconnectAttemptsRef = useRef(0) // Счетчик попыток переподключения

	const connect = () => {
		console.log('Подключение к WebSocket...')
		socketRef.current = new WebSocket(URL)

		socketRef.current.onopen = () => {
			console.log('Подключено к серверу')
			reconnectAttemptsRef.current = 0 // Сброс счетчика попыток
			reconnectIntervalRef.current = 1000 // Сброс интервала
		}

		socketRef.current.onerror = (error) => {
			console.error('Ошибка WebSocket:', error)
		}

		socketRef.current.onclose = () => {
			console.log('Соединение закрыто. Попытка переподключения...')
			reconnectAttemptsRef.current++
			reconnectIntervalRef.current = Math.min(
				maxReconnectIntervalRef.current,
				reconnectIntervalRef.current * 2
			) // Увеличиваем интервал

			setTimeout(connect, reconnectIntervalRef.current) // Запускаем попытку переподключения
		}

		socketRef.current.onmessage = onMessage
	}

	useEffect(() => {
		connect() // Запускаем подключение при монтировании компонента

		return () => {
			if (socketRef.current) {
				socketRef.current.close() // Закрываем WebSocket при размонтировании
				socketRef.current = null
			}
		}
	}, []) // Пустой массив зависимостей, чтобы подключение произошло только один раз

	return socketRef
}

export default useWebSocket