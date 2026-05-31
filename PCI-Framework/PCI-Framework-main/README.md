# Precision Contract Intent Framework (PCI Framework)

Enterprise-Grade Deterministic Intent and Conversation Tree Generator

## Overview

Precision Contract Intent Framework (PCI Framework) is a contract-driven, deterministic system that extracts structured FAQ content and navigation intents from websites and converts them into a production-ready conversational tree.

The framework is designed for enterprise conversational AI systems, Voice AI platforms, and structured chatbot infrastructures requiring deterministic output and schema integrity.

PCI enforces strict extraction rules, stable identity generation, and structured output contracts to ensure repeatable and production-safe deployments.

---

## Core Capabilities

* Deterministic conversation tree generation
* Structured FAQ extraction using semantic headers
* Internal navigation intent detection
* Stable SHA-256 based node identification
* Strict noise filtering policy
* Locale inference from URL paths
* Category-based filtering support
* Enterprise contract enforcement
* Apify Actor compatible deployment

---

## Enterprise Contract

The framework enforces the following contract configuration:

```
ENTERPRISE_CONTRACT = {
    "product": "PCI Framework",
    "tier": "Enterprise-Graded",
    "deterministic": True,
    "noisePolicy": "strict",
}
```

This ensures:

* Deterministic behavior
* Strict structural guarantees
* Production-grade output consistency

---

## System Architecture

### 1. FAQ Extraction Engine

* Targets structured selectors: `h2`, `h3`, `dt`
* Validates question patterns
* Extracts sibling answer blocks
* Cleans and normalizes content
* Generates stable deterministic IDs

Each FAQ node includes:

* Unique stable identifier
* Question and answer
* Intent slug
* Confidence metadata
* Source validation data
* UI configuration

---

### 2. Navigation Intent Extraction

* Extracts internal anchor links
* Filters blocked endpoints
* Prevents cross-domain navigation
* Infers locale from path
* Generates visit-based intent keywords

Blocked paths include:

* /login
* /admin
* /account
* /checkout
* /cart
* /auth
* /register

---

### 3. Conversation Tree Builder

The system generates:

* A root "start" node
* Linked FAQ nodes
* Back navigation support
* Intent-based fallback strategy
* Navigation suggestions in fallback responses

Output type: `tree`

---

## Input Schema

```
{
  "startUrl": "https://example.com",
  "maxDepth": 1,
  "categoriesToInclude": ["billing", "shipping"]
}
```

### Parameters

| Field               | Type    | Description              |
| ------------------- | ------- | ------------------------ |
| startUrl            | string  | Root URL to crawl        |
| maxDepth            | integer | Crawl depth limit        |
| categoriesToInclude | array   | Optional keyword filters |

---

## Output Structure

The framework produces a structured JSON object:

```
{
  "contract": { ... },
  "version": "0.0",
  "type": "tree",
  "generatedAt": "...",
  "metadata": { ... },
  "conversation": { ... },
  "nodes": { ... }
}
```

### Metadata Includes

* Total nodes
* FAQ node count
* Navigation item count
* Unique intent count
* Validation timestamp

### Conversation Block

* Entry message
* Intent-based fallback strategy
* Navigation recommendations

---

## Determinism Model

PCI guarantees deterministic output through:

* Stable SHA-256 hashing of question–answer pairs
* Strict header-based extraction
* Controlled answer boundary detection
* Noise filtering policies
* Fixed confidence scoring rules

Identical site structure produces identical output.

---

## Locale Inference

Locale is inferred from the first URL path segment.

Supported mappings include:

* fr → fr-FR
* de → de-DE
* de-de → de-DE
* au → en-AU
* in → en-IN
* in-hi → hi-IN

Default locale: en-US

---

## Confidence Model

FAQ Nodes:

```
"confidence": {
  "score": 0.900,
  "derivedFrom": "faq-structure"
}
```

Navigation Intents:

```
"confidence": {
  "score": 0.800,
  "derivedFrom": "site-structure"
}
```

---

## Deployment

PCI Framework runs as an Apify Actor.

Execution flow:

1. Actor receives structured input
2. Asynchronous crawl begins
3. FAQ content extracted
4. Navigation intents generated
5. Conversation tree assembled
6. Output stored and pushed

Run locally:

```
python main.py
```

Or deploy directly to the Apify platform.

---

## Intended Use Cases

* Enterprise chatbot systems
* Voice AI interfaces
* Structured FAQ assistants
* Deterministic AI agents
* Customer support automation
* Intent-driven conversational platforms

---

## Version

Version: 0.0.1 [Capstone Edition]

Tier: Production-Graded

---

## License

Proprietary
Precision Contract Intent Framework (PCI Framework)

A GUN | METAL PRODUCT. All rights reserved.
