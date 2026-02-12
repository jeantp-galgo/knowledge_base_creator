> ## Documentation Index
> Fetch the complete documentation index at: https://docs.firecrawl.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Agent

> Gather data wherever it lives on the web.

Firecrawl `/agent` is a magic API that searches, navigates, and gathers data from the widest range of websites, finding data in hard-to-reach places and uncovering data in ways no other API can. It accomplishes in a few minutes what would take a human many hours — end-to-end data collection, without scripts or manual work.
Whether you need one data point or entire datasets at scale, Firecrawl `/agent` works to get your data.

**Think of `/agent` as deep research for data, wherever it is!**

<Info>
  **Research Preview**: Agent is in early access. Expect rough edges. It will get significantly better over time. [Share feedback →](mailto:product@firecrawl.com)
</Info>

Agent builds on everything great about `/extract` and takes it further:

* **No URLs Required**: Just describe what you need via `prompt` parameter. URLs are optional
* **Deep Web Search**: Autonomously searches and navigates deep into sites to find your data
* **Reliable and Accurate**: Works with a wide variety of queries and use cases
* **Faster**: Processes multiple sources in parallel for quicker results

## Using `/agent`

The only required parameter is `prompt`. Simply describe what data you want to extract. For structured output, provide a JSON schema. The SDKs support Pydantic (Python) and Zod (Node) for type-safe schema definitions:

<CodeGroup>
  ```python Python theme={null}
  from firecrawl import Firecrawl
  from pydantic import BaseModel, Field
  from typing import List, Optional

  app = Firecrawl(api_key="fc-YOUR_API_KEY")

  class Founder(BaseModel):
      name: str = Field(description="Full name of the founder")
      role: Optional[str] = Field(None, description="Role or position")
      background: Optional[str] = Field(None, description="Professional background")

  class FoundersSchema(BaseModel):
      founders: List[Founder] = Field(description="List of founders")

  result = app.agent(
      prompt="Find the founders of Firecrawl",
      schema=FoundersSchema,
      model="spark-1-mini"
  )

  print(result.data)
  ```

  ```js Node theme={null}
  import Firecrawl from '@mendable/firecrawl-js';
  import { z } from 'zod';

  const firecrawl = new Firecrawl({ apiKey: "fc-YOUR_API_KEY" });

  const result = await firecrawl.agent({
    prompt: "Find the founders of Firecrawl",
    schema: z.object({
      founders: z.array(z.object({
        name: z.string().describe("Full name of the founder"),
        role: z.string().describe("Role or position").optional(),
        background: z.string().describe("Professional background").optional()
      })).describe("List of founders")
    }),
    model: "spark-1-mini"
  });

  console.log(result.data);
  ```

  ```bash cURL theme={null}
  curl -X POST "https://api.firecrawl.dev/v2/agent" \
    -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "prompt": "Find the founders of Firecrawl",
      "model": "spark-1-mini",
      "schema": {
        "type": "object",
        "properties": {
          "founders": {
            "type": "array",
            "description": "List of founders",
            "items": {
              "type": "object",
              "properties": {
                "name": { "type": "string", "description": "Full name" },
                "role": { "type": "string", "description": "Role or position" },
                "background": { "type": "string", "description": "Professional background" }
              },
              "required": ["name"]
            }
          }
        },
        "required": ["founders"]
      }
    }'
  ```
</CodeGroup>

### Response

```json JSON theme={null}
{
  "success": true,
  "status": "completed",
  "data": {
    "founders": [
      {
        "name": "Eric Ciarla",
        "role": "Co-founder",
        "background": "Previously at Mendable"
      },
      {
        "name": "Nicolas Camara",
        "role": "Co-founder",
        "background": "Previously at Mendable"
      },
      {
        "name": "Caleb Peffer",
        "role": "Co-founder",
        "background": "Previously at Mendable"
      }
    ]
  },
  "expiresAt": "2024-12-15T00:00:00.000Z",
  "creditsUsed": 15
}
```

## Providing URLs (Optional)

You can optionally provide URLs to focus the agent on specific pages:

<CodeGroup>
  ```python Python theme={null}
  from firecrawl import Firecrawl

  app = Firecrawl(api_key="fc-YOUR_API_KEY")

  result = app.agent(
      urls=["https://docs.firecrawl.dev", "https://firecrawl.dev/pricing"],
      prompt="Compare the features and pricing information from these pages"
  )

  print(result.data)
  ```

  ```js Node theme={null}
  import Firecrawl from '@mendable/firecrawl-js';

  const firecrawl = new Firecrawl({ apiKey: "fc-YOUR_API_KEY" });

  const result = await firecrawl.agent({
    urls: ["https://docs.firecrawl.dev", "https://firecrawl.dev/pricing"],
    prompt: "Compare the features and pricing information from these pages"
  });

  console.log(result.data);
  ```

  ```bash cURL theme={null}
  curl -X POST "https://api.firecrawl.dev/v2/agent" \
    -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "urls": [
        "https://docs.firecrawl.dev",
        "https://firecrawl.dev/pricing"
      ],
      "prompt": "Compare the features and pricing information from these pages"
    }'
  ```
</CodeGroup>

## Job Status and Completion

Agent jobs run asynchronously. When you submit a job, you'll receive a Job ID that you can use to check status:

* **Default method**: `agent()` waits and returns final results
* **Start then poll**: Use `start_agent` (Python) or `startAgent` (Node) to get a Job ID immediately, then poll with `get_agent_status` / `getAgentStatus`

<Note>Job results are available via the API for 24 hours after completion. After this period, you can still view your agent history and results in the [activity logs](https://www.firecrawl.dev/app/logs).</Note>

<CodeGroup>
  ```python Python theme={null}
  from firecrawl import Firecrawl

  app = Firecrawl(api_key="fc-YOUR_API_KEY")

  # Start an agent job
  agent_job = app.start_agent(
      prompt="Find the founders of Firecrawl"
  )

  # Check the status
  status = app.get_agent_status(agent_job.id)

  print(status)
  # Example output:
  # status='completed'
  # success=True
  # data={ ... }
  # expires_at=datetime.datetime(...)
  # credits_used=15
  ```

  ```js Node theme={null}
  import Firecrawl from '@mendable/firecrawl-js';

  const firecrawl = new Firecrawl({ apiKey: "fc-YOUR_API_KEY" });

  // Start an agent job
  const started = await firecrawl.startAgent({
    prompt: "Find the founders of Firecrawl"
  });

  // Check the status
  if (started.id) {
    const status = await firecrawl.getAgentStatus(started.id);
    console.log(status.status, status.data);
  }
  ```

  ```bash cURL theme={null}
  curl -X GET "https://api.firecrawl.dev/v2/agent/<jobId>" \
    -H "Authorization: Bearer $FIRECRAWL_API_KEY"
  ```
</CodeGroup>

### Possible States

| Status       | Description                                |
| ------------ | ------------------------------------------ |
| `processing` | The agent is still working on your request |
| `completed`  | Extraction finished successfully           |
| `failed`     | An error occurred during extraction        |

#### Pending Example

```json JSON theme={null}
{
  "success": true,
  "status": "processing",
  "expiresAt": "2024-12-15T00:00:00.000Z"
}
```

#### Completed Example

```json JSON theme={null}
{
  "success": true,
  "status": "completed",
  "data": {
    "founders": [
      {
        "name": "Eric Ciarla",
        "role": "Co-founder"
      },
      {
        "name": "Nicolas Camara",
        "role": "Co-founder"
      },
      {
        "name": "Caleb Peffer",
        "role": "Co-founder"
      }
    ]
  },
  "expiresAt": "2024-12-15T00:00:00.000Z",
  "creditsUsed": 15
}
```

## Model Selection

Firecrawl Agent offers two models. **Spark 1 Mini is 60% cheaper** and is the default — perfect for most use cases. Upgrade to Spark 1 Pro when you need maximum accuracy on complex tasks.

| Model          | Cost            | Accuracy | Best For                              |
| -------------- | --------------- | -------- | ------------------------------------- |
| `spark-1-mini` | **60% cheaper** | Standard | Most tasks (default)                  |
| `spark-1-pro`  | Standard        | Higher   | Complex research, critical extraction |

<Tip>
  **Start with Spark 1 Mini** (default) — it handles most extraction tasks well at 60% lower cost. Switch to Pro only for complex multi-domain research or when accuracy is critical.
</Tip>

### Spark 1 Mini (Default)

`spark-1-mini` is our efficient model, ideal for straightforward data extraction tasks.

**Use Mini when:**

* Extracting simple data points (contact info, pricing, etc.)
* Working with well-structured websites
* Cost efficiency is a priority
* Running high-volume extraction jobs

### Spark 1 Pro

`spark-1-pro` is our flagship model, designed for maximum accuracy on complex extraction tasks.

**Use Pro when:**

* Performing complex competitive analysis
* Extracting data that requires deep reasoning
* Accuracy is critical for your use case
* Dealing with ambiguous or hard-to-find data

### Specifying a Model

Pass the `model` parameter to select which model to use:

<CodeGroup>
  ```python Python theme={null}
  from firecrawl import Firecrawl

  app = Firecrawl(api_key="fc-YOUR_API_KEY")

  # Using Spark 1 Mini (default - can be omitted)
  result = app.agent(
      prompt="Find the pricing of Firecrawl",
      model="spark-1-mini"
  )

  # Using Spark 1 Pro for complex tasks
  result = app.agent(
      prompt="Compare all enterprise features and pricing across Firecrawl, Apify, and ScrapingBee",
      model="spark-1-pro"
  )

  print(result.data)
  ```

  ```js Node theme={null}
  import Firecrawl from '@mendable/firecrawl-js';

  const firecrawl = new Firecrawl({ apiKey: "fc-YOUR_API_KEY" });

  // Using Spark 1 Mini (default - can be omitted)
  const result = await firecrawl.agent({
    prompt: "Find the pricing of Firecrawl",
    model: "spark-1-mini"
  });

  // Using Spark 1 Pro for complex tasks
  const resultPro = await firecrawl.agent({
    prompt: "Compare all enterprise features and pricing across Firecrawl, Apify, and ScrapingBee",
    model: "spark-1-pro"
  });

  console.log(result.data);
  ```

  ```bash cURL theme={null}
  # Using Spark 1 Mini (default)
  curl -X POST "https://api.firecrawl.dev/v2/agent" \
    -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "prompt": "Find the pricing of Firecrawl",
      "model": "spark-1-mini"
    }'

  # Using Spark 1 Pro for complex tasks
  curl -X POST "https://api.firecrawl.dev/v2/agent" \
    -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "prompt": "Compare all enterprise features and pricing across Firecrawl, Apify, and ScrapingBee",
      "model": "spark-1-pro"
    }'
  ```
</CodeGroup>

## Parameters

| Parameter    | Type   | Required | Description                                                                                                                                                                              |
| ------------ | ------ | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `prompt`     | string | **Yes**  | Natural language description of the data you want to extract (max 10,000 characters)                                                                                                     |
| `model`      | string | No       | Model to use: `spark-1-mini` (default) or `spark-1-pro`                                                                                                                                  |
| `urls`       | array  | No       | Optional list of URLs to focus the extraction                                                                                                                                            |
| `schema`     | object | No       | Optional JSON schema for structured output                                                                                                                                               |
| `maxCredits` | number | No       | Maximum number of credits to spend on this agent task. If the limit is reached, the job fails and **no data is returned**, though credits consumed for work performed are still charged. |

## Agent vs Extract: What's Improved

| Feature           | Agent (New) | Extract  |
| ----------------- | ----------- | -------- |
| URLs Required     | No          | Yes      |
| Speed             | Faster      | Standard |
| Cost              | Lower       | Standard |
| Reliability       | Higher      | Standard |
| Query Flexibility | High        | Moderate |

## Example Use Cases

* **Research**: "Find the top 5 AI startups and their funding amounts"
* **Competitive Analysis**: "Compare pricing plans between Slack and Microsoft Teams"
* **Data Gathering**: "Extract contact information from company websites"
* **Content Summarization**: "Summarize the latest blog posts about web scraping"

## API Reference

Check out the [Agent API Reference](/api-reference/endpoint/agent) for more details.

Have feedback or need help? Email [help@firecrawl.com](mailto:help@firecrawl.com).

## Pricing

Firecrawl Agent uses **dynamic billing** that scales with the complexity of your data extraction request. You pay based on the actual work Agent performs, ensuring fair pricing whether you're extracting simple data points or complex structured information from multiple sources.

### How Agent pricing works

Agent pricing is **dynamic and credit-based** during Research Preview:

* **Simple extractions** (like contact info from a single page) typically use fewer credits and cost less
* **Complex research tasks** (like competitive analysis across multiple domains) use more credits but reflect the total effort involved
* **Transparent usage** shows you exactly how many credits each request consumed
* **Credit conversion** automatically converts agent credit usage to credits for easy billing

<Info>
  Credit usage varies based on the complexity of your prompt, the amount of data processed, and the structure of the output requested.
</Info>

### Parallel Agents Pricing

If you are running multiple agents in parallel with Spark-1 Fast, pricing is a lot more predictable at 10 credits per cell.

### Getting started

**All users** receive **5 free daily runs** to explore Agent's capabilities without any cost.

Additional usage is billed based on credit consumption and converted to credits.

### Managing costs

Agent can be expensive, but there are some ways to decrease the cost:

* **Start with free runs**: Use your 5 daily free requests to understand pricing
* **Set a `maxCredits` parameter**: Limit your spending by setting a maximum number of credits you're willing to spend
* **Optimize prompts**: More specific prompts often use fewer credits
* **Monitor usage**: Track your consumption through the dashboard
* **Set expectations**: Complex multi-domain research will use more credits than simple single-page extractions

Try Agent now at [firecrawl.dev/app/agent](https://www.firecrawl.dev/app/agent) to see how credit usage scales with your specific use cases.

<Note>
  Pricing is subject to change as we move from Research Preview to general availability. Current users will receive advance notice of any pricing updates.
</Note>
