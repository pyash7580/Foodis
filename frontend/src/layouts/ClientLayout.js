import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from '../components/Navbar';
import MobileBottomNav from '../components/MobileBottomNav';

const ClientLayout = () => {
    return (
        <div className="min-h-screen bg-gray-50 flex flex-col relative">
            {/* Desktop Navbar - Hidden on Mobile */}
            <div className="hidden md:block">
                <Navbar />
            </div>

            {/* Main Content Area */}
            <main className="flex-1 w-full pb-16 md:pb-0 safe-area-style">
                <Outlet />
            </main>

            {/* Mobile Bottom Navigation - Hidden on Desktop */}
            <MobileBottomNav />
        </div>
    );
};

export default ClientLayout;
