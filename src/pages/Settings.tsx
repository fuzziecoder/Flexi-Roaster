import { User, Bell, Shield, Database, Palette, Save, Upload, Sun, Moon, Monitor } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useAvatarUpload } from '@/hooks/useAvatarUpload';
import { toast } from '@/components/common';
import { useRef, useState } from 'react';
import { useUIStore } from '@/store/uiStore';

export function Settings() {
    const { user, updateProfile } = useAuth();
    const { uploadAvatar, removeAvatar, uploading, error: uploadError } = useAvatarUpload();
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [successMessage, setSuccessMessage] = useState('');
    const { theme, setTheme } = useUIStore();

    // Get user display info
    const userEmail = user?.email || 'user@example.com';
    const userAvatar = user?.user_metadata?.avatar_url;

    const [displayName, setDisplayName] = useState(
        user?.user_metadata?.full_name || user?.email?.split('@')[0] || ''
    );

    // Keep displayName in sync if user object changes (e.g. after profile update)
    useEffect(() => {
        setDisplayName(user?.user_metadata?.full_name || user?.email?.split('@')[0] || '');
    }, [user?.user_metadata?.full_name, user?.email]);

    const handleAvatarClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setSuccessMessage('');
        const { error } = await uploadAvatar(file);

        if (!error) {
            setSuccessMessage('Avatar updated successfully!');
            toast.success('Profile updated', 'Avatar has been updated successfully');
            setTimeout(() => window.location.reload(), 1000);
        } else {
            toast.error('Profile update failed', error);
        }
    };

    const handleRemoveAvatar = async () => {
        setSuccessMessage('');
        const { error } = await removeAvatar();

        if (!error) {
            setSuccessMessage('Avatar removed successfully!');
            toast.success('Profile updated', 'Avatar has been removed');
            setTimeout(() => window.location.reload(), 1000);
        } else {
            toast.error('Failed to remove avatar', error);
        }
    };

    const handleSaveChanges = async () => {
        setSaving(true);
        setSuccessMessage('');

        const { error } = await updateProfile({ full_name: displayName.trim() });

        if (!error) {
            setSuccessMessage('Profile saved successfully!');
            toast.success('Profile updated', 'Your name has been updated');
        } else {
            toast.error('Failed to save profile', error.message);
        }

        setSaving(false);
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
                                        alt={displayName}
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
                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={handleAvatarClick}
                                            disabled={uploading}
                                            className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white text-sm rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                                        >
                                            <Upload className="w-4 h-4" />
                                            {uploading ? 'Uploading...' : 'Change Avatar'}
                                        </button>
                                        {userAvatar && (
                                            <button
                                                onClick={handleRemoveAvatar}
                                                disabled={uploading}
                                                className="px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 text-sm rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                                Remove
                                            </button>
                                        )}
                                    </div>
                                    <p className="text-xs text-white/40 mt-1">Max 2MB, JPG or PNG</p>
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-white/70 mb-2">Name</label>
                                <input
                                    type="text"
                                    value={displayName}
                                    onChange={(e) => setDisplayName(e.target.value)}
                                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded text-white focus:outline-none focus:border-white/20"
                                    placeholder="Enter your name"
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

                    {/* Appearance / Theme Section */}
                    <div className="card p-6">
                        <div className="flex items-center gap-3 mb-6">
                            <Palette className="w-5 h-5 text-gray-300" />
                            <h2 className="text-lg font-semibold text-white">Appearance</h2>
                        </div>
                        <p className="text-gray-400 text-sm mb-4">Choose your preferred theme for the dashboard.</p>
                        <div className="grid grid-cols-2 gap-4">
                            {/* Dark Theme Option */}
                            <button
                                onClick={() => setTheme('dark')}
                                className={`relative flex flex-col items-center gap-3 p-5 rounded-lg border-2 transition-all ${
                                    theme === 'dark'
                                        ? 'border-white bg-white/10'
                                        : 'border-white/10 hover:border-white/30 bg-white/5'
                                }`}
                            >
                                <div className="w-full aspect-video rounded-md bg-gray-900 border border-white/10 flex flex-col overflow-hidden">
                                    <div className="h-2 bg-gray-800 border-b border-white/10"></div>
                                    <div className="flex-1 flex">
                                        <div className="w-1/4 bg-gray-800 border-r border-white/10"></div>
                                        <div className="flex-1 p-1.5 space-y-1">
                                            <div className="h-1.5 w-3/4 bg-gray-700 rounded"></div>
                                            <div className="h-1.5 w-1/2 bg-gray-700 rounded"></div>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Moon className="w-4 h-4" />
                                    <span className="text-sm font-medium text-white">Dark</span>
                                </div>
                                {theme === 'dark' && (
                                    <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-white flex items-center justify-center">
                                        <div className="w-2.5 h-2.5 rounded-full bg-gray-900"></div>
                                    </div>
                                )}
                            </button>

                            {/* Light Theme Option */}
                            <button
                                onClick={() => setTheme('light')}
                                className={`relative flex flex-col items-center gap-3 p-5 rounded-lg border-2 transition-all ${
                                    theme === 'light'
                                        ? 'border-white bg-white/10'
                                        : 'border-white/10 hover:border-white/30 bg-white/5'
                                }`}
                            >
                                <div className="w-full aspect-video rounded-md bg-gray-100 border border-gray-300 flex flex-col overflow-hidden">
                                    <div className="h-2 bg-white border-b border-gray-200"></div>
                                    <div className="flex-1 flex">
                                        <div className="w-1/4 bg-white border-r border-gray-200"></div>
                                        <div className="flex-1 p-1.5 space-y-1">
                                            <div className="h-1.5 w-3/4 bg-gray-300 rounded"></div>
                                            <div className="h-1.5 w-1/2 bg-gray-300 rounded"></div>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Sun className="w-4 h-4" />
                                    <span className="text-sm font-medium text-white">Light</span>
                                </div>
                                {theme === 'light' && (
                                    <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-white flex items-center justify-center">
                                        <div className="w-2.5 h-2.5 rounded-full bg-gray-900"></div>
                                    </div>
                                )}
                            </button>
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

            <button
                onClick={handleSaveChanges}
                disabled={saving}
                className="btn btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
                <Save className="w-4 h-4" />
                {saving ? 'Saving...' : 'Save Changes'}
            </button>
        </div>
    );
}
