import React from 'react';
import { motion } from 'framer-motion';

const DashboardStatCard = ({ title, value, icon: Icon, color, trend, index }) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="glass-card p-6 rounded-3xl relative overflow-hidden group border border-white/5"
        >
            <div className={`absolute top-0 right-0 w-24 h-24 bg-${color}-500/10 rounded-full blur-3xl -mr-12 -mt-12 group-hover:bg-${color}-500/20 transition-all duration-500`}></div>
            <div className="relative z-10">
                <div className="flex items-center justify-between mb-4">
                    <div className={`p-3 bg-${color}-500/20 rounded-2xl text-${color}-400`}>
                        <Icon className="text-xl" />
                    </div>
                    {trend && (
                        <span className={`text-[9px] font-black text-${color}-400 bg-${color}-400/10 px-2 py-1 rounded-full uppercase tracking-tighter`}>
                            {trend}
                        </span>
                    )}
                </div>
                <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest mb-1">{title}</p>
                <h3 className="text-3xl font-black text-white">{value}</h3>
            </div>
        </motion.div>
    );
};

export default DashboardStatCard;
