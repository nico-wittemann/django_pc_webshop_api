import { useCart } from '../context/CartContext';
import { useNavigate } from 'react-router-dom';

function Cart() {
  const {
    cartItems,
    removeFromCart,
    increaseQuantity,
    decreaseQuantity,
    clearCart,
    total,
  } = useCart();
    const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-[#0f172a] text-white px-4 py-12">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-4xl font-bold mb-10 text-center">Your Cart</h1>

        {cartItems.length === 0 ? (
          <p className="text-center text-gray-400">Your cart is empty 🛒</p>
        ) : (
          <>
            <div className="space-y-6">
              {cartItems.map((item) => (
                <div
                  key={`${item.id}-${item.type}`}
                  className="bg-[#1e293b] p-6 rounded-xl shadow flex flex-col md:flex-row justify-between gap-4 items-start md:items-center"
                >
                  <div className="flex-1">
                    <h2 className="text-lg font-semibold text-cyan-400 mb-2">{item.name}</h2>
                    <p className="text-sm text-gray-400">
                      <strong>Type:</strong> {item.type}
                      {item.manufacturer && (
                        <>
                          {' '}| <strong>Manufacturer:</strong> {item.manufacturer}
                        </>
                      )}
                    </p>
                    <p className="text-cyan-300 mt-2">
                      Price: € {parseFloat(item.price).toFixed(2)} × {item.quantity}
                    </p>
                    <p className="text-white font-bold">
                      Total: € {(item.quantity * parseFloat(item.price)).toFixed(2)}
                    </p>
                  </div>

                  <div className="flex flex-col gap-2 items-center">
                    <div className="flex gap-2">
                      <button
                        onClick={() => decreaseQuantity(item.id)}
                        className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded"
                      >
                        –
                      </button>
                      <span className="px-3 py-1 bg-gray-800 rounded text-white">{item.quantity}</span>
                      <button
                        onClick={() => increaseQuantity(item.id)}
                        className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded"
                      >
                        +
                      </button>
                    </div>
                    <button
                      onClick={() => removeFromCart(item.id)}
                      className="text-sm text-red-400 hover:underline mt-1"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Bottom row: total + buttons */}
            <div className="mt-12 flex flex-col md:flex-row justify-between items-center gap-4">
              {/* Left: Clear button */}
              <button
                onClick={clearCart}
                className="bg-red-500 hover:bg-red-400 text-white font-semibold px-6 py-2 rounded"
              >
                Clear Cart
              </button>

              {/* Right: Total + Buy Now */}
              <div className="text-right">
                <p className="text-xl font-semibold mb-4">
                  🧾 <span className="text-gray-400">Total:</span>{' '}
                  <span className="text-cyan-400">€ {total.toFixed(2)}</span>
                </p>

                <button
                  onClick={() => navigate('/checkout')}
                  className="bg-green-500 hover:bg-green-400 text-black font-bold px-6 py-2 rounded"
                >
                  Checkout
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default Cart;
