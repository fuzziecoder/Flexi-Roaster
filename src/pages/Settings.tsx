import { User, Bell, Shield, Database, Palette, Save } from 'lucide-react';

export function Settings() {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-white">Settings</h1>
                <p className="text-gray-400 mt-1">Configure your dashboard preferences</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                    {/* Profile Settings */}
                    <div className="card p-6">
                        <div className="flex items-center gap-3 mb-6">
                            <User className="w-5 h-5 text-gray-300" />
                            <h2 className="text-lg font-semibold text-white">Profile</h2>
                        </div>
                        <div className="space-y-4">
                            <div>
                                <label className="text-sm text-gray-400 mb-1 block">Name</label>
                                <input
                                    type="text"
                                    defaultValue="Administrator"
                                    className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-gray-500 transition-colors"
                                />
                            </div>
                            <div>
                                <label className="text-sm text-gray-400 mb-1 block">Email</label>
                                <input
                                    type="email"
                                    defaultValue="admin@flexiroaster.io"
                                    className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-gray-500 transition-colors"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Notification Settings */}
                    <div className="card p-6">
                        <div className="flex items-center gap-3 mb-6">
                            <Bell className="w-5 h-5 text-gray-300" />
                            <h2 className="text-lg font-semibold text-white">Notifications</h2>
                        </div>
                        <div className="space-y-4">
                            {['Critical Alerts', 'Warning Alerts', 'Pipeline Completions', 'AI Insights'].map((item) => (
                                <div key={item} className="flex items-center justify-between">
                                    <span className="text-gray-300">{item}</span>
                                    <label className="relative inline-flex items-center cursor-pointer">
                                        <input type="checkbox" defaultChecked className="sr-only peer" />
                                        <div className="w-11 h-6 bg-gray-700 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-gray-400 after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-gray-300 peer-checked:after:bg-gray-900"></div>
                                    </label>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="space-y-4">
                    {[
                        { icon: Shield, label: 'Security', desc: 'Manage access controls' },
                        { icon: Database, label: 'Data', desc: 'Configure connections' },
                        { icon: Palette, label: 'Theme', desc: 'Customize appearance' },
                    ].map((item) => (
                        <div key={item.label} className="card p-4 hover:border-gray-600 cursor-pointer transition-colors">
                            <div className="flex items-center gap-3">
                                <item.icon className="w-5 h-5 text-gray-300" />
                                <div>
                                    <p className="font-medium text-white">{item.label}</p>
                                    <p className="text-xs text-gray-400">{item.desc}</p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <button className="btn btn-primary flex items-center gap-2">
                <Save className="w-4 h-4" />
                Save Changes
            </button>
        </div>
    );
}
