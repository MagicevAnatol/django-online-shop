var mix = {
  methods: {
      submitPaymentSomeone() {
          const generatedNumber = document.getElementById('numero1').value.trim()
          const urlParams = new URLSearchParams(window.location.search);
          const orderId = urlParams.get('orderId');
          this.postData(`/api/payment-someone/`, {
              number: generatedNumber,
              orderId: orderId
          }).then(() => {
              alert('Успешная оплата')
              this.numero1 = ''
              location.assign('/')
          }).catch(() => {
              console.warn('Ошибка при оплате')
          })

    },
  },
}