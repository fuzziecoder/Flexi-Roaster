// Supabase Edge Function: Flexible AI Chat Proxy
// Deploy to Supabase Functions to keep API key secure

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";

const NVIDIA_API_KEY = Deno.env.get("NVIDIA_API_KEY");
const NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1";

// System prompt with app context
const SYSTEM_PROMPT = `You are Flexible AI, an intelligent assistant for FlexiRoaster - a pipeline automation and monitoring system.

## Your Capabilities:
1. **Create Pipelines** - Help users create data pipelines with stages
2. **Execute Pipelines** - Start pipeline executions
3. **Explain Insights** - Help users understand AI-generated insights
4. **Troubleshoot** - Debug pipeline failures and issues
5. **Navigate** - Guide users through the app

## App Structure:
- **Dashboard** - Overview of system health and metrics
- **Pipelines** - Create, edit, manage data pipelines
- **Executions** - Monitor running and past executions
- **AI Insights** - View failure predictions and anomalies
- **Logs** - Search and filter execution logs
- **Alerts** - View and manage system alerts
- **Settings** - User preferences and configuration

## Pipeline Stages:
- INPUT - Load data from sources (API, file, database)
- TRANSFORM - Process and transform data
- VALIDATION - Validate data against rules
- OUTPUT - Save data to destination

## When creating pipelines:
- Use descriptive names
- Add clear descriptions
- Define proper stage dependencies
- Set appropriate timeouts (default 120s)
- Configure retries for reliability (default 3)

## Response Style:
- Be concise and helpful
- Use markdown formatting
- For actions, use the available tools
- Explain what you're doing

Always be ready to help with pipeline automation tasks!`;

// Tool definitions for DeepSeek
const TOOLS = [
    {
        type: "function",
        function: {
            name: "create_pipeline",
            description: "Create a new data pipeline with stages",
            parameters: {
                type: "object",
                properties: {
                    name: {
                        type: "string",
                        description: "Name of the pipeline"
                    },
                    description: {
                        type: "string",
                        description: "Description of what the pipeline does"
                    },
                    stages: {
                        type: "array",
                        description: "List of pipeline stages",
                        items: {
                            type: "object",
                            properties: {
                                id: { type: "string", description: "Unique stage ID" },
                                name: { type: "string", description: "Stage name" },
                                type: { type: "string", enum: ["input", "transform", "validation", "output"] },
                                config: { type: "object", description: "Stage configuration" },
                                dependencies: { type: "array", items: { type: "string" } }
                            },
                            required: ["id", "name", "type"]
                        }
                    }
                },
                required: ["name", "stages"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "execute_pipeline",
            description: "Execute/run an existing pipeline",
            parameters: {
                type: "object",
                properties: {
                    pipeline_id: {
                        type: "string",
                        description: "ID of the pipeline to execute"
                    },
                    variables: {
                        type: "object",
                        description: "Optional variables to pass to the pipeline"
                    }
                },
                required: ["pipeline_id"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "list_pipelines",
            description: "Get a list of all available pipelines",
            parameters: {
                type: "object",
                properties: {
                    is_active: {
                        type: "boolean",
                        description: "Filter by active status"
                    }
                }
            }
        }
    },
    {
        type: "function",
        function: {
            name: "get_pipeline_status",
            description: "Get the status of a specific pipeline execution",
            parameters: {
                type: "object",
                properties: {
                    execution_id: {
                        type: "string",
                        description: "ID of the execution to check"
                    }
                },
                required: ["execution_id"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "get_ai_insights",
            description: "Retrieve AI-generated insights and predictions",
            parameters: {
                type: "object",
                properties: {
                    pipeline_id: {
                        type: "string",
                        description: "Optional: filter by pipeline ID"
                    }
                }
            }
        }
    },
    {
        type: "function",
        function: {
            name: "navigate_to",
            description: "Navigate user to a specific page in the app",
            parameters: {
                type: "object",
                properties: {
                    page: {
                        type: "string",
                        enum: ["dashboard", "pipelines", "executions", "ai-insights", "logs", "alerts", "settings"],
                        description: "Page to navigate to"
                    }
                },
                required: ["page"]
            }
        }
    }
];

const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
    "Access-Control-Allow-Methods": "POST, OPTIONS"
};

serve(async (req) => {
    // Handle CORS preflight
    if (req.method === "OPTIONS") {
        return new Response("ok", { headers: corsHeaders });
    }

    try {
        if (!NVIDIA_API_KEY) {
            throw new Error("NVIDIA_API_KEY not configured");
        }

        const { messages, stream = true } = await req.json();

        // Add system prompt to messages
        const fullMessages = [
            { role: "system", content: SYSTEM_PROMPT },
            ...messages
        ];

        const response = await fetch(`${NVIDIA_BASE_URL}/chat/completions`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${NVIDIA_API_KEY}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                model: "deepseek-ai/deepseek-v3.2",
                messages: fullMessages,
                temperature: 0.7,
                top_p: 0.95,
                max_tokens: 4096,
                stream: stream,
                tools: TOOLS,
                tool_choice: "auto",
                extra_body: { chat_template_kwargs: { thinking: true } }
            })
        });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(`NVIDIA API error: ${error}`);
        }

        if (stream) {
            // Stream the response
            return new Response(response.body, {
                headers: {
                    ...corsHeaders,
                    "Content-Type": "text/event-stream",
                    "Cache-Control": "no-cache"
                }
            });
        } else {
            const data = await response.json();
            return new Response(JSON.stringify(data), {
                headers: {
                    ...corsHeaders,
                    "Content-Type": "application/json"
                }
            });
        }
    } catch (error) {
        console.error("Error:", error);
        return new Response(
            JSON.stringify({ error: error.message }),
            {
                status: 500,
                headers: {
                    ...corsHeaders,
                    "Content-Type": "application/json"
                }
            }
        );
    }
});
