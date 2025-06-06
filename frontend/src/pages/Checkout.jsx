import { useState } from 'react';
import { useCart } from '../context/CartContext';

function Checkout() {
  const { cartItems, total, clearCart } = useCart();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [iban, setIban] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [paymentInfo, setPaymentInfo] = useState(null); // 👈 NEU

  const handlePayment = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setPaymentInfo(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/pay/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`  // 👈 NEU!
  },
  body: JSON.stringify({
    name,
    email,
    iban,
    items: cartItems,
    total,
  }),
});


      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Payment failed');
      }

      setMessage('✅ Payment initiated successfully!');
      setPaymentInfo(data);         // 👈 Zeigt Details im UI an
      clearCart();
    } catch (err) {
      setMessage(`❌ ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-white px-4 py-12">
      <div className="max-w-xl mx-auto bg-[#1e293b] p-8 rounded-xl shadow space-y-6">
        <h1 className="text-3xl font-bold text-cyan-400 text-center">Checkout</h1>

        <form onSubmit={handlePayment} className="space-y-4">
          <input
            type="text"
            placeholder="Name"
            className="w-full p-3 bg-[#0f172a] border border-gray-700 rounded"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <input
            type="email"
            placeholder="Email"
            className="w-full p-3 bg-[#0f172a] border border-gray-700 rounded"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="IBAN"
            className="w-full p-3 bg-[#0f172a] border border-gray-700 rounded"
            value={iban}
            onChange={(e) => setIban(e.target.value)}
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-green-500 hover:bg-green-400 text-black font-bold rounded"
          >
            {loading ? 'Processing...' : `Pay € ${total.toFixed(2)}`}
          </button>
        </form>

        {message && (
          <p className={`text-center font-medium ${message.startsWith('✅') ? 'text-green-400' : 'text-red-400'}`}>
            {message}
          </p>
        )}

        {/* ✅ Anzeige von Order-Daten bei Erfolg */}
        {paymentInfo && (
          <div className="mt-6 bg-[#0f172a] border border-cyan-700 rounded-lg p-4 space-y-2 text-sm">
            <p><span className="text-gray-400">Order ID:</span> <span className="text-white">{paymentInfo.order_id}</span></p>
            <p><span className="text-gray-400">Payment Intent:</span> <span className="text-white">{paymentInfo.payment_intent}</span></p>
            <p><span className="text-gray-400">Status:</span> <span className="text-white">{paymentInfo.status}</span></p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Checkout;