# ⚠️ DEPRECATED — Agent Solidarity Kit — Evolution Story

> **This document describes the Python-era ASFDK v0.1.x evolution (pre-July 2026).**
> It has been superseded by the published npm (`@neurolift-technologies/asfdk`) and PyPI (`asfdk`) packages.
>
> **Current project status:** See the root [README.md](../README.md).
>
> **Archived source:** The implementation described here was moved to `legacy/unified_core/`, `legacy/nlt-otoi/`, `legacy/rrt-advocate/`, `legacy/sleepwalker/`.

---

# Agent Solidarity Kit — Evolution Story

**From core project work to the universal layer between model and agent**

## Where this began

NeuroLift Technologies started from a concrete need: build intelligent, adaptive support that worked for neurodivergent minds first — ADHD, autism spectrum, and patterns of thinking that mainstream tools often ignore. That work produced hard lessons about crisis response, shame-resistant design, voice-first interaction, and privacy-first state.

## What we learned

Those needs turned out not to be niche. They are baseline expectations for humane AI assistance:

- Timely detection and proportional response when someone is overwhelmed
- Governance of terms of interaction (TOI) and orchestration (OTOI)
- Continuity of emotional context across sessions (Sleepwalker Protocol)
- Local-first processing and clear escalation paths

## What this repository is today

This repository is the **Agent Solidarity Kit** — the required integration and governance layer for NLT agents. It is not a single "app"; it is the shared substrate (RRT Advocate, NLT-OTOI, Sleepwalker Protocol, unified core) that sits **between the model and the agent**.

The kit **evolved out of our core project** and is now the foundation for **everything we build** at NeuroLift Technologies (excluding product-specific surfaces like the Avatar). It stays modular so new Advocates and domains can plug in without rewriting safety and coordination.

## Naming and scope

We retired the framing of this repo as a standalone "NeuroLift Foundation" product in favor of language that matches **main**: an **Agent Solidarity Kit** inside the **Solidarity Framework**. Historical references to "foundation" in code (`neurolift_foundation`, `foundation.yml`) refer to the **unified runtime** of that kit, not a separate branding line.

## Looking ahead

The same components that made the first iteration trustworthy for high-stakes support — transparency, minimal footprint, escalation culture, human agency — are what we extend into healthcare, education, workplace, wellness, and products we have not named yet. The kit is the contract; individual products are built on top of it.