import React, { useEffect } from 'react';
import axios from 'axios';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { WebSocketProvider } from './contexts/WebSocketContext';
import { Toaster } from 'react-hot-toast';
import { CartProvider } from './contexts/CartContext';
import { SpeedInsights } from '@vercel/speed-insights/react';

import ClientRoutes from './routes/ClientRoutes';
import RestaurantRoutes from './routes/RestaurantRoutes';
import RiderRoutes from './routes/RiderRoutes';
import AdminRoutes from './routes/AdminRoutes';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import RestaurantLogin from './pages/auth/RestaurantLogin';
// import RestaurantSignup from './pages/auth/RestaurantSignup'; // DISABLED: Only admin can add restaurants
import RiderLogin from './pages/rider/RiderLogin';
import AdminLogin from './pages/admin/AdminLogin';

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
            console.log(`Backend connection failed. Retrying in 2s... (Attempt ${config.__retryCount}/3)`);

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
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/restaurant/login" element={<RestaurantLogin />} />
              {/* <Route path="/restaurant/signup" element={<RestaurantSignup />} /> */}
              {/* DISABLED: Restaurant signup removed - only admin can add restaurants */}
              <Route path="/rider/login" element={<RiderLogin />} />
              <Route path="/admin/login" element={<AdminLogin />} />
              <Route path="/client/*" element={<ClientRoutes />} />
              <Route path="/restaurant/*" element={<RestaurantRoutes />} />
              <Route path="/rider/*" element={<RiderRoutes />} />
              <Route path="/admin/*" element={<AdminRoutes />} />

              {/* Specialized Full Screen Routes */}
              <Route path="/payment-success/:orderId" element={
                <React.Suspense fallback={<div className="h-screen bg-[#19a463]" />}>
                  {React.createElement(React.lazy(() => import('./components/PaymentSuccessScreen')))}
                </React.Suspense>
              } />

              <Route path="/" element={<Navigate to="/client" replace />} />
            </Routes>
          </CartProvider>
        </WebSocketProvider>
        <SpeedInsights />
      </AuthProvider>
    </Router>
  );
}

export default App;
