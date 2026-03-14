%%{init: { 'themeVariables': { 'subgraph': { 'theme': 'default' } } }}%%

### Diagram

```mermaid
classDiagram
  classDef core fill:#f9f,stroke:#333,stroke-width:2px;
  classDef engine fill:#bbf,stroke:#333,stroke-width:2px;
  classDef db fill:#bfb,stroke:#333,stroke-width:2px;

  class Core {
    +initialize()
    +run()
  }

  class Engine {
    +execute()
  }

  class DB {
    +connect()
  }
```

### Notes

This diagram was updated to avoid parse errors caused by reserved keywords in Mermaid diagrams, specifically 'subgraph'.