export interface GeneratedPipelineStage {
    name: string;
    order: number;
    type: 'source' | 'transform' | 'destination' | 'validation' | 'notification';
    config: Record<string, unknown>;
}

export interface GeneratedPipelinePlan {
    name: string;
    description: string;
    cron: string;
    timezone: string;
    stages: GeneratedPipelineStage[];
    config: {
        generatedFromPrompt: string;
        schedule: {
            cron: string;
            timezone: string;
            humanReadable: string;
        };
        stages: GeneratedPipelineStage[];
    };
}

const DEFAULT_TIMEZONE = 'UTC';

const titleCase = (value: string) => value.charAt(0).toUpperCase() + value.slice(1);

const parseSchedule = (prompt: string) => {
    const input = prompt.toLowerCase();

    const dayMap: Record<string, number> = {
        sunday: 0,
        monday: 1,
        tuesday: 2,
        wednesday: 3,
        thursday: 4,
        friday: 5,
        saturday: 6,
    };

    let minute = 0;
    let hour: number | "*" = 0;
    let dayOfMonth = '*';
    const month = '*';
    let dayOfWeek = '*';
    let humanReadable = 'Daily at 09:00 UTC';

    const timeMatch = input.match(/at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?/i);
    if (timeMatch) {
        hour = Number(timeMatch[1]);
        minute = Number(timeMatch[2] ?? 0);
        const period = timeMatch[3]?.toLowerCase();
        if (period === 'pm' && hour < 12) hour += 12;
        if (period === 'am' && hour === 12) hour = 0;
    } else {
        const militaryMatch = input.match(/at\s+(\d{1,2}):(\d{2})/);
        if (militaryMatch) {
            hour = Number(militaryMatch[1]);
            minute = Number(militaryMatch[2]);
        }
    }

    const specificDay = Object.entries(dayMap).find(([day]) => input.includes(`every ${day}`) || input.includes(`on ${day}`));
    if (specificDay) {
        dayOfWeek = String(specificDay[1]);
        humanReadable = `Every ${titleCase(specificDay[0])} at ${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')} UTC`;
    } else if (input.includes('hourly')) {
        minute = 0;
        hour = '*';
        humanReadable = 'Hourly';
    } else if (input.includes('weekly')) {
        dayOfWeek = '1';
        humanReadable = `Weekly on Monday at ${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')} UTC`;
    } else if (input.includes('monthly')) {
        dayOfMonth = '1';
        humanReadable = `Monthly on day 1 at ${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')} UTC`;
    } else {
        humanReadable = `Daily at ${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')} UTC`;
    }

    const cron = `${minute} ${hour} ${dayOfMonth} ${month} ${dayOfWeek}`;
    return { cron, humanReadable };
};

const inferSourceStage = (prompt: string): GeneratedPipelineStage => {
    const input = prompt.toLowerCase();

    if (input.includes('s3')) {
        return {
            name: 'Fetch from S3',
            order: 0,
            type: 'source',
            config: {
                connector: 'aws_s3',
                bucket: 'replace-with-your-bucket',
                format: input.includes('csv') ? 'csv' : 'parquet',
            },
        };
    }

    if (input.includes('kafka')) {
        return {
            name: 'Read Kafka Topic',
            order: 0,
            type: 'source',
            config: {
                connector: 'kafka',
                topic: 'replace-with-topic',
                format: 'json',
            },
        };
    }

    return {
        name: 'Ingest Data',
        order: 0,
        type: 'source',
        config: {
            connector: 'generic_source',
        },
    };
};

const inferTransformStage = (prompt: string, order: number): GeneratedPipelineStage => {
    const input = prompt.toLowerCase();

    if (input.includes('pandas')) {
        return {
            name: 'Transform with Pandas',
            order,
            type: 'transform',
            config: {
                engine: 'pandas',
                script: 'df = df.drop_duplicates()\n# add your transformations here',
            },
        };
    }

    return {
        name: 'Transform Data',
        order,
        type: 'transform',
        config: {
            engine: 'python',
        },
    };
};

const inferDestinationStage = (prompt: string, order: number): GeneratedPipelineStage => {
    const input = prompt.toLowerCase();

    if (input.includes('postgres') || input.includes('postgresql')) {
        return {
            name: 'Load to PostgreSQL',
            order,
            type: 'destination',
            config: {
                connector: 'postgresql',
                table: 'replace_with_table_name',
                mode: 'append',
            },
        };
    }

    return {
        name: 'Write Output',
        order,
        type: 'destination',
        config: {
            connector: 'generic_destination',
        },
    };
};

const inferPipelineName = (prompt: string): string => {
    const source = prompt.toLowerCase().includes('s3') ? 'S3' : 'Source';
    const destination = prompt.toLowerCase().includes('postgres') ? 'Postgres' : 'Target';
    return `${source} to ${destination} Pipeline`;
};

export const generatePipelineFromPrompt = (prompt: string): GeneratedPipelinePlan => {
    const trimmedPrompt = prompt.trim();
    const { cron, humanReadable } = parseSchedule(trimmedPrompt);

    const stages: GeneratedPipelineStage[] = [];
    stages.push(inferSourceStage(trimmedPrompt));

    if (trimmedPrompt.toLowerCase().includes('transform')) {
        stages.push(inferTransformStage(trimmedPrompt, stages.length));
    }

    stages.push(inferDestinationStage(trimmedPrompt, stages.length));

    const name = inferPipelineName(trimmedPrompt);
    const description = `Auto-generated from prompt: "${trimmedPrompt}"`;

    return {
        name,
        description,
        cron,
        timezone: DEFAULT_TIMEZONE,
        stages,
        config: {
            generatedFromPrompt: trimmedPrompt,
            schedule: {
                cron,
                timezone: DEFAULT_TIMEZONE,
                humanReadable,
            },
            stages,
        },
    };
};
