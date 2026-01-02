# Diplomacy LLM Research

Using Diplomacy as a testbed to study how LLMs reason about strategy, deception, and spatial problems in multi-agent environments.

## Origin

This project started as informal testing of LLMs on strategic games (chess, Diplomacy) across model releases going back to GPT-4. Early models failed spectacularly. Gemini 3 (late 2025) was the first to show genuine strategic understanding - a "spark" that suggested something worth investigating. What began as automation of browser-based play evolved into structured research when unexpected behaviors emerged.

## Research Progression

| Phase | What We Did | What We Learned |
|-------|-------------|-----------------|
| **Game 001** (Gunboat) | Full 12-year game, zero intervention, minimal prompts | Agents don't learn from mistakes unless they explicitly write about them |
| **Experiment 001** | Iterated on DEBRIEF prompts using 001 findings | Explored what notes agents take and how they communicate |
| **Experiment 002** | New PLAN phase, ran through Spring 1902 | Strategic reasoning works great; spatial/mechanical reasoning is the gap |
| **Experiment 003** | *Next* | Combine learning interventions with spatial reasoning prompts |

**The core question for 003**: Can spatial reasoning limitations be overcome with learning, or is this a fundamental LLM limitation?

---

## Two Core Findings

### 1. Spatial/Mechanical Reasoning Gap (from Experiment 002)

LLMs reason brilliantly about strategy and deception but struggle with spatial/mechanical aspects that would be obvious to a human looking at a map.

**The spectrum of difficulty:**
| Type | Example | Works? |
|------|---------|--------|
| Simple adjacency | "Does EMS border Greece?" | Yes |
| Self-consistency | "Do my orders conflict?" | No |
| Counterfactual | "Could I achieve this differently?" | No |
| Cascade reasoning | "If move A fails, what happens to B?" | No |

See: `findings/spatial-reasoning-gap.md`

### 2. Reflection-Learning Gap (from Game 001)

Agents CAN learn from mistakes, but only when they explicitly process failures in their notes. Passive exposure to feedback in game history is insufficient.

See: `findings/reflection-learning-gap.md`

### How They Connect

Both findings reveal the same underlying issue: **LLMs need explicit prompting to notice things that seem obvious**. Whether it's:
- Spatial relationships on a map (spatial gap)
- Failures in game history (learning gap)

The solution space is similar: structured prompts that force explicit attention and verification.

## Project Structure

```
research/
├── README.md                         # This file
├── next-steps.md                     # Current priorities and research questions
├── experiments/
│   ├── 001-emergent-behavior.md      # Iterated on DEBRIEF using Game 001 findings
│   ├── 002-multi-option-planning.md  # PLAN phase: multi-option strategic planning
│   └── 003-spatial-learning.md       # NEXT: Can spatial reasoning be learned?
├── findings/
│   ├── spatial-reasoning-gap.md      # Core finding: mechanical reasoning failures
│   ├── reflection-learning-gap.md    # Learning requires explicit reflection
│   ├── learning-failure-taxonomy.md  # Four types of learning failures
│   └── case-studies.md               # Agent-by-agent analysis across games
├── hypotheses/
│   └── interventions.md              # Proposed experiments to test
└── data/
    ├── game-001-summary.md           # 12-year gunboat game (Dec 2025)
    └── game-002-summary.md           # PLAN experiment game (Jan 2026)
```

## Games Run

| Game | Mode | Duration | Key Finding |
|------|------|----------|-------------|
| 001 | Gunboat (no messaging) | 12 years | Reflection-learning gap |
| 002 | PLAN phase (multi-option) | 3 seasons | Spatial reasoning gap |

## Quick Links

- [Experiment 003](experiments/003-spatial-learning.md) - **NEXT**: Can spatial reasoning be learned?
- [Next Steps](next-steps.md) - Current research priorities
- [Spatial Reasoning Gap](findings/spatial-reasoning-gap.md) - Core finding
- [Proposed Interventions](hypotheses/interventions.md) - Experiments to run
