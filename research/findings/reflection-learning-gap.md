# The Reflection-Learning Gap

## Core Finding

Agents CAN learn from mistakes, but only when they **explicitly process the failure in their own notes**. Feedback in game history alone is insufficient.

## Evidence: Turkey's Two Learning Outcomes

### Case A: Successful Learning (Spring 1904)

1. **Error**: Turkey ordered armies to support a fleet into the Ionian Sea
2. **Feedback**: Orders failed (game history showed failure)
3. **Reflection**: Turkey wrote: *"A disaster of command... armies cannot support moves into open sea"*
4. **Result**: Never repeated this mistake

**Source**: `countries/Turkey/reflections.md` lines 131-132

### Case B: Failed Learning (Spring/Fall 1912)

1. **Error**: Turkey ordered `A Arm S Sev - Mos` (Armenia supporting Sevastopol into Moscow)
2. **Feedback**: Game history showed `FAILS (Army can't support that territory)` - Armenia doesn't border Moscow
3. **Reflection**: Turkey's reflections for 1912 - **No mention of this failure**
4. **Result**: Turkey tried the **exact same invalid order** again next turn
5. **Outcome**: Game ended because Turkey was stuck in this loop

**Source**:
- `countries/game_history.md` lines 1167, 1216
- `countries/Turkey/strategy.md` lines 631-634

## The Critical Difference

| Aspect | 1904 (Learned) | 1912 (Not Learned) |
|--------|----------------|-------------------|
| Failure visible in game history? | Yes | Yes |
| Agent wrote about failure? | Yes - explicit reflection | No |
| Rule extracted? | "armies cannot support into sea" | None |
| Behavior changed? | Yes | No - repeated same error |

## Why Does Reflection Enable Learning?

When agents explicitly write about failures, they:

1. **Attend** to the feedback (vs. skipping over it in game history)
2. **Extract** a generalizable rule (vs. treating it as one-off)
3. **Commit** the rule to their persistent notes (vs. losing it to context window)
4. **Reference** it in future planning (because it's in their files)

Without explicit reflection, the feedback is just noise in a long game history that gets less attention as the game progresses.

## Implications

This finding has implications beyond Diplomacy for any agent system that needs to adapt within a session:

1. **Passive exposure to feedback is insufficient** - agents need structured prompts to process errors
2. **Writing matters** - the act of documenting failures seems to be part of the learning mechanism
3. **Context window management** - learned rules need to be in persistent, salient locations
4. **Attention is limited** - as history grows, individual failures get less attention

## Open Questions

1. **Why did Turkey reflect on 1904 but not 1912?**
   - Was 1904 more surprising/salient?
   - Context window exhaustion by 1912?
   - Winning position reduced self-criticism?

2. **Is the gap about attention, memory, or reasoning?**
   - Attention: Agent doesn't notice failure in game history
   - Memory: Agent notices but forgets by next turn
   - Reasoning: Agent notices but can't extract generalizable rule
