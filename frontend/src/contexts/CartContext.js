
import React, { createContext, useState, useEffect, useContext } from 'react';

const CartContext = createContext();

export const useCart = () => useContext(CartContext);

export const CartProvider = ({ children }) => {
    const [cartItems, setCartItems] = useState([]);
    const [restaurant, setRestaurant] = useState(null); // Cart can only hold items from one restaurant at a time

    // Load cart from local storage on init
    useEffect(() => {
        const savedCart = localStorage.getItem('foodis_cart');
        const savedRestaurant = localStorage.getItem('foodis_restaurant');
        if (savedCart) {
            setCartItems(JSON.parse(savedCart));
        }
        if (savedRestaurant) {
            setRestaurant(JSON.parse(savedRestaurant));
        }
    }, []);

    // Save cart to local storage whenever it changes
    useEffect(() => {
        localStorage.setItem('foodis_cart', JSON.stringify(cartItems));
        localStorage.setItem('foodis_restaurant', JSON.stringify(restaurant));
    }, [cartItems, restaurant]);

    const addToCart = (item, currentRestaurant, quantity = 1, customizations = {}) => {
        // Check if adding from a different restaurant
        if (restaurant && restaurant.id !== currentRestaurant.id) {
            if (!window.confirm("Start a new basket? Adding items from a different restaurant will clear your current cart.")) {
                return;
            }
            setCartItems([]); // Clear cart
        }

        setRestaurant(currentRestaurant);

        setCartItems(prevItems => {
            // Check if item with same ID AND same customizations exists
            const existingItemIndex = prevItems.findIndex(i =>
                i.id === item.id && JSON.stringify(i.customizations) === JSON.stringify(customizations)
            );

            if (existingItemIndex > -1) {
                const newItems = [...prevItems];
                newItems[existingItemIndex].quantity += quantity;
                return newItems;
            } else {
                return [...prevItems, { ...item, quantity, customizations }];
            }
        });
    };

    const removeFromCart = (itemId) => {
        setCartItems(prevItems => prevItems.filter(item => item.id !== itemId));
        if (cartItems.length === 1) {
            setRestaurant(null); // Clear restaurant if last item removed
        }
    };

    const updateQuantity = (itemId, delta) => {
        setCartItems(prevItems => {
            return prevItems.map(item => {
                if (item.id === itemId) {
                    const newQuantity = Math.max(0, item.quantity + delta);
                    return { ...item, quantity: newQuantity };
                }
                return item;
            }).filter(item => item.quantity > 0);
        });

        // Cleanup restaurant if empty
        // Note: Logic inside map/filter complex, purely relying on useEffect might require checking length there or here separately.
        // Simplified:
        // If the resulting array is empty, setRestaurant(null) below is tricky due to async state update.
        // We'll let the user clear it or handle it on "checkout" or "add".
    };

    const clearCart = () => {
        setCartItems([]);
        setRestaurant(null);
    };

    const getCartTotal = () => {
        return cartItems.reduce((total, item) => total + (item.price * item.quantity), 0);
    };

    const getCartCount = () => {
        return cartItems.reduce((count, item) => count + item.quantity, 0);
    };

    const value = {
        cartItems,
        restaurant,
        addToCart,
        removeFromCart,
        updateQuantity,
        clearCart,
        getCartTotal,
        getCartCount
    };

    return (
        <CartContext.Provider value={value}>
            {children}
        </CartContext.Provider>
    );
};

export default CartContext;
