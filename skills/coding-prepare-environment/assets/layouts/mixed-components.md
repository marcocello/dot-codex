# Mixed components

Use named components when a supplied full-stack application and separately maintained integrations do not fit a simple frontend/backend split. For a website with a chat integration and retrieval workflows:

```text
project/
├── website/
│   ├── Dockerfile
│   ├── config/
│   └── www/                   # Supplied full-stack application; ignored if private
├── ask-assistant/
│   ├── frontend/              # Widget source, templates, manifest, and browser tests
│   ├── gateway/               # Server endpoint and its installation
│   ├── tests/                 # Integration checks
│   ├── tools/                 # Optional preview and integration diagnostics
│   └── Dockerfile
├── retrieval-api/
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   ├── tools/
│   └── Dockerfile
├── n8n-workflows/
│   ├── workflows/             # Definitions and generators
│   ├── installer/             # API import and publication logic
│   ├── tests/
│   └── Dockerfile
├── deployments/
│   ├── local/
│   │   ├── compose.yml        # Assembly
│   │   ├── website.yml
│   │   ├── ask-assistant.yml
│   │   ├── retrieval-api.yml
│   │   └── n8n-workflows.yml
│   └── prod/                 # Corresponding production assembly and configuration
├── docs/
├── .vscode/tasks.json
└── .gitignore
```

`website/` owns the original application and its runtime. It includes frontend presentation and server logic. `ask-assistant/` owns the added widget and PHP gateway, although the installed gateway executes in the website's container. Keep integration installers and preview utilities with that integration. The retrieval API owns parsing, retrieval, dependencies, and diagnostics. Workflow definitions, generators, and installation belong together in `n8n-workflows/`.

`deployments/` selects components, connects networks, orders setup jobs, and configures data mounts or built images. It can use standard database images without inventing source components for them. Modular Compose files are useful when they clarify the assembly; smaller projects can keep one Compose file per environment. An evaluation API or shared configuration job warrants another component only if that responsibility actually exists.

Identify separately managed infrastructure, required credentials, and supplied data in the startup journey. Ordinary startup must preserve edited installed workflows and private data; workflow import or publication follows the accepted operational contract and authority. Verify installation, the served widget and gateway, an answer through the chosen backend, and data-preserving restart at the authorized boundary. Do not claim a remote production deployment from local container checks.
