var mix = {
	methods: {
		submitPayment() {
			const orderId = location.pathname.startsWith('/payment/')
				? Number(location.pathname.replace('/payment/', '').replace('/', ''))
				: null
			console.log({
				name: this.name,
				number: this.number1,
				year: this.year,
				month: this.month,
				code: this.code,
			})
			let url = `/api/order/${orderId}`;
			const paymentParam = this.getParameterByName('payment');
			if (paymentParam) {
				url += `?payment=${paymentParam}`;
			}

			this.postData(url, {
				name: this.name,
				number: this.number1,
				year: this.year,
				month: this.month,
				code: this.code
			}).then(() => {
				alert('Успешная оплата')
				this.number1 = ''
				this.name = ''
				this.year = ''
				this.month = ''
				this.code = ''
				location.assign('/')
			}).catch(() => {
			 	console.warn('Ошибка при оплате')
			})
		}
	},
	data() {
		return {
			number1: '',
			month: '',
			year: '',
			name: '',
			code: ''
		}
	}
}