# RAG Document Sources

The FinOps RAG demo uses three public, text-based PDF documents.

The PDF files are downloaded locally and are not committed to this repository.
Download them from their official sources and place them in this directory
using the exact filenames shown below.

## Documents

### 1. What is FOCUS?

Filename:

```text
What-is-FOCUS-December-2025.pdf
```

Official source:

https://focus.finops.org/wp-content/uploads/2025/12/What-is-FOCUS-December-2025.pdf

### 2. FinOps with Azure

Filename:

```text
FinOps-with-Azure.pdf
```

Official source:

https://azure.microsoft.com/mediahandler/files/resourcefiles/finops-with-azure-bringing-finops-to-life-through-organizational-and-cultural-alignment/bringing-finops-to-life-through-organizational-and-cultural-alignment.pdf

### 3. Cloud FinOps Shared Services Cost Allocation

Filename:

```text
Cloud-FinOps-Shared-Services-Cost-Allocation.pdf
```

Official source:

https://services.google.com/fh/files/misc/cloud_finops_shared_services_cost_allocation_whitepaper.pdf

## Build the Local Index

After downloading or changing the PDF documents, set the following value in
the local `.env` file:

```env
RAG_REBUILD_INDEX=true
```

Run:

```bash
python run_finops_rag.py
```

After the index builds successfully, change the setting back to:

```env
RAG_REBUILD_INDEX=false
```

Future executions will load the saved local index.

The generated file under `data/rag_index/` is a local runtime artifact and is
intentionally excluded from Git.