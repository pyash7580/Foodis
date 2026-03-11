import React, { Suspense, useEffect } from 'react';
import { SpeedInsights } from '@vercel/speed-insights/react';
import axios from 'axios';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { WebSocketProvider } from './contexts/WebSocketContext';
import { Toaster } from 'react-hot-toast';
import { CartProvider } from './contexts/CartContext';

// Eagerly load auth pages (always needed on cold start)
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import RestaurantLogin from './pages/auth/RestaurantLogin';
import RiderLogin from './pages/rider/RiderLogin';
import AdminLogin from './pages/admin/AdminLogin';

// Lazy-load entire role-based route trees — each role only loads its own bundle
const ClientRoutes = React.lazy(() => import('./routes/ClientRoutes'));
const RestaurantRoutes = React.lazy(() => import('./routes/RestaurantRoutes'));
const RiderRoutes = React.lazy(() => import('./routes/RiderRoutes'));
const AdminRoutes = React.lazy(() => import('./routes/AdminRoutes'));
const PaymentSuccessScreen = React.lazy(() => import('./components/PaymentSuccessScreen'));

const PageLoader = () => (
  <div className="h-screen flex items-center justify-center bg-gray-50">
    <div className="w-12 h-12 border-4 border-red-600 border-t-transparent rounded-full animate-spin" />
  </div>
);

function App() {
  useEffect(() => {
    const retryInterceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const { config, message } = error;

        // If it's a network error (no response) and we haven't retried too many times
        if (!error.response && message === 'Network Error') {
          config.__retryCount = config.__retryCount || 0;

          if (config.__retryCount < 3) {
            config.__retryCount += 1;
            // Wait for 2 seconds before retrying
            await new Promise(resolve => setTimeout(resolve, 2000));
            return axios(config);
          }
        }
        return Promise.reject(error);
      }
    );

    return () => axios.interceptors.response.eject(retryInterceptor);
  }, []);

  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <Toaster position="top-center" reverseOrder={false} />
        <WebSocketProvider>
          <CartProvider>
            <Suspense fallback={<PageLoader />}>
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/restaurant/login" element={<RestaurantLogin />} />
                <Route path="/rider/login" element={<RiderLogin />} />
                <Route path="/admin/login" element={<AdminLogin />} />
                <Route path="/client/*" element={<ClientRoutes />} />
                <Route path="/restaurant/*" element={<RestaurantRoutes />} />
                <Route path="/rider/*" element={<RiderRoutes />} />
                <Route path="/admin/*" element={<AdminRoutes />} />

                {/* Specialized Full Screen Routes */}
                <Route path="/payment-success/:orderId" element={<PaymentSuccessScreen />} />

                <Route path="/" element={<Navigate to="/client" replace />} />
              </Routes>
            </Suspense>
          </CartProvider>
        </WebSocketProvider>
        <SpeedInsights />
      </AuthProvider>
    </Router>
  );
}

export default App;
