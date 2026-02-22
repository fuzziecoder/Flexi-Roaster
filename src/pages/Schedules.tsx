import { useEffect, useMemo, useState } from 'react';
import { Card } from '@/components/common';
import { toast } from '@/components/common/Toast';
import { usePipelines } from '@/hooks/usePipelines';
import {
    Calendar,
    Clock,
    Play,
    Pause,
    Plus,
    Trash2,
    Edit2,
    Webhook,
    Zap,
    RefreshCw,
    MoreVertical,
    X,
} from 'lucide-react';

// Schedule type - would be stored in database
interface Schedule {
    id: string;
    name: string;
    pipelineId: string;
    pipelineName: string;
    type: 'cron' | 'interval' | 'webhook' | 'event';
    expression: string;
    isActive: boolean;
    lastRun: string | null;
    nextRun: string | null;
    createdAt: string;
}

const SCHEDULES_STORAGE_KEY = 'flexiroaster:schedules';

const typeIcons = {
    cron: Clock,
    interval: RefreshCw,
    webhook: Webhook,
    event: Zap,
};

const typeLabels = {
    cron: 'Cron',
    interval: 'Interval',
    webhook: 'Webhook',
    event: 'Event',
};

function formatRelativeTime(dateStr: string | null): string {
    if (!dateStr) return 'Never';
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const future = diff < 0;
    const absDiff = Math.abs(diff);

    const minutes = Math.floor(absDiff / 60000);
    const hours = Math.floor(absDiff / 3600000);
    const days = Math.floor(absDiff / 86400000);

    if (minutes < 60) return future ? `in ${minutes}m` : `${minutes}m ago`;
    if (hours < 24) return future ? `in ${hours}h` : `${hours}h ago`;
    return future ? `in ${days}d` : `${days}d ago`;
}

function calculateNextRun(type: Schedule['type'], expression: string): string | null {
    const now = new Date();

    if (type === 'interval') {
        const match = expression.trim().match(/(\d+)\s*(minute|minutes|hour|hours|day|days)/i);
        if (!match) return null;
        const count = Number(match[1]);
        const unit = match[2].toLowerCase();
        const next = new Date(now);

        if (unit.startsWith('minute')) next.setMinutes(next.getMinutes() + count);
        if (unit.startsWith('hour')) next.setHours(next.getHours() + count);
        if (unit.startsWith('day')) next.setDate(next.getDate() + count);
        return next.toISOString();
    }

    if (type === 'cron') {
        // Basic cron support for the common "minute hour * * *" pattern.
        const cronMatch = expression.trim().match(/^(\*|\d{1,2})\s+(\*|\d{1,2})\s+\*\s+\*\s+\*$/);
        if (!cronMatch) return null;

        const [, minuteToken, hourToken] = cronMatch;
        const minute = minuteToken === '*' ? now.getMinutes() + 1 : Number(minuteToken);
        const hour = hourToken === '*' ? now.getHours() : Number(hourToken);

        const next = new Date(now);
        next.setSeconds(0, 0);
        next.setMinutes(Math.min(minute, 59));
        next.setHours(Math.min(hour, 23));

        if (next <= now || minuteToken === '*') {
            next.setMinutes(next.getMinutes() + (minuteToken === '*' ? 1 : 60 * 24));
        }
        if (hourToken === '*' && next <= now) {
            next.setHours(next.getHours() + 1);
        }

        return next.toISOString();
    }

    return null;
}

// New Schedule Modal
function NewScheduleModal({
    isOpen,
    onClose,
    pipelines,
    onSave
}: {
    isOpen: boolean;
    onClose: () => void;
    pipelines: { id: string; name: string }[];
    onSave: (schedule: Omit<Schedule, 'id' | 'lastRun' | 'nextRun' | 'createdAt'>) => void;
}) {
    const [name, setName] = useState('');
    const [pipelineId, setPipelineId] = useState('');
    const [type, setType] = useState<'cron' | 'interval' | 'webhook' | 'event'>('cron');
    const [expression, setExpression] = useState('');

    if (!isOpen) return null;

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!name || !pipelineId || !expression) {
            toast.error('Please fill all fields');
            return;
        }

        const pipeline = pipelines.find(p => p.id === pipelineId);
        onSave({
            name,
            pipelineId,
            pipelineName: pipeline?.name || '',
            type,
            expression,
            isActive: true,
        });

        // Reset form
        setName('');
        setPipelineId('');
        setType('cron');
        setExpression('');
        onClose();
    };

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-[#1a1a1a] border border-white/10 rounded-xl w-full max-w-md shadow-2xl">
                <div className="flex items-center justify-between p-4 border-b border-white/10">
                    <h2 className="text-lg font-semibold text-white">New Schedule</h2>
                    <button onClick={onClose} className="p-1 hover:bg-white/10 rounded">
                        <X className="w-5 h-5 text-white/60" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-4 space-y-4">
                    <div>
                        <label className="block text-xs text-white/50 mb-1.5">Schedule Name</label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="e.g., Daily ETL Job"
                            className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-white/30 focus:outline-none focus:border-white/20"
                        />
                    </div>

                    <div>
                        <label className="block text-xs text-white/50 mb-1.5">Pipeline</label>
                        <select
                            value={pipelineId}
                            onChange={(e) => setPipelineId(e.target.value)}
                            className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white focus:outline-none focus:border-white/20"
                        >
                            <option value="">Select a pipeline</option>
                            {pipelines.map(p => (
                                <option key={p.id} value={p.id}>{p.name}</option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-xs text-white/50 mb-1.5">Trigger Type</label>
                        <div className="grid grid-cols-4 gap-2">
                            {(['cron', 'interval', 'webhook', 'event'] as const).map(t => {
                                const Icon = typeIcons[t];
                                return (
                                    <button
                                        key={t}
                                        type="button"
                                        onClick={() => setType(t)}
                                        className={`flex flex-col items-center gap-1 p-2 rounded-lg border transition-colors ${type === t
                                                ? 'bg-white/10 border-white/30'
                                                : 'border-white/10 hover:border-white/20'
                                            }`}
                                    >
                                        <Icon className="w-4 h-4 text-white/60" />
                                        <span className="text-[10px] text-white/60">{typeLabels[t]}</span>
                                    </button>
                                );
                            })}
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs text-white/50 mb-1.5">
                            {type === 'cron' ? 'Cron Expression' :
                                type === 'interval' ? 'Interval (e.g., every 1 hour)' :
                                    type === 'webhook' ? 'Webhook Path' : 'Event Pattern'}
                        </label>
                        <input
                            type="text"
                            value={expression}
                            onChange={(e) => setExpression(e.target.value)}
                            placeholder={
                                type === 'cron' ? '0 * * * *' :
                                    type === 'interval' ? 'every 30 minutes' :
                                        type === 'webhook' ? '/api/trigger/my-pipeline' : 'file.uploaded'
                            }
                            className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white font-mono placeholder-white/30 focus:outline-none focus:border-white/20"
                        />
                    </div>

                    <div className="flex gap-3 pt-2">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-2 border border-white/10 text-white/60 rounded-lg hover:bg-white/5 transition-colors text-sm"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="flex-1 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/15 transition-colors text-sm font-medium"
                        >
                            Create Schedule
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

function ScheduleCard({
    schedule,
    onDelete,
    onToggleActive,
    onRunNow,
}: {
    schedule: Schedule;
    onDelete: (id: string) => void;
    onToggleActive: (id: string) => void;
    onRunNow: (id: string) => void;
}) {
    const [showMenu, setShowMenu] = useState(false);
    const TypeIcon = typeIcons[schedule.type];

    return (
        <div className="p-4 rounded-lg bg-white/[0.02] border border-white/5 hover:border-white/10 transition-all group">
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${schedule.isActive ? 'bg-white/10' : 'bg-white/5'}`}>
                        <TypeIcon className={`w-4 h-4 ${schedule.isActive ? 'text-white/60' : 'text-white/30'}`} />
                    </div>
                    <div>
                        <h3 className="text-sm font-medium text-white/90">{schedule.name}</h3>
                        <p className="text-xs text-white/40">{schedule.pipelineName}</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 text-[10px] rounded ${schedule.isActive
                            ? 'bg-white/10 text-white/60'
                            : 'bg-white/5 text-white/30'
                        }`}>
                        {schedule.isActive ? 'Active' : 'Paused'}
                    </span>
                    <div className="relative">
                        <button
                            onClick={() => setShowMenu(!showMenu)}
                            className="p-1 hover:bg-white/10 rounded opacity-0 group-hover:opacity-100"
                        >
                            <MoreVertical className="w-4 h-4 text-white/40" />
                        </button>
                        {showMenu && (
                            <div className="absolute right-0 top-full mt-1 w-32 bg-[#1a1a1a] border border-white/10 rounded-lg shadow-xl z-10">
                                <button className="w-full px-3 py-2 text-left text-xs text-white/60 hover:bg-white/5 flex items-center gap-2">
                                    <Edit2 className="w-3 h-3" /> Edit
                                </button>
                                <button
                                    onClick={() => {
                                        onToggleActive(schedule.id);
                                        setShowMenu(false);
                                    }}
                                    className="w-full px-3 py-2 text-left text-xs text-white/60 hover:bg-white/5 flex items-center gap-2"
                                >
                                    {schedule.isActive ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
                                    {schedule.isActive ? 'Pause' : 'Resume'}
                                </button>
                                <button
                                    onClick={() => {
                                        onRunNow(schedule.id);
                                        setShowMenu(false);
                                    }}
                                    className="w-full px-3 py-2 text-left text-xs text-white/60 hover:bg-white/5 flex items-center gap-2"
                                >
                                    <Play className="w-3 h-3" /> Run Now
                                </button>
                                <button
                                    onClick={() => { onDelete(schedule.id); setShowMenu(false); }}
                                    className="w-full px-3 py-2 text-left text-xs text-red-400/60 hover:bg-white/5 flex items-center gap-2"
                                >
                                    <Trash2 className="w-3 h-3" /> Delete
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <div className="flex items-center gap-4 text-xs">
                <div className="flex items-center gap-1.5">
                    <span className="text-white/30">Type:</span>
                    <span className="px-1.5 py-0.5 bg-white/5 rounded text-white/50">
                        {typeLabels[schedule.type]}
                    </span>
                </div>
                <div className="flex items-center gap-1.5 flex-1 min-w-0">
                    <span className="text-white/30">Expression:</span>
                    <code className="text-white/50 font-mono text-[10px] truncate">
                        {schedule.expression}
                    </code>
                </div>
            </div>

            <div className="flex items-center gap-4 mt-3 pt-3 border-t border-white/5 text-xs">
                <div>
                    <span className="text-white/30">Last run: </span>
                    <span className="text-white/50">{formatRelativeTime(schedule.lastRun)}</span>
                </div>
                {schedule.nextRun && (
                    <div>
                        <span className="text-white/30">Next run: </span>
                        <span className="text-white/50">{formatRelativeTime(schedule.nextRun)}</span>
                    </div>
                )}
            </div>
        </div>
    );
}

export function SchedulesPage() {
    const { pipelines } = usePipelines();
    const [filter, setFilter] = useState<'all' | 'cron' | 'interval' | 'webhook' | 'event'>('all');
    const [showNewModal, setShowNewModal] = useState(false);
    const [schedules, setSchedules] = useState<Schedule[]>([]);

    useEffect(() => {
        const stored = localStorage.getItem(SCHEDULES_STORAGE_KEY);
        if (!stored) return;
        try {
            const parsed = JSON.parse(stored) as Schedule[];
            if (Array.isArray(parsed)) {
                setSchedules(parsed);
            }
        } catch {
            localStorage.removeItem(SCHEDULES_STORAGE_KEY);
        }
    }, []);

    useEffect(() => {
        localStorage.setItem(SCHEDULES_STORAGE_KEY, JSON.stringify(schedules));
    }, [schedules]);

    const handleSaveSchedule = (scheduleData: Omit<Schedule, 'id' | 'lastRun' | 'nextRun' | 'createdAt'>) => {
        const newSchedule: Schedule = {
            ...scheduleData,
            id: `sch-${Date.now()}`,
            lastRun: null,
            nextRun: calculateNextRun(scheduleData.type, scheduleData.expression),
            createdAt: new Date().toISOString(),
        };
        setSchedules(prev => [newSchedule, ...prev]);
        toast.success('Schedule created', `${scheduleData.name} has been created`);
    };

    const handleDeleteSchedule = (id: string) => {
        setSchedules(prev => prev.filter(s => s.id !== id));
        toast.success('Schedule deleted');
    };

    const handleToggleActive = (id: string) => {
        setSchedules((prev) => prev.map((s) => {
            if (s.id !== id) return s;
            const isActive = !s.isActive;
            return {
                ...s,
                isActive,
                nextRun: isActive ? calculateNextRun(s.type, s.expression) : null,
            };
        }));
    };

    const handleRunNow = (id: string) => {
        setSchedules((prev) => prev.map((s) => {
            if (s.id !== id) return s;
            return {
                ...s,
                lastRun: new Date().toISOString(),
                nextRun: s.isActive ? calculateNextRun(s.type, s.expression) : null,
            };
        }));
        toast.success('Schedule triggered', 'Pipeline execution has been queued');
    };

    const filteredSchedules = useMemo(() => (
        filter === 'all' ? schedules : schedules.filter(s => s.type === filter)
    ), [filter, schedules]);

    const stats = {
        total: schedules.length,
        active: schedules.filter(s => s.isActive).length,
        cron: schedules.filter(s => s.type === 'cron').length,
        webhook: schedules.filter(s => s.type === 'webhook').length,
    };

    return (
        <div className="space-y-6">
            {/* New Schedule Modal */}
            <NewScheduleModal
                isOpen={showNewModal}
                onClose={() => setShowNewModal(false)}
                pipelines={pipelines}
                onSave={handleSaveSchedule}
            />

            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Schedules & Triggers</h1>
                    <p className="text-white/50 text-sm mt-1">Automate pipeline execution with schedules and triggers</p>
                </div>
                <button
                    onClick={() => setShowNewModal(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/15 text-white rounded-lg transition-colors"
                >
                    <Plus className="w-4 h-4" />
                    <span className="text-sm font-medium">New Schedule</span>
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <Card className="p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5">
                            <Calendar className="w-4 h-4 text-white/40" />
                        </div>
                        <div>
                            <p className="text-xl font-bold text-white/90">{stats.total}</p>
                            <p className="text-xs text-white/40">Total Schedules</p>
                        </div>
                    </div>
                </Card>
                <Card className="p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5">
                            <Play className="w-4 h-4 text-white/40" />
                        </div>
                        <div>
                            <p className="text-xl font-bold text-white/90">{stats.active}</p>
                            <p className="text-xs text-white/40">Active</p>
                        </div>
                    </div>
                </Card>
                <Card className="p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5">
                            <Clock className="w-4 h-4 text-white/40" />
                        </div>
                        <div>
                            <p className="text-xl font-bold text-white/90">{stats.cron}</p>
                            <p className="text-xs text-white/40">Cron Jobs</p>
                        </div>
                    </div>
                </Card>
                <Card className="p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5">
                            <Webhook className="w-4 h-4 text-white/40" />
                        </div>
                        <div>
                            <p className="text-xl font-bold text-white/90">{stats.webhook}</p>
                            <p className="text-xs text-white/40">Webhooks</p>
                        </div>
                    </div>
                </Card>
            </div>

            {/* Filter Tabs */}
            <div className="flex items-center gap-2">
                {(['all', 'cron', 'interval', 'webhook', 'event'] as const).map(type => (
                    <button
                        key={type}
                        onClick={() => setFilter(type)}
                        className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${filter === type
                                ? 'bg-white/10 text-white'
                                : 'text-white/40 hover:text-white/60 hover:bg-white/5'
                            }`}
                    >
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                    </button>
                ))}
            </div>

            {/* Schedule List */}
            {filteredSchedules.length > 0 ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {filteredSchedules.map(schedule => (
                        <ScheduleCard
                            key={schedule.id}
                            schedule={schedule}
                            onDelete={handleDeleteSchedule}
                            onToggleActive={handleToggleActive}
                            onRunNow={handleRunNow}
                        />
                    ))}
                </div>
            ) : (
                <Card className="p-12 text-center">
                    <Calendar className="w-12 h-12 text-white/20 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-white/60 mb-2">No schedules yet</h3>
                    <p className="text-sm text-white/40 mb-4">
                        {pipelines.length > 0
                            ? 'Create your first schedule to automate pipeline execution'
                            : 'Create a pipeline first, then add schedules to automate it'
                        }
                    </p>
                    <button
                        onClick={() => pipelines.length > 0 ? setShowNewModal(true) : null}
                        disabled={pipelines.length === 0}
                        className="px-4 py-2 bg-white/10 hover:bg-white/15 text-white rounded-lg transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {pipelines.length > 0 ? 'Create Schedule' : 'Create Pipeline First'}
                    </button>
                </Card>
            )}
        </div>
    );
}
