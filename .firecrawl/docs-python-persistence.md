[Skip to main content](https://docs.langchain.com/oss/python/langgraph/persistence#content-area)

[Docs by LangChain home page![light logo](https://mintcdn.com/langchain-5e9cc07a/nQm-sjd_MByLhgeW/images/brand/langchain-docs-dark-blue.png?fit=max&auto=format&n=nQm-sjd_MByLhgeW&q=85&s=5babf1a1962208fd7eed942fa2432ecb)![dark logo](https://mintcdn.com/langchain-5e9cc07a/nQm-sjd_MByLhgeW/images/brand/langchain-docs-light-blue.png?fit=max&auto=format&n=nQm-sjd_MByLhgeW&q=85&s=0bcd2a1f2599ed228bcedf0f535b45b1)](https://docs.langchain.com/)

![https://mintlify.s3.us-west-1.amazonaws.com/langchain-5e9cc07a/images/brand/langchain-icon.png](https://mintlify.s3.us-west-1.amazonaws.com/langchain-5e9cc07a/images/brand/langchain-icon.png)Open source

Search...

Ctrl K

Search...

Navigation

Capabilities

Persistence

[Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview) [LangChain](https://docs.langchain.com/oss/python/langchain/overview) [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) [Integrations](https://docs.langchain.com/oss/python/integrations/providers/overview) [Learn](https://docs.langchain.com/oss/python/learn) [Reference](https://docs.langchain.com/oss/python/reference/overview) [Contribute](https://docs.langchain.com/oss/python/contributing/overview)

Python

- [Overview](https://docs.langchain.com/oss/python/langgraph/overview)

##### Get started

- [Install](https://docs.langchain.com/oss/python/langgraph/install)
- [Quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart)
- [Local server](https://docs.langchain.com/oss/python/langgraph/local-server)
- [Changelog](https://docs.langchain.com/oss/python/releases/changelog)
- [Thinking in LangGraph](https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph)
- [Workflows + agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents)

##### Capabilities

- [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [Durable execution](https://docs.langchain.com/oss/python/langgraph/durable-execution)
- [Streaming](https://docs.langchain.com/oss/python/langgraph/streaming)
- [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
- [Time travel](https://docs.langchain.com/oss/python/langgraph/use-time-travel)
- [Memory](https://docs.langchain.com/oss/python/langgraph/add-memory)
- [Subgraphs](https://docs.langchain.com/oss/python/langgraph/use-subgraphs)

##### Production

- [Application structure](https://docs.langchain.com/oss/python/langgraph/application-structure)
- [Test](https://docs.langchain.com/oss/python/langgraph/test)
- [LangSmith Studio](https://docs.langchain.com/oss/python/langgraph/studio)
- [Agent Chat UI](https://docs.langchain.com/oss/python/langgraph/ui)
- [LangSmith Deployment](https://docs.langchain.com/oss/python/langgraph/deploy)
- [LangSmith Observability](https://docs.langchain.com/oss/python/langgraph/observability)

##### LangGraph APIs

- Graph API

- Functional API

- [Runtime](https://docs.langchain.com/oss/python/langgraph/pregel)

On this page

- [Threads](https://docs.langchain.com/oss/python/langgraph/persistence#threads)
- [Checkpoints](https://docs.langchain.com/oss/python/langgraph/persistence#checkpoints)
- [Get state](https://docs.langchain.com/oss/python/langgraph/persistence#get-state)
- [Get state history](https://docs.langchain.com/oss/python/langgraph/persistence#get-state-history)
- [Replay](https://docs.langchain.com/oss/python/langgraph/persistence#replay)
- [Update state](https://docs.langchain.com/oss/python/langgraph/persistence#update-state)
- [config](https://docs.langchain.com/oss/python/langgraph/persistence#config)
- [values](https://docs.langchain.com/oss/python/langgraph/persistence#values)
- [as\_node](https://docs.langchain.com/oss/python/langgraph/persistence#as_node)
- [Memory store](https://docs.langchain.com/oss/python/langgraph/persistence#memory-store)
- [Basic usage](https://docs.langchain.com/oss/python/langgraph/persistence#basic-usage)
- [Semantic search](https://docs.langchain.com/oss/python/langgraph/persistence#semantic-search)
- [Using in LangGraph](https://docs.langchain.com/oss/python/langgraph/persistence#using-in-langgraph)
- [Checkpointer libraries](https://docs.langchain.com/oss/python/langgraph/persistence#checkpointer-libraries)
- [Checkpointer interface](https://docs.langchain.com/oss/python/langgraph/persistence#checkpointer-interface)
- [Serializer](https://docs.langchain.com/oss/python/langgraph/persistence#serializer)
- [Serialization with pickle](https://docs.langchain.com/oss/python/langgraph/persistence#serialization-with-pickle)
- [Encryption](https://docs.langchain.com/oss/python/langgraph/persistence#encryption)
- [Capabilities](https://docs.langchain.com/oss/python/langgraph/persistence#capabilities)
- [Human-in-the-loop](https://docs.langchain.com/oss/python/langgraph/persistence#human-in-the-loop)
- [Memory](https://docs.langchain.com/oss/python/langgraph/persistence#memory)
- [Time travel](https://docs.langchain.com/oss/python/langgraph/persistence#time-travel)
- [Fault-tolerance](https://docs.langchain.com/oss/python/langgraph/persistence#fault-tolerance)
- [Pending writes](https://docs.langchain.com/oss/python/langgraph/persistence#pending-writes)

LangGraph has a built-in persistence layer, implemented through checkpointers. When you compile a graph with a checkpointer, the checkpointer saves a `checkpoint` of the graph state at every super-step. Those checkpoints are saved to a `thread`, which can be accessed after graph execution. Because `threads` allow access to graph’s state after execution, several powerful capabilities including human-in-the-loop, memory, time travel, and fault-tolerance are all possible. Below, we’ll discuss each of these concepts in more detail.![Checkpoints](https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/checkpoints.jpg?fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=966566aaae853ed4d240c2d0d067467c)

**Agent Server handles checkpointing automatically**
When using the [Agent Server](https://docs.langchain.com/langsmith/agent-server), you don’t need to implement or configure checkpointers manually. The server handles all persistence infrastructure for you behind the scenes.

## [​](https://docs.langchain.com/oss/python/langgraph/persistence\#threads)  Threads

A thread is a unique ID or thread identifier assigned to each checkpoint saved by a checkpointer. It contains the accumulated state of a sequence of [runs](https://docs.langchain.com/langsmith/assistants#execution). When a run is executed, the [state](https://docs.langchain.com/oss/python/langgraph/graph-api#state) of the underlying graph of the assistant will be persisted to the thread.When invoking a graph with a checkpointer, you **must** specify a `thread_id` as part of the `configurable` portion of the config:

Copy

```
{"configurable": {"thread_id": "1"}}
```

A thread’s current and historical state can be retrieved. To persist state, a thread must be created prior to executing a run. The LangSmith API provides several endpoints for creating and managing threads and thread state. See the [API reference](https://reference.langchain.com/python/langsmith/) for more details.The checkpointer uses `thread_id` as the primary key for storing and retrieving checkpoints. Without it, the checkpointer cannot save state or resume execution after an [interrupt](https://docs.langchain.com/oss/python/langgraph/interrupts), since the checkpointer uses `thread_id` to load the saved state.

## [​](https://docs.langchain.com/oss/python/langgraph/persistence\#checkpoints)  Checkpoints

The state of a thread at a particular point in time is called a checkpoint. Checkpoint is a snapshot of the graph state saved at each super-step and is represented by `StateSnapshot` object with the following key properties:

- `config`: Config associated with this checkpoint.
- `metadata`: Metadata associated with this checkpoint.
- `values`: Values of the state channels at this point in time.
- `next` A tuple of the node names to execute next in the graph.
- `tasks`: A tuple of `PregelTask` objects that contain information about next tasks to be executed. If the step was previously attempted, it will include error information. If a graph was interrupted [dynamically](https://docs.langchain.com/oss/python/langgraph/interrupts#pause-using-interrupt) from within a node, tasks will contain additional data associated with interrupts.

Checkpoints are persisted and can be used to restore the state of a thread at a later time.Let’s see what checkpoints are saved when a simple graph is invoked as follows:

Copy

```
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig
from typing import Annotated
from typing_extensions import TypedDict
from operator import add

class State(TypedDict):
    foo: str
    bar: Annotated[list[str], add]

def node_a(state: State):
    return {"foo": "a", "bar": ["a"]}

def node_b(state: State):
    return {"foo": "b", "bar": ["b"]}

workflow = StateGraph(State)
workflow.add_node(node_a)
workflow.add_node(node_b)
workflow.add_edge(START, "node_a")
workflow.add_edge("node_a", "node_b")
workflow.add_edge("node_b", END)

checkpointer = InMemorySaver()
graph = workflow.compile(checkpointer=checkpointer)

config: RunnableConfig = {"configurable": {"thread_id": "1"}}
graph.invoke({"foo": "", "bar":[]}, config)
```

After we run the graph, we expect to see exactly 4 checkpoints:

- Empty checkpoint with [`START`](https://reference.langchain.com/python/langgraph/constants/START) as the next node to be executed
- Checkpoint with the user input `{'foo': '', 'bar': []}` and `node_a` as the next node to be executed
- Checkpoint with the outputs of `node_a``{'foo': 'a', 'bar': ['a']}` and `node_b` as the next node to be executed
- Checkpoint with the outputs of `node_b``{'foo': 'b', 'bar': ['a', 'b']}` and no next nodes to be executed

Note that we `bar` channel values contain outputs from both nodes as we have a reducer for `bar` channel.

### [​](https://docs.langchain.com/oss/python/langgraph/persistence\#get-state)  Get state

When interacting with the saved graph state, you **must** specify a [thread identifier](https://docs.langchain.com/oss/python/langgraph/persistence#threads). You can view the _latest_ state of the graph by calling `graph.get_state(config)`. This will return a `StateSnapshot` object that corresponds to the latest checkpoint associated with the thread ID provided in the config or a checkpoint associated with a checkpoint ID for the thread, if provided.

Copy

```
# get the latest state snapshot
config = {"configurable": {"thread_id": "1"}}
graph.get_state(config)

# get a state snapshot for a specific checkpoint_id
config = {"configurable": {"thread_id": "1", "checkpoint_id": "1ef663ba-28fe-6528-8002-5a559208592c"}}
graph.get_state(config)
```

In our example, the output of `get_state` will look like this:

Copy

```
StateSnapshot(
    values={'foo': 'b', 'bar': ['a', 'b']},
    next=(),
    config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1ef663ba-28fe-6528-8002-5a559208592c'}},
    metadata={'source': 'loop', 'writes': {'node_b': {'foo': 'b', 'bar': ['b']}}, 'step': 2},
    created_at='2024-08-29T19:19:38.821749+00:00',
    parent_config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1ef663ba-28f9-6ec4-8001-31981c2c39f8'}}, tasks=()
)
```

### [​](https://docs.langchain.com/oss/python/langgraph/persistence\#get-state-history)  Get state history

You can get the full history of the graph execution for a given thread by calling [`graph.get_state_history(config)`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.get_state_history). This will return a list of `StateSnapshot` objects associated with the thread ID provided in the config. Importantly, the checkpoints will be ordered chronologically with the most recent checkpoint / `StateSnapshot` being the first in the list.

Copy

```
config = {"configurable": {"thread_id": "1"}}
list(graph.get_state_history(config))
```

In our example, the output of [`get_state_history`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.get_state_history) will look like this:

Copy

```
[\
    StateSnapshot(\
        values={'foo': 'b', 'bar': ['a', 'b']},\
        next=(),\
        config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1ef663ba-28fe-6528-8002-5a559208592c'}},\
        metadata={'source': 'loop', 'writes': {'node_b': {'foo': 'b', 'bar': ['b']}}, 'step': 2},\
        created_at='2024-08-29T19:19:38.821749+00:00',\
        parent_config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1ef663ba-28f9-6ec4-8001-31981c2c39f8'}},\
        tasks=(),\
    ),\
    StateSnapshot(\
        values={'foo': 'a', 'bar': ['a']},\
        next=('node_b',),\
        config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1ef663ba-28f9-6ec4-8001-31981c2c39f8'}},\
        metadata={'source': 'loop', 'writes': {'node_a': {'foo': 'a', 'bar': ['a']}}, 'step': 1},\
        created_at='2024-08-29T19:19:38.819946+00:00',\
        parent_config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1ef663ba-28f4-6b4a-8000-ca575a13d36a'}},\
        tasks=(PregelTask(id='6fb7314f-f114-5413-a1f3-d37dfe98ff44', name='node_b', error=None, interrupts=()),),\
    ),\
    StateSnapshot(\
        values={'foo': '', 'bar': []},\
        next=('node_a',),\
        config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1ef663ba-28f4-6b4a-8000-ca575a13d36a'}},\
        metadata={'source': 'loop', 'writes': None, 'step': 0},\
        created_at='2024-08-29T19:19:38.817813+00:00',\
        parent_config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1ef663ba-28f0-6c66-bfff-6723431e8481'}},\
        tasks=(PregelTask(id='f1b14528-5ee5-579c-949b-23ef9bfbed58', name='node_a', error=None, interrupts=()),),\
    ),\
    StateSnapshot(\
        values={'bar': []},\
        next=('__start__',),\
        config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1ef663ba-28f0-6c66-bfff-6723431e8481'}},\
        metadata={'source': 'input', 'writes': {'foo': ''}, 'step': -1},\
        created_at='2024-08-29T19:19:38.816205+00:00',\
        parent_config=None,\
        tasks=(PregelTask(id='6d27aa2e-d72b-5504-a36f-8620e54a76dd', name='__start__', error=None, interrupts=()),),\
    )\
]
```

![State](https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/get_state.jpg?fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=38ffff52be4d8806b287836295a3c058)

### [​](https://docs.langchain.com/oss/python/langgraph/persistence\#replay)  Replay

It’s also possible to play-back a prior graph execution. If we `invoke` a graph with a `thread_id` and a `checkpoint_id`, then we will _re-play_ the previously executed steps _before_ a checkpoint that corresponds to the `checkpoint_id`, and only execute the steps _after_ the checkpoint.

- `thread_id` is the ID of a thread.
- `checkpoint_id` is an identifier that refers to a specific checkpoint within a thread.

You must pass these when invoking the graph as part of the `configurable` portion of the config:

Copy

```
config = {"configurable": {"thread_id": "1", "checkpoint_id": "0c62ca34-ac19-445d-bbb0-5b4984975b2a"}}
graph.invoke(None, config=config)
```

Importantly, LangGraph knows whether a particular step has been executed previously. If it has, LangGraph simply _re-plays_ that particular step in the graph and does not re-execute the step, but only for the steps _before_ the provided `checkpoint_id`. All of the steps _after_`checkpoint_id` will be executed (i.e., a new fork), even if they have been executed previously. See this [how to guide on time-travel to learn more about replaying](https://docs.langchain.com/oss/python/langgraph/use-time-travel).![Replay](https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/re_play.png?fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=d7b34b85c106e55d181ae1f4afb50251)

### [​](https://docs.langchain.com/oss/python/langgraph/persistence\#update-state)  Update state

In addition to re-playing the graph from specific `checkpoints`, we can also _edit_ the graph state. We do this using [`update_state`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.update_state). This method accepts three different arguments:

#### [​](https://docs.langchain.com/oss/python/langgraph/persistence\#config)  `config`

The config should contain `thread_id` specifying which thread to update. When only the `thread_id` is passed, we update (or fork) the current state. Optionally, if we include `checkpoint_id` field, then we fork that selected checkpoint.

#### [​](https://docs.langchain.com/oss/python/langgraph/persistence\#values)  `values`

These are the values that will be used to update the state. Note that this update is treated exactly as any update from a node is treated. This means that these values will be passed to the [reducer](https://docs.langchain.com/oss/python/langgraph/graph-api#reducers) functions, if they are defined for some of the channels in the graph state. This means that [`update_state`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.update_state) does NOT automatically overwrite the channel values for every channel, but only for the channels without reducers. Let’s walk through an example.Let’s assume you have defined the state of your graph with the following schema (see full example above):

Copy

```
from typing import Annotated
from typing_extensions import TypedDict
from operator import add

class State(TypedDict):
    foo: int
    bar: Annotated[list[str], add]
```

Let’s now assume the current state of the graph is

Copy

```
{"foo": 1, "bar": ["a"]}
```

If you update the state as below:

Copy

```
graph.update_state(config, {"foo": 2, "bar": ["b"]})
```

Then the new state of the graph will be:

Copy

```
{"foo": 2, "bar": ["a", "b"]}
```

The `foo` key (channel) is completely changed (because there is no reducer specified for that channel, so [`update_state`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.update_state) overwrites it). However, there is a reducer specified for the `bar` key, and so it appends `"b"` to the state of `bar`.

#### [​](https://docs.langchain.com/oss/python/langgraph/persistence\#as_node)  `as_node`

The final thing you can optionally specify when calling [`update_state`](https://reference.langchain.com/python/langgraph/graphs/#langgraph.graph.state.CompiledStateGraph.update_state) is `as_node`. If you provided it, the update will be applied as if it came from node `as_node`. If `as_node` is not provided, it will be set to the last node that updated the state, if not ambiguous. The reason this matters is that the next steps to execute depend on the last node to have given an update, so this can be used to control which node executes next. See this [how to guide on time-travel to learn more about forking state](https://docs.langchain.com/oss/python/langgraph/use-time-travel).![Update](https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/checkpoints_full_story.jpg?fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=a52016b2c44b57bd395d6e1eac47aa36)

## [​](https://docs.langchain.com/oss/python/langgraph/persistence\#memory-store)  Memory store

![Model of shared state](https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/shared_state.png?fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=354526fb48c5eb11b4b2684a2df40d6c)A [state schema](https://docs.langchain.com/oss/python/langgraph/graph-api#schema) specifies a set of keys that are populated as a graph is executed. As discussed above, state can be written by a checkpointer to a thread at each graph step, enabling state persistence.But, what if we want to retain some information _across threads_? Consider the case of a chatbot where we want to retain specific information about the user across _all_ chat conversations (e.g., threads) with that user!With checkpointers alone, we cannot share information across threads. This motivates the need for the [`Store`](https://reference.langchain.com/python/langgraph/store/) interface. As an illustration, we can define an `InMemoryStore` to store information about a user across threads. We simply compile our graph with a checkpointer, as before, and pass the store.

**LangGraph API handles stores automatically**
When using the LangGraph API, you don’t need to implement or configure stores manually. The API handles all storage infrastructure for you behind the scenes.

[InMemoryStore](https://reference.langchain.com/python/langchain-core/stores/InMemoryStore) is suitable for development and testing. For production, use a persistent store like `PostgresStore` or `RedisStore`. All implementations extend [BaseStore](https://reference.langchain.com/python/langchain-core/stores/BaseStore), which is the type annotation to use in node function signatures.

### [​](https://docs.langchain.com/oss/python/langgraph/persistence\#basic-usage)  Basic usage

First, let’s showcase this in isolation without using LangGraph.

Copy

```
from langgraph.store.memory import InMemoryStore
store = InMemoryStore()
```

Memories are namespaced by a `tuple`, which in this specific example will be `(<user_id>, "memories")`. The namespace can be any length and represent anything, does not have to be user specific.

Copy

```
user_id = "1"
namespace_for_memory = (user_id, "memories")
```

We use the `store.put` method to save memories to our namespace in the store. When we do this, we specify the namespace, as defined above, and a key-value pair for the memory: the key is simply a unique identifier for the memory (`memory_id`) and the value (a dictionary) is the memory itself.

Copy

```
memory_id = str(uuid.uuid4())
memory = {"food_preference" : "I like pizza"}
store.put(namespace_for_memory, memory_id, memory)
```

We can read out memories in our namespace using the `store.search` method, which will return all memories for a given user as a list. The most recent memory is the last in the list.

Copy

```
memories = store.search(namespace_for_memory)
memories[-1].dict()
{'value': {'food_preference': 'I like pizza'},
 'key': '07e0caf4-1631-47b7-b15f-65515d4c1843',
 'namespace': ['1', 'memories'],
 'created_at': '2024-10-02T17:22:31.590602+00:00',
 'updated_at': '2024-10-02T17:22:31.590605+00:00'}
```

Each memory type is a Python class ( [`Item`](https://langchain-ai.github.io/langgraph/reference/store/#langgraph.store.base.Item)) with certain attributes. We can access it as a dictionary by converting via `.dict` as above.The attributes it has are:

- `value`: The value (itself a dictionary) of this memory
- `key`: A unique key for this memory in this namespace
- `namespace`: A tuple of strings, the namespace of this memory type






While the type is `tuple[str, ...]`, it may be serialized as a list when converted to JSON (for example, `['1', 'memories']`).

- `created_at`: Timestamp for when this memory was created
- `updated_at`: Timestamp for when this memory was updated

### [​](https://docs.langchain.com/oss/python/langgraph/persistence\#semantic-search)  Semantic search

Beyond simple retrieval, the store also supports semantic search, allowing you to find memories based on meaning rather than exact matches. To enable this, configure the store with an embedding model:

Copy

```
from langchain.embeddings import init_embeddings

store = InMemoryStore(
    index={
        "embed": init_embeddings("openai:text-embedding-3-small"),  # Embedding provider
        "dims": 1536,                              # Embedding dimensions
        "fields": ["food_preference", "$"]              # Fields to embed
    }
)
```

Now when searching, you can use natural language queries to find relevant memories:

Copy

```
# Find memories about food preferences
# (This can be done after putting memories into the store)
memories = store.search(
    namespace_for_memory,
    query="What does the user like to eat?",
    limit=3  # Return top 3 matches
)
```

You can control which parts of your memories get embedded by configuring the `fields` parameter or by specifying the `index` parameter when storing memories:

Copy

```
# Store with specific fields to embed
store.put(
    namespace_for_memory,
    str(uuid.uuid4()),
    {
        "food_preference": "I love Italian cuisine",
        "context": "Discussing dinner plans"
    },
    index=["food_preference"]  # Only embed "food_preferences" field
)

# Store without embedding (still retrievable, but not searchable)
store.put(
    namespace_for_memory,
    str(uuid.uuid4()),
    {"system_info": "Last updated: 2024-01-01"},
    index=False
)
```

### [​](https://docs.langchain.com/oss/python/langgraph/persistence\#using-in-langgraph)  Using in LangGraph

With this all in place, we use the store in LangGraph. The store works hand-in-hand with the checkpointer: the checkpointer saves state to threads, as discussed above, and the store allows us to store arbitrary information for access _across_ threads. We compile the graph with both the checkpointer and the store as follows.

Copy

```
from dataclasses import dataclass
from langgraph.checkpoint.memory import InMemorySaver

@dataclass
class Context:
    user_id: str

# We need this because we want to enable threads (conversations)
checkpointer = InMemorySaver()

# ... Define the graph ...

# Compile the graph with the checkpointer and store
builder = StateGraph(MessagesState, context_schema=Context)
# ... add nodes and edges ...
graph = builder.compile(checkpointer=checkpointer, store=store)
```

We invoke the graph with a `thread_id`, as before, and also with a `user_id`, which we’ll use to namespace our memories to this particular user as we showed above.

Copy

```
# Invoke the graph
config = {"configurable": {"thread_id": "1"}}

# First let's just say hi to the AI
for update in graph.stream(
    {"messages": [{"role": "user", "content": "hi"}]},
    config,
    stream_mode="updates",
    context=Context(user_id="1"),
):
    print(update)
```

You can access the store and the `user_id` in _any node_ by using the `Runtime` object. The `Runtime` is automatically injected by LangGraph when you add it as a parameter to your node function. Here’s how you might use it to save memories:

Copy

```
from langgraph.runtime import Runtime
from dataclasses import dataclass

@dataclass
class Context:
    user_id: str

async def update_memory(state: MessagesState, runtime: Runtime[Context]):

    # Get the user id from the runtime context
    user_id = runtime.context.user_id

    # Namespace the memory
    namespace = (user_id, "memories")

    # ... Analyze conversation and create a new memory

    # Create a new memory ID
    memory_id = str(uuid.uuid4())

    # We create a new memory
    await runtime.store.aput(namespace, memory_id, {"memory": memory})
```

As we showed above, we can also access the store in any node and use the `store.search` method to get memories. Recall the memories are returned as a list of objects that can be converted to a dictionary.

Copy

```
memories[-1].dict()
{'value': {'food_preference': 'I like pizza'},
 'key': '07e0caf4-1631-47b7-b15f-65515d4c1843',
 'namespace': ['1', 'memories'],
 'created_at': '2024-10-02T17:22:31.590602+00:00',
 'updated_at': '2024-10-02T17:22:31.590605+00:00'}
```

We can access the memories and use them in our model call.

Copy

```
from dataclasses import dataclass
from langgraph.runtime import Runtime

@dataclass
class Context:
    user_id: str

async def call_model(state: MessagesState, runtime: Runtime[Context]):
    # Get the user id from the runtime context
    user_id = runtime.context.user_id

    # Namespace the memory
    namespace = (user_id, "memories")

    # Search based on the most recent message
    memories = await runtime.store.asearch(
        namespace,
        query=state["messages"][-1].content,
        limit=3
    )
    info = "\n".join([d.value["memory"] for d in memories])

    # ... Use memories in the model call
```

If we create a new thread, we can still access the same memories so long as the `user_id` is the same.

Copy

```
# Invoke the graph on a new thread
config = {"configurable": {"thread_id": "2"}}

# Let's say hi again
for update in graph.stream(
    {"messages": [{"role": "user", "content": "hi, tell me about my memories"}]},
    config,
    stream_mode="updates",
    context=Context(user_id="1"),
):
    print(update)
```

When we use the LangSmith, either locally (e.g., in [Studio](https://docs.langchain.com/langsmith/studio)) or [hosted with LangSmith](https://docs.langchain.com/langsmith/platform-setup), the base store is available to use by default and does not need to be specified during graph compilation. To enable semantic search, however, you **do** need to configure the indexing settings in your `langgraph.json` file. For example:

Copy

```
{
    ...
    "store": {
        "index": {
            "embed": "openai:text-embeddings-3-small",
            "dims": 1536,
            "fields": ["$"]
        }
    }
}
```

See the [deployment guide](https://docs.langchain.com/langsmith/semantic-search) for more details and configuration options.

## [​](https://docs.langchain.com/oss/python/langgraph/persistence\#checkpointer-libraries)  Checkpointer libraries

Under the hood, checkpointing is powered by checkpointer objects that conform to [`BaseCheckpointSaver`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.base.BaseCheckpointSaver) interface. LangGraph provides several checkpointer implementations, all implemented via standalone, installable libraries:

- `langgraph-checkpoint`: The base interface for checkpointer savers ( [`BaseCheckpointSaver`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.base.BaseCheckpointSaver)) and serialization/deserialization interface ( [`SerializerProtocol`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.serde.base.SerializerProtocol)). Includes in-memory checkpointer implementation ( [`InMemorySaver`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.memory.InMemorySaver)) for experimentation. LangGraph comes with `langgraph-checkpoint` included.
- `langgraph-checkpoint-sqlite`: An implementation of LangGraph checkpointer that uses SQLite database ( [`SqliteSaver`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.sqlite.SqliteSaver) / [`AsyncSqliteSaver`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver)). Ideal for experimentation and local workflows. Needs to be installed separately.
- `langgraph-checkpoint-postgres`: An advanced checkpointer that uses Postgres database ( [`PostgresSaver`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.postgres.PostgresSaver) / [`AsyncPostgresSaver`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver)), used in LangSmith. Ideal for using in production. Needs to be installed separately.
- `langgraph-checkpoint-cosmosdb`: An implementation of LangGraph checkpointer that uses Azure Cosmos DB (@\[`CosmosDBSaver`\] / @\[`AsyncCosmosDBSaver`\]). Ideal for using in production with Azure. Supports both sync and async operations. Needs to be installed separately.

### [​](https://docs.langchain.com/oss/python/langgraph/persistence\#checkpointer-interface)  Checkpointer interface

Each checkpointer conforms to [`BaseCheckpointSaver`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.base.BaseCheckpointSaver) interface and implements the following methods:

- `.put` \- Store a checkpoint with its configuration and metadata.
- `.put_writes` \- Store intermediate writes linked to a checkpoint (i.e. [pending writes](https://docs.langchain.com/oss/python/langgraph/persistence#pending-writes)).
- `.get_tuple` \- Fetch a checkpoint tuple using for a given configuration (`thread_id` and `checkpoint_id`). This is used to populate `StateSnapshot` in `graph.get_state()`.
- `.list` \- List checkpoints that match a given configuration and filter criteria. This is used to populate state history in `graph.get_state_history()`

If the checkpointer is used with asynchronous graph execution (i.e. executing the graph via `.ainvoke`, `.astream`, `.abatch`), asynchronous versions of the above methods will be used (`.aput`, `.aput_writes`, `.aget_tuple`, `.alist`).

For running your graph asynchronously, you can use [`InMemorySaver`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.memory.InMemorySaver), or async versions of Sqlite/Postgres checkpointers — [`AsyncSqliteSaver`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver) / [`AsyncPostgresSaver`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver) checkpointers.

### [​](https://docs.langchain.com/oss/python/langgraph/persistence\#serializer)  Serializer

When checkpointers save the graph state, they need to serialize the channel values in the state. This is done using serializer objects.`langgraph_checkpoint` defines [protocol](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.serde.base.SerializerProtocol) for implementing serializers provides a default implementation ( [`JsonPlusSerializer`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.serde.jsonplus.JsonPlusSerializer)) that handles a wide variety of types, including LangChain and LangGraph primitives, datetimes, enums and more.

#### [​](https://docs.langchain.com/oss/python/langgraph/persistence\#serialization-with-pickle)  Serialization with `pickle`

The default serializer, [`JsonPlusSerializer`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.serde.jsonplus.JsonPlusSerializer), uses ormsgpack and JSON under the hood, which is not suitable for all types of objects.If you want to fallback to pickle for objects not currently supported by our msgpack encoder (such as Pandas dataframes),
you can use the `pickle_fallback` argument of the [`JsonPlusSerializer`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.serde.jsonplus.JsonPlusSerializer):

Copy

```
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

# ... Define the graph ...
graph.compile(
    checkpointer=InMemorySaver(serde=JsonPlusSerializer(pickle_fallback=True))
)
```

#### [​](https://docs.langchain.com/oss/python/langgraph/persistence\#encryption)  Encryption

Checkpointers can optionally encrypt all persisted state. To enable this, pass an instance of [`EncryptedSerializer`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.serde.encrypted.EncryptedSerializer) to the `serde` argument of any [`BaseCheckpointSaver`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.base.BaseCheckpointSaver) implementation. The easiest way to create an encrypted serializer is via [`from_pycryptodome_aes`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.serde.encrypted.EncryptedSerializer.from_pycryptodome_aes), which reads the AES key from the `LANGGRAPH_AES_KEY` environment variable (or accepts a `key` argument):

Copy

```
import sqlite3

from langgraph.checkpoint.serde.encrypted import EncryptedSerializer
from langgraph.checkpoint.sqlite import SqliteSaver

serde = EncryptedSerializer.from_pycryptodome_aes()  # reads LANGGRAPH_AES_KEY
checkpointer = SqliteSaver(sqlite3.connect("checkpoint.db"), serde=serde)
```

Copy

```
from langgraph.checkpoint.serde.encrypted import EncryptedSerializer
from langgraph.checkpoint.postgres import PostgresSaver

serde = EncryptedSerializer.from_pycryptodome_aes()
checkpointer = PostgresSaver.from_conn_string("postgresql://...", serde=serde)
checkpointer.setup()
```

When running on LangSmith, encryption is automatically enabled whenever `LANGGRAPH_AES_KEY` is present, so you only need to provide the environment variable. Other encryption schemes can be used by implementing [`CipherProtocol`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.serde.base.CipherProtocol) and supplying it to [`EncryptedSerializer`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.serde.encrypted.EncryptedSerializer).

## [​](https://docs.langchain.com/oss/python/langgraph/persistence\#capabilities)  Capabilities

### [​](https://docs.langchain.com/oss/python/langgraph/persistence\#human-in-the-loop)  Human-in-the-loop

First, checkpointers facilitate [human-in-the-loop workflows](https://docs.langchain.com/oss/python/langgraph/interrupts) by allowing humans to inspect, interrupt, and approve graph steps. Checkpointers are needed for these workflows as the human has to be able to view the state of a graph at any point in time, and the graph has to be to resume execution after the human has made any updates to the state. See [the how-to guides](https://docs.langchain.com/oss/python/langgraph/interrupts) for examples.

### [​](https://docs.langchain.com/oss/python/langgraph/persistence\#memory)  Memory

Second, checkpointers allow for [“memory”](https://docs.langchain.com/oss/python/concepts/memory) between interactions. In the case of repeated human interactions (like conversations) any follow up messages can be sent to that thread, which will retain its memory of previous ones. See [Add memory](https://docs.langchain.com/oss/python/langgraph/add-memory) for information on how to add and manage conversation memory using checkpointers.

### [​](https://docs.langchain.com/oss/python/langgraph/persistence\#time-travel)  Time travel

Third, checkpointers allow for [“time travel”](https://docs.langchain.com/oss/python/langgraph/use-time-travel), allowing users to replay prior graph executions to review and / or debug specific graph steps. In addition, checkpointers make it possible to fork the graph state at arbitrary checkpoints to explore alternative trajectories.

### [​](https://docs.langchain.com/oss/python/langgraph/persistence\#fault-tolerance)  Fault-tolerance

Lastly, checkpointing also provides fault-tolerance and error recovery: if one or more nodes fail at a given superstep, you can restart your graph from the last successful step. Additionally, when a graph node fails mid-execution at a given superstep, LangGraph stores pending checkpoint writes from any other nodes that completed successfully at that superstep, so that whenever we resume graph execution from that superstep we don’t re-run the successful nodes.

#### [​](https://docs.langchain.com/oss/python/langgraph/persistence\#pending-writes)  Pending writes

Additionally, when a graph node fails mid-execution at a given superstep, LangGraph stores pending checkpoint writes from any other nodes that completed successfully at that superstep, so that whenever we resume graph execution from that superstep we don’t re-run the successful nodes.

* * *

[Edit this page on GitHub](https://github.com/langchain-ai/docs/edit/main/src/oss/langgraph/persistence.mdx) or [file an issue](https://github.com/langchain-ai/docs/issues/new/choose).

[Connect these docs](https://docs.langchain.com/use-these-docs) to Claude, VSCode, and more via MCP for real-time answers.

Was this page helpful?

YesNo

[Workflows and agents\\
\\
Previous](https://docs.langchain.com/oss/python/langgraph/workflows-agents) [Durable execution\\
\\
Next](https://docs.langchain.com/oss/python/langgraph/durable-execution)

Ctrl+I

![Checkpoints](https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/checkpoints.jpg?w=840&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=46a2f9ed3b131a7c78700711e8c314d6)

![State](https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/get_state.jpg?w=840&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=0ac091c7dbe8b1f0acff97615a3683ee)

![Replay](https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/re_play.png?w=840&fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=7cc304a2a0996e22f783e9a5f7a69f89)

![Update](https://mintcdn.com/langchain-5e9cc07a/-_xGPoyjhyiDWTPJ/oss/images/checkpoints_full_story.jpg?w=840&fit=max&auto=format&n=-_xGPoyjhyiDWTPJ&q=85&s=58cfc0341a77e179ce443a89d667784c)

![Model of shared state](https://mintcdn.com/langchain-5e9cc07a/dL5Sn6Cmy9pwtY0V/oss/images/shared_state.png?w=840&fit=max&auto=format&n=dL5Sn6Cmy9pwtY0V&q=85&s=4ef92e64d1151922511c78afde7abdca)