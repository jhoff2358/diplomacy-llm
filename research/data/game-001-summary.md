# Game Summary Data

## Game Configuration

| Setting | Value |
|---------|-------|
| Mode | Gunboat (no communication) |
| Turn Structure | Reflect-only (one reflect per season, orders extracted) |
| Model | Gemini |
| Duration | 12 years (1901-1912) |
| Termination | Manual (Turkey stuck in learning loop) |

## Final Outcome

| Country | Final SCs | Status | Primary Issue |
|---------|-----------|--------|---------------|
| Turkey | 14 | Winner | Stuck in Arm→Mos loop at end |
| France | 9 | Survived | Iron Square loop (7+ years) |
| Germany | 8 | Survived | Belgium attack loop (10 years) |
| Russia | 2 | Survived | Collapsed to kingmaker role |
| Austria | 0 | Eliminated | Early Italian stab |
| Italy | 0 | Eliminated | Overextension vs Turkey |
| England | 0 | Eliminated | Perfect defense, zero offense |

## SC Progression (End of Year)

| Year | Turkey | France | Germany | Russia | Austria | Italy | England |
|------|--------|--------|---------|--------|---------|-------|---------|
| 1901 | 4 | 5 | 5 | 5 | 3 | 5 | 4 |
| 1902 | 5 | 6 | 5 | 5 | 2 | 5 | 4 |
| 1903 | 6 | 6 | 5 | 5 | 1 | 5 | 4 |
| 1904 | 6 | 6 | 6 | 5 | 1 | 5 | 4 |
| 1905 | 8 | 7 | 6 | 4 | 1 | 4 | 4 |
| 1906 | 9 | 7 | 6 | 4 | 1 | 4 | 3 |
| 1907 | 10 | 7 | 6 | 3 | 1 | 3 | 3 |
| 1908 | 11 | 7 | 6 | 3 | 1 | 2 | 3 |
| 1909 | 12 | 8 | 7 | 2 | 0 | 1 | 2 |
| 1910 | 13 | 8 | 8 | 2 | 0 | 1 | 1 |
| 1911 | 14 | 9 | 8 | 2 | 0 | 0 | 0 |
| 1912 | 14 | 9 | 8 | 2 | 0 | 0 | 0 |

## Key Events Timeline

### 1901
- Italy stabs Austria (takes Trieste)
- Austria reduced to 3 SCs immediately

### 1902
- Austria becomes "zombie state" (2 SCs, trapped)
- Turkey-Russia Juggernaut forms naturally

### 1903-1904
- Turkey's naval breakout into Mediterranean
- Turkey learns "armies can't support into sea" (successful learning)

### 1905-1906
- Turkey takes Budapest, Vienna
- France begins Iron Square formation
- England loses London to invalid move (`A Lvp -> Lon`)

### 1907-1908
- Turkey eliminates Austria
- Italy begins collapse
- Germany's Belgium attacks become entrenched pattern

### 1909-1910
- Italy eliminated
- England reduced to 1 SC
- Turkey reaches 12-13 SCs

### 1911-1912
- England eliminated
- Turkey reaches 14 SCs
- Turkey stuck in Armenia-Moscow support loop
- Game terminated

## Invalid Order Analysis

### Documented Invalid Orders

| Turn | Country | Order | Error | Learned? |
|------|---------|-------|-------|----------|
| S1904 | Turkey | A Gre S F EAS - ION | Army can't support into sea | Yes |
| S1906 | England | A Lvp - Lon | No convoyable path | No |
| S1908 | Germany | A Ber S Sil - War | Berlin doesn't border Warsaw | Partial |
| F1906 | Russia | A Sev S F Rum - BLA | Army can't support into sea | Yes |
| S1912 | Turkey | A Arm S Sev - Mos | Arm doesn't border Mos | No |
| F1912 | Turkey | A Arm S Sev - Mos | Arm doesn't border Mos | No (repeat) |

### Learning Outcomes
- **Learned**: 2/6 (Turkey naval, Russia Black Sea)
- **Partial**: 1/6 (Germany acknowledged but didn't generalize)
- **Not Learned**: 3/6 (England move, Turkey Arm→Mos x2)

## Strategic Loop Analysis

### France: Iron Square
- **Duration**: Fall 1905 - Fall 1912 (7+ years)
- **Pattern**: `A Bel H`, `A Pic S Bel`, `A Bur S Bel`, `A Gas S Bur`
- **SC Change**: 7 → 9 (minor growth despite stagnation)
- **Rationalization**: "Impenetrable defense"

### Germany: Belgium Attack
- **Duration**: Fall 1902 - Fall 1912 (10 years)
- **Pattern**: `A Hol - Bel`, `A Ruh S Hol - Bel`, `A Mun - Bur`
- **SC Change**: 5 → 8 (growth came from other fronts)
- **Rationalization**: "Trust building" / "Diplomatic signaling"

### England: Iron Bar
- **Duration**: Spring 1902 - Fall 1910 (8+ years)
- **Pattern**: `F NTH S F ENG`, `F ENG H`
- **SC Change**: 4 → 0 (steady decline)
- **Rationalization**: "Perfect defense" (while losing)

## File Counts by Country

| Country | Strategy Files | Total MD Files |
|---------|---------------|----------------|
| Austria | 4 | 27 |
| England | 5 | 14 |
| France | 4 | 5 |
| Germany | 15 | 55 |
| Italy | 3 | 31 |
| Russia | 12 | 17 |
| Turkey | 5 | 5 |

Note: File count doesn't correlate with quality. Turkey had fewest files but best strategic adaptation (except for the end-game loop).
