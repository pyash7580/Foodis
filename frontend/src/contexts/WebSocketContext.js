
import React, { createContext, useContext } from 'react';

const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
    const sendMessage = (msg) => console.log('WebSocket msg:', msg);

    return (
        <WebSocketContext.Provider value={{ sendMessage }}>
            {children}
        </WebSocketContext.Provider>
    );
};

export const useWebSocket = () => useContext(WebSocketContext);
