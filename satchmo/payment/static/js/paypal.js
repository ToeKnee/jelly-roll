document.addEventListener('readystatechange', () => {
  if (document.readyState === 'complete') {
    setupPayPal();
  }
});

const getValueForInput = name => {
  const form = document.getElementById('paypal-form');
  const inputs = form.getElementsByTagName('input');
  for (let i = 0; i < inputs.length; i++) {
    if (inputs[i].getAttribute('name') === name) {
      return inputs[i].value;
    }
  }
};

const setupPayPal = () => {
  paypal.Button.render(
    {
      env: getValueForInput('environment'),
      commit: true, // Show a 'Pay Now' button
      style: {
        size: 'medium', // tiny, small, medium
        shape: 'rect' // pill, rect
      },
      // Set up the payment:
      // 1. Add a payment callback
      payment: function(data, actions) {
        // 2. Make a request to your server
        return actions.request
          .post(getValueForInput('create-payment'))
          .then(function(res) {
            // 3. Return res.id from the response
            return res.id;
          });
      },
      // Execute the payment:
      // 1. Add an onAuthorize callback
      onAuthorize: function(data, actions) {
        // 2. Make a request to your server
        return actions.payment.get().then(function(paymentDetails) {
          const paymentData = {
            paymentID: paymentDetails.id,
            payerID: paymentDetails.payer.payer_info.payer_id
          };
          return actions.request
            .post(getValueForInput('execute-payment'), paymentData)
            .then(function(res) {
              // 3. Show the buyer a confirmation message.
              // Redirect to order history page
              window.location = res.url;
            });
        });
      },

      onError: function(error) {
        // Show an error page here, when an error occurs
        alert(
          'Something went wrong with your PayPal payment.\n\nPlease check your address and try again.\n\nIf the problem persists, please contact us.'
        );
        window.location.reload();
      }
    },
    '#paypal-button'
  );
};
