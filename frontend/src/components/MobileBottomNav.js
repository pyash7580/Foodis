import React from 'react';
import { NavLink } from 'react-router-dom';
import { FaHome, FaSearch, FaShoppingCart, FaClipboardList, FaUserAlt } from 'react-icons/fa';
import { useCart } from '../contexts/CartContext';

const MobileBottomNav = () => {
    const { getCartCount } = useCart();
    const cartCount = getCartCount();

    const navItems = [
        { path: '/client', icon: FaHome, label: 'Home', exact: true },
        { path: '/client/search', icon: FaSearch, label: 'Browse' },
        { path: '/client/cart', icon: FaShoppingCart, label: 'Cart', showBadge: true },
        { path: '/client/orders', icon: FaClipboardList, label: 'Orders' },
        { path: '/client/profile', icon: FaUserAlt, label: 'Profile' }
    ];

    return (
        <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 z-50 pt-2 pb-3 px-4 shadow-[0_-4px_20px_-10px_rgba(0,0,0,0.1)]">
            <nav className="flex items-center justify-between safe-area-pb">
                {navItems.map((item) => (
                    <NavLink
                        key={item.label}
                        to={item.path}
                        end={item.exact}
                        className={({ isActive }) => `
                            flex flex-col items-center justify-center w-16 relative
                            transition-colors duration-200 ease-in-out
                            ${isActive ? 'text-red-500' : 'text-gray-400 hover:text-gray-500'}
                        `}
                    >
                        {({ isActive }) => (
                            <>
                                <div className={`relative mb-1 transition-transform duration-200 ${isActive ? 'scale-110' : 'scale-100'}`}>
                                    <item.icon className="text-xl" />
                                    {item.showBadge && cartCount > 0 && (
                                        <span className="absolute -top-2 -right-2 bg-red-500 text-white text-[10px] font-black h-4 min-w-[16px] flex items-center justify-center rounded-full px-1 border-2 border-white ring-0">
                                            {cartCount}
                                        </span>
                                    )}
                                </div>
                                <span className={`text-[10px] font-bold tracking-tight ${isActive ? 'opacity-100' : 'opacity-80'}`}>
                                    {item.label}
                                </span>
                            </>
                        )}
                    </NavLink>
                ))}
            </nav>
        </div>
    );
};

export default MobileBottomNav;
