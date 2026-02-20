
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../config';
import {
    FaUsers, FaStore, FaMotorcycle, FaBox, FaMoneyBillWave, FaChartLine
} from 'react-icons/fa';
import { Line, Bar } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    Title,
    Tooltip,
    Legend
);

const StatCard = ({ title, value, subtext, icon, color }) => (
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center hover:shadow-md transition">
        <div className={`w-16 h-16 rounded-full flex items-center justify-center text-white text-2xl mr-4 ${color}`}>
            {icon}
        </div>
        <div>
            <p className="text-gray-500 text-sm font-bold uppercase tracking-wide">{title}</p>
            <h3 className="text-3xl font-black text-gray-800">{value}</h3>
            {subtext && <p className="text-xs text-gray-400 mt-1">{subtext}</p>}
        </div>
    </div>
);

const AdminDashboard = () => {
    const [stats, setStats] = useState(null);
    const [graphData, setGraphData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const token = localStorage.getItem('token_admin');
                const headers = { Authorization: `Bearer ${token}`, 'X-Role': 'ADMIN' };

                // Fetch Stats
                const statsRes = await axios.get(`${API_BASE_URL}/api/admin/dashboard/stats/`, { headers });
                setStats(statsRes.data);

                // Fetch Graph Data
                const graphRes = await axios.get(`${API_BASE_URL}/api/admin/dashboard/revenue-graph/?days=7`, { headers });
                setGraphData(graphRes.data);

            } catch (error) {
                console.error("Dashboard data fetch failed", error.response?.data || error.message);
                setStats(null);
            } finally {
                setLoading(false);
            }
        };
        fetchDashboardData();
    }, []);

    if (loading) return <div className="p-10 font-bold text-gray-500">Loading Dashboard...</div>;
    if (!stats) return (
        <div className="p-10 text-center">
            <div className="text-red-500 font-bold text-xl mb-2">Failed to load statistics</div>
            <p className="text-gray-400 text-sm">Check console for details or ensure you are logged in as Admin.</p>
            <button
                onClick={() => window.location.reload()}
                className="mt-4 px-4 py-2 bg-red-500 text-white rounded-lg text-sm"
            >
                Retry
            </button>
        </div>
    );

    return (
        <div className="space-y-8">
            {/* Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="Total Revenue"
                    value={`₹${stats.revenue?.total?.toLocaleString() || 0}`}
                    subtext={`Today: ₹${stats.revenue?.today?.toLocaleString()}`}
                    icon={<FaMoneyBillWave />}
                    color="bg-green-500"
                />
                <StatCard
                    title="Total Orders"
                    value={stats.orders?.total}
                    subtext={`Pending: ${stats.orders?.today} Today`}
                    icon={<FaBox />}
                    color="bg-purple-500"
                />
                <StatCard
                    title="Active Users"
                    value={stats.users?.total}
                    subtext={`${stats.users?.clients} Clients`}
                    icon={<FaUsers />}
                    color="bg-blue-500"
                />
                <StatCard
                    title="Restaurants"
                    value={stats.restaurants?.approved}
                    subtext={`${stats.restaurants?.pending} Pending Approval`}
                    icon={<FaStore />}
                    color="bg-orange-500"
                />
            </div>

            {/* Quick Actions / Second Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 col-span-1 lg:col-span-2">
                    <h3 className="text-xl font-bold mb-4 flex items-center">
                        <FaChartLine className="mr-2 text-red-500" /> Revenue Trend (Last 7 Days)
                    </h3>
                    <div className="h-64 bg-gray-50 rounded-lg p-2">
                        {graphData && graphData.daily_data ? (
                            <Line
                                data={{
                                    labels: graphData.daily_data.map(d => d.date),
                                    datasets: [{
                                        label: 'Revenue (₹)',
                                        data: graphData.daily_data.map(d => d.revenue),
                                        fill: true,
                                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                                        borderColor: 'rgb(239, 68, 68)',
                                        tension: 0.4,
                                        pointRadius: 4,
                                        pointBackgroundColor: 'rgb(239, 68, 68)'
                                    }]
                                }}
                                options={{
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    plugins: {
                                        legend: { display: false },
                                        tooltip: {
                                            mode: 'index',
                                            intersect: false,
                                        }
                                    },
                                    scales: {
                                        y: {
                                            beginAtZero: true,
                                            grid: { color: 'rgba(0,0,0,0.05)' }
                                        },
                                        x: {
                                            grid: { display: false }
                                        }
                                    }
                                }}
                            />
                        ) : (
                            <div className="h-full flex items-center justify-center text-gray-400">
                                <p>No growth data available yet</p>
                            </div>
                        )}
                    </div>
                </div>

                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <h3 className="text-xl font-bold mb-4">Urgent Actions</h3>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg border border-red-100">
                            <div>
                                <p className="font-bold text-red-800">Pending Restaurants</p>
                                <p className="text-xs text-red-600">Requires verification</p>
                            </div>
                            <span className="bg-red-200 text-red-800 py-1 px-3 rounded-full text-xs font-bold">
                                {stats.restaurants?.pending}
                            </span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg border border-yellow-100">
                            <div>
                                <p className="font-bold text-yellow-800">Pending Riders</p>
                                <p className="text-xs text-yellow-600">Document review needed</p>
                            </div>
                            <span className="bg-yellow-200 text-yellow-800 py-1 px-3 rounded-full text-xs font-bold">
                                {stats.riders?.pending}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
