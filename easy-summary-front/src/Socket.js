import React from 'react'

const URL = 'ws://localhost:7256/easy-summary/recognize'

class WebSocketManager extends React.Component {
	constructor(props) {
		super(props)
		this.socket = null
		this.reconnectIntervalRef = 1000 // Начальный интервал для переподключения
		this.maxReconnectIntervalRef = 30000 // Максимальный интервал переподключения
		this.reconnectAttemptsRef = 0 // Счетчик попыток переподключения
		this.isConnected = false // Флаг для контроля состояния подключения
	}

	// Метод для подключения к WebSocket
	connect = () => {
		if (this.isConnected) return // Если соединение уже установлено, не подключаемся снова

		console.log('Подключение к WebSocket...')
		this.socket = new WebSocket(URL)

		this.socket.onopen = () => {
			console.log('Подключено к серверу')
			this.isConnected = true // Устанавливаем флаг подключения
			this.reconnectAttemptsRef = 0 // Сброс счетчика попыток
			this.reconnectIntervalRef = 1000 // Сброс интервала
		}

		if (this.props.onMessage) {
			this.socket.onmessage = this.props.onmessage
		}

		this.socket.onerror = (error) => {
			console.error('Ошибка WebSocket:', error)
		}

		this.socket.onclose = () => {
			console.log('Соединение закрыто. Попытка переподключения...')
			this.isConnected = false // Обновляем флаг на не подключено
			this.reconnectAttemptsRef++
			this.reconnectIntervalRef = Math.min(
				this.maxReconnectIntervalRef,
				this.reconnectIntervalRef * 2
			) // Увеличиваем интервал

			setTimeout(this.connect, this.reconnectIntervalRef) // Запускаем попытку переподключения
		}
	};

	// Метод для остановки соединения
	stopConnection = () => {
		if (this.socket) {
			this.socket.close()
			this.isConnected = false // Устанавливаем флаг на отключено
			console.log('Соединение закрыто вручную')
		}
	};

	// Метод для старта соединения
	startConnection = () => {
		if (!this.isConnected) {
			this.connect() // Если нет активного соединения, подключаемся
		}
	};

	// Метод жизненного цикла componentDidMount
	componentDidMount() {
		// Здесь можно подключиться сразу или по требованию
		// this.startConnection() // Включаем подключение при монтировании компонента
	}

	// Метод жизненного цикла componentWillUnmount
	componentWillUnmount() {
		this.stopConnection() // Останавливаем соединение при размонтировании компонента
	}

	// Метод для получения доступа к WebSocket
	getSocket = () => {
		return this.socket
	};

	render() {
		// Компонент не рендерит ничего
		return null
	}
}

export default WebSocketManager
