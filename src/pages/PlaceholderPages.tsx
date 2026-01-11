import { Card } from '@/components/common';
import { Construction } from 'lucide-react';

interface PlaceholderPageProps {
    title: string;
    description: string;
}

function PlaceholderPage({ title, description }: PlaceholderPageProps) {
    return (
        <div className="space-y-6 animate-fade-in">
            <div>
                <h1 className="text-2xl font-bold text-white/90">{title}</h1>
                <p className="text-white/40">{description}</p>
            </div>
            <Card className="flex flex-col items-center justify-center py-20">
                <Construction size={64} className="text-white/20 mb-4" />
                <h2 className="text-xl font-semibold text-white/80 mb-2">Coming Soon</h2>
                <p className="text-white/40 text-center max-w-md">
                    This page is under development. Check back soon for updates!
                </p>
            </Card>
        </div>
    );
}

export function Executions() {
    return <PlaceholderPage title="Executions" description="View and manage pipeline executions" />;
}

export function AIInsightsPage() {
    return <PlaceholderPage title="AI Insights" description="AI-powered recommendations and predictions" />;
}

export function Logs() {
    return <PlaceholderPage title="Logs" description="System and pipeline logs" />;
}

export function Alerts() {
    return <PlaceholderPage title="Alerts" description="Manage alerts and notifications" />;
}

export function Settings() {
    return <PlaceholderPage title="Settings" description="Configure your FlexiRoaster instance" />;
}
