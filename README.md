# SchemaLens as a summary
ScehmaLens is an Enterprise Schema Discovery &amp; Governance Middleware Gateway designed to sit between autonomous AI agents and enterprise relational databases.

# What does SchemaLens do?

A lightweight, middleware lying, FastAPI based program that acts as an opaque mediator between the the communication of the agent and a relational database.
Instead of dumping the entire schema, the agent calls an introspective discovery tool for specific entities (e.g., claimants, disbursements). It returns only the targeted column definitions, data types, and primary/foreign keys.  

SchemaLens also acts as a security layer, possessing the abililty to validate incoming SQL using AST parsing to only permit 'SELECT' statements and blocking destructive commands that an agent should NEVER call (DROP, DELETE, UPDATE, ALTER). It additionally enforces row limits, configurable to scaling needs.

SchemaLens uses FastAPI's native /docs interface as a clean, interactive console and runs side-by-side benchmarking comparing an unoptimized full-schema dump against the targeted discovery tool, showing live token savings, latency metrics, and safety checks without needing a fragile frontend.

# What does it Solve?

Framed around the real-world challenges of incorportating agentic services to pre-existing architecture; when enterprise clients wish to adopt AI powered analytics tools, they run into three severe blockers.

  1. **Context Window Bloat**: Full database DDLS and catalog schemas can oversaturate an LLM and flood the context window with tens of thousands of uneccessary tokens per query. This causes not only high latency, but is finanically unsustainable along with looping "grep cascades"
  2. **Infrastructure Instability**: Agents that maintain an open and direct connection to databases face the very prevelant of socket leaks and connection exhaustion. The longer the session is held, the more prominent these issues become.
  3. **Safety**: Generative models always have the capability to hallucinate or be hi-jacked by malicious prompt engineering. In any case, without proper infrastructure-level interception, an agent can run rampant with destructive or harmful queries. These are in violation of core security principles, namely Confidentiality and Integritiy. 

  
