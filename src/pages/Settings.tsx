import { User, Bell, Shield, Database, Palette, Save, Upload } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useAvatarUpload } from '@/hooks/useAvatarUpload';
import { useRef, useState } from 'react';

export function Settings() {
    const { user } = useAuth();
    const { uploadAvatar, uploading, error: uploadError } = useAvatarUpload();
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [successMessage, setSuccessMessage] = useState('');

    // Get user display info
    const userName = user?.user_metadata?.full_name || user?.email?.split('@')[0] || 'User';
    const userEmail = user?.email || 'user@example.com';
    const userAvatar = user?.user_metadata?.avatar_url;

    const handleAvatarClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setSuccessMessage('');
        const { error } = await uploadAvatar(file);

        if (!error) {
            setSuccessMessage('Avatar updated successfully! Refresh to see changes.');
            // Reload page after 1 second to show new avatar
            setTimeout(() => window.location.reload(), 1000);
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-white">Settings</h1>
                <p className="text-gray-400 mt-1">Configure your dashboard preferences</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                    {/* Profile Section */}
                    <div className="card p-6">
                        <div className="flex items-center gap-2 mb-4">
                            <User className="w-5 h-5 text-white/70" />
                            <h2 className="text-lg font-semibold text-white">Profile</h2>
                        </div>

                        {/* Success/Error Messages */}
                        {successMessage && (
                            <div className="mb-4 p-3 bg-green-500/10 border border-green-500/20 rounded text-green-400 text-sm">
                                {successMessage}
                            </div>
                        )}
                        {uploadError && (
                            <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded text-red-400 text-sm">
                                {uploadError}
                            </div>
                        )}

                        <div className="space-y-4">
                            <div className="flex items-center gap-4">
                                {userAvatar ? (
                                    <img
                                        src={userAvatar}
                                        alt={userName}
                                        className="w-16 h-16 rounded-full object-cover"
                                    />
                                ) : (
                                    <div className="w-16 h-16 rounded-full bg-white/10 flex items-center justify-center">
                                        <User className="w-8 h-8 text-white/70" />
                                    </div>
                                )}
                                <div>
                                    <input
                                        ref={fileInputRef}
                                        type="file"
                                        accept="image/*"
                                        onChange={handleFileChange}
                                        className="hidden"
                                    />
                                    <button
                                        onClick={handleAvatarClick}
                                        disabled={uploading}
                                        className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white text-sm rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                                    >
                                        <Upload className="w-4 h-4" />
                                        {uploading ? 'Uploading...' : 'Change Avatar'}
                                    </button>
                                    <p className="text-xs text-white/40 mt-1">Max 2MB, JPG or PNG</p>
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-white/70 mb-2">Name</label>
                                <input
                                    type="text"
                                    value={userName}
                                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded text-white focus:outline-none focus:border-white/20"
                                    readOnly
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-white/70 mb-2">Email</label>
                                <input
                                    type="email"
                                    value={userEmail}
                                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded text-white focus:outline-none focus:border-white/20"
                                    readOnly
                                />
                                <p className="text-xs text-white/40 mt-1">Email cannot be changed</p>
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
