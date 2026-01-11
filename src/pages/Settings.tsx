import { Settings as SettingsIcon, Database, Bell, Palette, Shield } from 'lucide-react';

export function SettingsPage() {
    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-semibold text-white/90">Settings</h1>
                <p className="text-sm text-white/50 mt-1">Configure your FlexiRoaster instance</p>
            </div>

            {/* Settings Sections */}
            <div className="grid grid-cols-1 gap-6">
                {/* General Settings */}
                <div className="bg-[hsl(var(--card))] border border-white/10 rounded-lg">
                    <div className="p-4 border-b border-white/10">
                        <div className="flex items-center gap-2">
                            <SettingsIcon size={18} className="text-white/70" />
                            <h2 className="text-sm font-medium text-white/90">General</h2>
                        </div>
                    </div>
                    <div className="p-4 space-y-4">
                        <div>
                            <label className="block text-sm text-white/70 mb-2">Instance Name</label>
                            <input
                                type="text"
                                defaultValue="FlexiRoaster Production"
                                className="w-full px-3 py-2 bg-[hsl(var(--background))] border border-white/10 rounded text-white/90 focus:outline-none focus:border-white/30"
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-white/70 mb-2">API Endpoint</label>
                            <input
                                type="text"
                                defaultValue="http://127.0.0.1:8000"
                                className="w-full px-3 py-2 bg-[hsl(var(--background))] border border-white/10 rounded text-white/90 focus:outline-none focus:border-white/30"
                            />
                        </div>
                    </div>
                </div>

                {/* Database Settings */}
                <div className="bg-[hsl(var(--card))] border border-white/10 rounded-lg">
                    <div className="p-4 border-b border-white/10">
                        <div className="flex items-center gap-2">
                            <Database size={18} className="text-white/70" />
                            <h2 className="text-sm font-medium text-white/90">Database</h2>
                        </div>
                    </div>
                    <div className="p-4 space-y-4">
                        <div>
                            <label className="block text-sm text-white/70 mb-2">Database Type</label>
                            <select className="w-full px-3 py-2 bg-[hsl(var(--background))] border border-white/10 rounded text-white/90 focus:outline-none focus:border-white/30">
                                <option>SQLite</option>
                                <option>PostgreSQL</option>
                                <option>MySQL</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm text-white/70 mb-2">Connection String</label>
                            <input
                                type="text"
                                defaultValue="sqlite:///./flexiroaster.db"
                                className="w-full px-3 py-2 bg-[hsl(var(--background))] border border-white/10 rounded text-white/90 focus:outline-none focus:border-white/30"
                            />
                        </div>
                    </div>
                </div>

                {/* Notifications */}
                <div className="bg-[hsl(var(--card))] border border-white/10 rounded-lg">
                    <div className="p-4 border-b border-white/10">
                        <div className="flex items-center gap-2">
                            <Bell size={18} className="text-white/70" />
                            <h2 className="text-sm font-medium text-white/90">Notifications</h2>
                        </div>
                    </div>
                    <div className="p-4 space-y-4">
                        <label className="flex items-center gap-3">
                            <input type="checkbox" defaultChecked className="w-4 h-4" />
                            <span className="text-sm text-white/70">Email notifications</span>
                        </label>
                        <label className="flex items-center gap-3">
                            <input type="checkbox" defaultChecked className="w-4 h-4" />
                            <span className="text-sm text-white/70">Slack integration</span>
                        </label>
                        <label className="flex items-center gap-3">
                            <input type="checkbox" className="w-4 h-4" />
                            <span className="text-sm text-white/70">SMS alerts</span>
                        </label>
                    </div>
                </div>

                {/* Appearance */}
                <div className="bg-[hsl(var(--card))] border border-white/10 rounded-lg">
                    <div className="p-4 border-b border-white/10">
                        <div className="flex items-center gap-2">
                            <Palette size={18} className="text-white/70" />
                            <h2 className="text-sm font-medium text-white/90">Appearance</h2>
                        </div>
                    </div>
                    <div className="p-4 space-y-4">
                        <div>
                            <label className="block text-sm text-white/70 mb-2">Theme</label>
                            <select className="w-full px-3 py-2 bg-[hsl(var(--background))] border border-white/10 rounded text-white/90 focus:outline-none focus:border-white/30">
                                <option>Muted Dark Grey (Current)</option>
                                <option>Dark</option>
                                <option>Light</option>
                            </select>
                        </div>
                        <label className="flex items-center gap-3">
                            <input type="checkbox" defaultChecked className="w-4 h-4" />
                            <span className="text-sm text-white/70">Compact mode</span>
                        </label>
                    </div>
                </div>

                {/* Security */}
                <div className="bg-[hsl(var(--card))] border border-white/10 rounded-lg">
                    <div className="p-4 border-b border-white/10">
                        <div className="flex items-center gap-2">
                            <Shield size={18} className="text-white/70" />
                            <h2 className="text-sm font-medium text-white/90">Security</h2>
                        </div>
                    </div>
                    <div className="p-4 space-y-4">
                        <label className="flex items-center gap-3">
                            <input type="checkbox" defaultChecked className="w-4 h-4" />
                            <span className="text-sm text-white/70">Two-factor authentication</span>
                        </label>
                        <label className="flex items-center gap-3">
                            <input type="checkbox" defaultChecked className="w-4 h-4" />
                            <span className="text-sm text-white/70">API key rotation</span>
                        </label>
                        <label className="flex items-center gap-3">
                            <input type="checkbox" className="w-4 h-4" />
                            <span className="text-sm text-white/70">Audit logging</span>
                        </label>
                    </div>
                </div>
            </div>

            {/* Save Button */}
            <div className="flex justify-end">
                <button className="px-6 py-2 bg-white/10 hover:bg-white/20 text-white/90 rounded border border-white/20 transition-colors">
                    Save Changes
                </button>
            </div>
        </div>
    );
}
