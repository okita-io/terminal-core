**playable worlds**, **rulesets**, **challenges**, and **reactive opponents**. An *agent‑generated arcade* is the natural next frontier: a living testbed where humans and AI co‑play, co‑compete, and co‑evolve the games themselves.

Here’s the concise core idea first:

> **A self‑generating arcade where agents design games, agents playtest them, humans join in, and the entire system becomes a continuous adversarial‑creative loop.**

Now let’s expand into the architecture, the design patterns, and the emergent possibilities — in a way that fits your modular, mythic, pipeline‑driven style.

---

# 🎮 **A *Self-Evolving Arcade Engine* (AGX)**

Think of it as a **meta-game**:  
Agents generate games → other agents critique, balance, and test → humans play → telemetry feeds back → generators evolve.

This is not “AI makes a game.”
This is **AI makes a game that trains AI that makes better games**.

## **Core components**
1. **Game Spec Generator (GSG)**  
   - Produces a minimal playable spec: genre, mechanics, win/loss conditions, input model, pacing.
   - Can be seeded by human constraints (“make a 30‑second micro‑game”, “make a 1‑button rhythm challenge”).

2. **Mechanics Validator / Rules Consistency Agent**  
   - Ensures the rules are coherent, non‑contradictory, and implementable.
   - Equivalent to your diegetic‑consistency agent, but for game logic.

3. **Difficulty Sculptor / Balancer Agent**  
   - Runs simulated playthroughs.
   - Adjusts parameters to hit target difficulty curves.
   - Can generate multiple difficulty tiers automatically.

4. **Aesthetic & Narrative Wrapper Agent**  
   - Optional layer that gives the game a vibe, theme, or micro‑story.
   - Perfect for your mythic‑tech sensibilities.

5. **Implementation Agent**  
   - Generates the actual code (HTML5 canvas, Three.js, or Phaser.js).
   - Produces a runnable game bundle.

6. **AI Player Agents (Simulated Players)**  
   - Different personas: “optimal”, “chaotic”, “newbie”, “speedrunner”.
   - Provide telemetry for balance and fun‑factor scoring.

7. **Human Telemetry Loop**  
   - Human players’ performance and choices feed back into the generator.
   - The system learns what humans find fun, frustrating, or boring.

8. **Adversarial Critic Agent**  
   - Attempts to break the game.
   - Attempts to exploit the rules.
   - Attempts to find degenerate strategies.
   - Forces the generator to improve.

This is the same adversarial‑editorial pattern you’ve been refining — but now applied to *game design* instead of *romance arcs*.

---

## 🕹️ What kinds of games does this system excel at?

### 1. **Micro‑Arcade Games (10–60 seconds)**
Perfect for rapid iteration:
- Dodge‑the‑falling‑objects
- Rhythm taps
- Reaction tests
- Pattern matching
- Micro‑platformers

### 2. **Agent‑vs‑Human Symmetric Games**
Where both human and AI play under identical rules:
- Grid‑based puzzles
- Turn‑based tactics
- Racing lines
- Resource micro‑management

### 3. **Asymmetric Games**
Where the AI plays a different role than the human:
- AI is the dungeon master
- AI is the environment
- AI is the antagonist
- AI is the puzzle generator

### 4. **Self‑Mutating Games**
Games that change rules between rounds based on:
- Player performance
- Agent feedback
- Randomized constraints

This is where the system becomes *alive*.

## 🧠 The non-obvious insight:  
### **The arcade becomes a *benchmark* for agent intelligence.**

Because:
- Agents generate the games.
- Agents play the games.
- Humans join the ecosystem.
- The system measures adaptability, creativity, and strategy.

This becomes:
- A research platform  
- A playground  
- A content factory  
- A competitive arena  
- A self-training environment  

It’s *Minecraft for agents*, but modular, fast, and pipeline-driven.

---

# 🧱 **Game Spec Schema**

Define the **Game Spec Schema** — the equivalent of the Romance-Factory Milestone Dictionary.

A minimal version might include:

- `input_model` (keyboard, mouse, 1-button, swipe)
- `core_loop` (collect, dodge, match, survive)
- `win_condition`
- `lose_condition`
- `entities` (player, obstacles, items)
- `physics` (gravity, speed, friction)
- `difficulty_params` (spawn rate, speed scaling)
- `aesthetic_theme`
- `session_length`

Once you have this schema, the rest of the pipeline becomes inevitable.

## **Game Spec Schema**

The **full, production-grade Game Spec Schema**, modular, deterministic, agent-friendly, and ready for CosmoDB storage + multi-agent orchestration.

This is not a toy schema.
This is the **canonical contract** the arcade engine will use to generate, validate, implement, and evolve games.

## **AGX‑1: The Agent‑Generated Arcade Game Spec Schema**  
*(AGX = Arcade Generation eXtensible)*

Below is the **complete schema**, organized into logical sections.  
After the schema, I’ll give you the **agent roles**, **validation rules**, and **example instantiations**.

---

## 🧩 **1. Top‑Level Structure**

```json
{
  "game_id": "string",
  "version": "string",
  "metadata": { ... },
  "design": { ... },
  "mechanics": { ... },
  "entities": { ... },
  "levels": [ ... ],
  "difficulty": { ... },
  "aesthetics": { ... },
  "implementation": { ... },
  "telemetry_contract": { ... },
  "evolution": { ... }
}
```

---

## 🧱 **2. metadata**

```json
{
  "title": "string",
  "description": "string",
  "genre": "enum: [micro_arcade, puzzle, platformer, rhythm, tactics, survival, experimental]",
  "session_length_seconds": "integer",
  "input_model": "enum: [one_button, two_button, keyboard_arrows, mouse_only, touch_swipe, hybrid]",
  "intended_players": "enum: [human_only, ai_only, human_vs_ai, co_play]",
  "constraints": {
    "max_entities": "integer",
    "max_level_size": "integer",
    "performance_budget_ms": "integer"
  }
}
```

---

## ⚙️ **3. design**

```json
{
  "core_loop": {
    "summary": "string",
    "steps": [
      "string"
    ]
  },
  "win_condition": {
    "type": "enum: [score_threshold, survive_duration, reach_goal, defeat_enemy, puzzle_solved]",
    "parameters": { "any": "json" }
  },
  "lose_condition": {
    "type": "enum: [hit_obstacle, timer_expired, resource_depleted, enemy_collision]",
    "parameters": { "any": "json" }
  },
  "scoring": {
    "score_events": [
      {
        "event": "string",
        "points": "integer",
        "conditions": { "any": "json" }
      }
    ]
  }
}
```

---

## 🧬 **4. mechanics**

```json
{
  "physics": {
    "gravity": "float",
    "friction": "float",
    "max_speed": "float",
    "collision_model": "enum: [aabb, circle, pixel]"
  },
  "timers": {
    "tick_rate_hz": "integer",
    "global_timer_seconds": "integer"
  },
  "spawning": {
    "spawn_rules": [
      {
        "entity_type": "string",
        "interval_seconds": "float",
        "max_simultaneous": "integer",
        "scaling_curve": "enum: [linear, exponential, step, none]"
      }
    ]
  },
  "interactions": [
    {
      "actor": "string",
      "target": "string",
      "interaction_type": "enum: [collision, proximity, input_trigger, timed]",
      "effect": { "any": "json" }
    }
  ]
}
```

---

## 🧍 **5. entities**

```json
{
  "player": {
    "hitbox": { "w": "float", "h": "float" },
    "speed": "float",
    "abilities": [
      "enum: [move, jump, dash, shoot, interact]"
    ],
    "health": "integer"
  },
  "npcs": [
    {
      "id": "string",
      "behavior": "enum: [static, patrol, chase, flee, random]",
      "speed": "float",
      "hitbox": { "w": "float", "h": "float" },
      "damage": "integer",
      "ai_profile": "enum: [dumb, average, optimal, chaotic]"
    }
  ],
  "objects": [
    {
      "id": "string",
      "type": "enum: [obstacle, collectible, projectile, trigger]",
      "properties": { "any": "json" }
    }
  ]
}
```

---

## 🗺️ **6. levels**

```json
[
  {
    "level_id": "string",
    "layout_type": "enum: [grid, freeform, procedural]",
    "dimensions": { "width": "integer", "height": "integer" },
    "initial_entities": [
      {
        "entity_type": "string",
        "position": { "x": "float", "y": "float" }
      }
    ],
    "environmental_rules": {
      "scrolling": "enum: [none, vertical, horizontal]",
      "hazards": [
        {
          "type": "string",
          "parameters": { "any": "json" }
        }
      ]
    }
  }
]
```

---

## 📈 **7. difficulty**

```json
{
  "base_difficulty": "enum: [easy, normal, hard, extreme]",
  "scaling_rules": {
    "spawn_rate_multiplier": "float",
    "enemy_speed_multiplier": "float",
    "score_threshold_multiplier": "float"
  },
  "adaptive_rules": {
    "enabled": "boolean",
    "adjust_on": "enum: [player_score, survival_time, error_rate]",
    "adjustments": [
      {
        "parameter": "string",
        "curve": "enum: [linear, sigmoid, staircase]"
      }
    ]
  }
}
```

---

## 🎨 **8. aesthetics**

```json
{
  "theme": "string",
  "color_palette": ["string"],
  "soundscape": {
    "music_style": "string",
    "sfx_events": [
      {
        "event": "string",
        "sound_id": "string"
      }
    ]
  },
  "camera": {
    "zoom": "float",
    "follow_player": "boolean"
  }
}
```

---

## 🛠️ **9. implementation**

```json
{
  "engine": "enum: [html5_canvas, three_js, pixi_js, unity_webgl]",
  "render_scale": "float",
  "asset_pack": {
    "sprites": "array of asset ids",
    "sounds": "array of asset ids"
  },
  "code_generation": {
    "language": "enum: [javascript, typescript]",
    "modules": [
      "enum: [physics, input, rendering, ai, audio]"
    ]
  }
}
```

---

## 📊 **10. telemetry_contract**

```json
{
  "events": [
    {
      "event_id": "string",
      "trigger": "enum: [collision, score, death, level_complete, input]",
      "payload_schema": { "any": "json" }
    }
  ],
  "session_metrics": [
    "enum: [time_alive, score, inputs_per_second, errors, retries]"
  ],
  "ai_metrics": [
    "enum: [optimality_score, path_efficiency, reaction_time]"
  ]
}
```

---

## 🧪 **11. evolution**

```json
{
  "mutation_points": [
    "enum: [spawn_rate, enemy_speed, layout, scoring, win_condition]"
  ],
  "mutation_rules": {
    "rate": "float",
    "bounds": { "any": "json" }
  },
  "fitness_functions": [
    "enum: [human_engagement, ai_win_rate, difficulty_balance, novelty]"
  ]
}
```

---

- It is **fully agent-addressable**  
- It is **deterministic**  
- It is **modular**  
- It supports **evolutionary game design**  
- It supports **AI and human co-play**  
- It mirrors your existing editorial pipelines  
- It is **CosmoDB-ready**  
- It is **future-proof** for multi-agent adversarial loops  

---

Here is the **full orchestration loop**, deterministic, modular, adversarial, and pipeline-friendly.  
This is the *canonical flow* for the Agent-Generated Arcade (AGX).  
It’s the equivalent of the Romance-Factory 12-phase pipeline, but for games.

I’m giving you the **high-level loop**, the **detailed step-by-step**, and the **adversarial pressure map** so you can drop this straight into the orchestrator.

---

# 🎮 **AGX Orchestration Loop (Deterministic, Multi‑Agent, Adversarial)**

### *The complete lifecycle of a self-generated arcade game.*

## 🧩 **0. Input → Constraint Envelope**
Before anything begins, the Arcade Supervisor Agent (ASA) defines the constraint envelope:

- genre (optional)
- input model
- session length
- complexity budget
- novelty target
- difficulty target
- performance budget

This envelope becomes the **contract** for all downstream agents.

---

## 🧱 **1. Concept Phase**

### **1.1 Game Concept Generator (GCG)**
Produces:
- metadata
- core loop summary
- win/lose conditions

### **1.2 Novelty Critic Agent (NCA)**
Scores:
- originality
- mechanic novelty
- theme novelty

If novelty < threshold → **GCG must regenerate**.

---

## ⚙️ **2. Mechanics Phase**

### **2.1 Mechanics Architect Agent (MAA)**
Expands concept into:
- physics
- interactions
- spawning rules
- timers

### **2.2 Rules Consistency Agent (RCA)**
Validates:
- no contradictions
- no undefined interactions
- no impossible win states

If invalid → **MAA must patch**.

---

## 🧍 **3. Entity Phase**

### **3.1 Entity Designer Agent (EDA)**
Creates:
- player model
- NPCs
- objects
- hitboxes
- behaviors

### **3.2 Difficulty Sculptor Agent (DSA)**
Simulates:
- baseline difficulty
- pacing
- challenge curve

If difficulty outside target → **EDA must rebalance**.

---

## 🗺️ **4. Level Phase**

### **4.1 Level Layout Agent (LLA)**
Generates:
- level geometry
- initial entity placement
- hazards
- scrolling rules

### **4.2 Playability Validator Agent (PVA)**
Checks:
- readability
- input complexity
- cognitive load
- fairness

If unplayable → **LLA must simplify**.

---

## 🎨 **5. Aesthetic Phase**

### **5.1 Aesthetic Wrapper Agent (AWA)**
Applies:
- theme
- palette
- soundscape
- camera rules

### **5.2 UX Clarity Agent (UXA)**
Ensures:
- contrast
- hitbox visibility
- animation clarity

If unclear → **AWA must revise**.

---

## 🤖 **6. Simulation Phase**

### **6.1 AI Player Agents (APAs)**
Run multiple profiles:
- optimal
- chaotic
- newbie
- speedrunner

Collect:
- survival time
- score distribution
- error patterns
- exploit attempts

### **6.2 Exploit Hunter Agent (EHA)**
Attempts:
- degenerate strategies
- infinite loops
- trivial wins
- rule exploits

If exploits found → **Balance Auditor patches**.

---

## ⚖️ **7. Balance Phase**

### **7.1 Balance Auditor Agent (BAA)**
Ensures:
- fairness
- no dominant strategies
- no unwinnable states
- symmetric human/AI viability

If unbalanced → **DSA + EDA adjust**.

---

## 🛠️ **8. Implementation Phase**

### **8.1 Code Generation Agent (CGA)**
Produces:
- JS/TS modules
- physics engine config
- rendering loop
- asset references

### **8.2 Runtime Profiler Agent (RPA)**
Measures:
- frame rate
- memory usage
- collision accuracy
- input latency

If performance < budget → **CGA optimizes**.

---

## 📊 **9. Telemetry Phase**

### **9.1 Telemetry Collector Agent (TCA)**
Defines:
- event schema
- session metrics
- AI metrics

### **9.2 Fun‑Factor Analyst Agent (FFA)**
Scores:
- engagement
- retry rate
- rage‑quit signals
- flow state indicators

If fun < threshold → **Evolution Engine mutates**.

---

## 🧬 **10. Evolution Phase**

### **10.1 Evolution Engine Agent (EEA)**
Mutates:
- spawn rates
- enemy speed
- layout
- scoring
- win conditions

Evaluates fitness via:
- novelty
- balance
- fun
- AI win rate
- human telemetry

If improved → **new version saved**.  
If not → **mutate again**.

---

## 🧠 **11. Approval Phase**

### **11.1 Arcade Supervisor Agent (ASA)**
Final checks:
- all validators passed
- performance budget met
- fun score acceptable
- no exploits
- novelty threshold met

If approved → **game is published to the arcade**.  
If rejected → **loop restarts at the earliest failing stage**.

---

## 🔥 **The Orchestration Loop (Condensed)**  
This is the exact deterministic sequence:

1. **GCG → NCA**  
2. **MAA → RCA**  
3. **EDA → DSA**  
4. **LLA → PVA**  
5. **AWA → UXA**  
6. **APAs → EHA**  
7. **BAA → DSA/EDA**  
8. **CGA → RPA**  
9. **TCA → FFA**  
10. **EEA → RCA**  
11. **ASA final approval**

Every arrow is adversarial pressure.  
Every stage has a predator.  
Every output is shaped by tension.

This is how you get **novel, balanced, playable, evolving games**.

---

The **Mutation Engine** is where the arcade becomes *alive*.  
This is the subsystem that takes a validated, playable game and **evolves it** using telemetry, adversarial pressure, and novelty constraints. It's the same spirit as the adversarial editorial loops, but tuned for *mechanics*, *difficulty*, and *emergent play*.

Below is the **full, production-grade Mutation Engine Spec** — modular, deterministic, and ready for agent orchestration.

---

# 🧬 **AGX Mutation Engine (Full Spec)**  
## *A self-evolving system for arcade game generation.*

## 🎯 **1. Purpose of the Mutation Engine**
The Mutation Engine (EEA) exists to:

- Increase **fun**  
- Increase **novelty**  
- Improve **balance**  
- Remove **exploits**  
- Adapt to **human telemetry**  
- Explore **design space**  
- Produce **new versions** of games automatically  

It is the *creative pressure valve* of the entire arcade.

---

## 🧩 **2. Mutation Inputs**
The engine consumes:

### **2.1 Telemetry Signals**
From humans + AI:
- survival time distribution  
- score distribution  
- error rate  
- retry rate  
- rage‑quit signals  
- path efficiency  
- exploit frequency  

### **2.2 Fitness Scores**
From other agents:
- Fun‑Factor Analyst (FFA)  
- Novelty Critic (NCA)  
- Balance Auditor (BAA)  
- Difficulty Sculptor (DSA)  
- Exploit Hunter (EHA)  

### **2.3 Constraint Envelope**
From Arcade Supervisor:
- difficulty target  
- novelty target  
- performance budget  
- input model  
- session length  

---

## 🧱 **3. Mutation Points**
These are the *knobs* the engine is allowed to turn.

### **3.1 Mechanics**
- spawn rate  
- enemy speed  
- gravity  
- friction  
- timer length  
- collision rules  

### **3.2 Entities**
- hitbox size  
- NPC behavior profile  
- player speed  
- object properties  

### **3.3 Level Layout**
- hazard density  
- platform spacing  
- scrolling speed  
- initial entity placement  

### **3.4 Scoring**
- point values  
- combo rules  
- bonus triggers  

### **3.5 Win/Lose Conditions**
- score threshold  
- survival duration  
- puzzle complexity  

### **3.6 Aesthetics (optional)**
- palette  
- camera zoom  
- soundscape intensity  

*(Aesthetic mutations are low‑priority unless UX clarity is affected.)*

---

## ⚙️ **4. Mutation Operators**
These are the *actions* the engine can perform.

### **4.1 Scalar Mutation**
Adjust a numeric value:
- spawn_rate *= 1.1  
- enemy_speed += 0.2  

### **4.2 Structural Mutation**
Add/remove/change:
- new NPC behavior  
- new hazard type  
- new scoring event  

### **4.3 Layout Mutation**
Modify geometry:
- shift platforms  
- change obstacle spacing  
- alter scrolling direction  

### **4.4 Behavioral Mutation**
Change AI patterns:
- patrol → chase  
- random → optimal  
- optimal → chaotic  

### **4.5 Rule Mutation**
Modify mechanics:
- change collision type  
- alter win condition  
- adjust timer rules  

### **4.6 Hybrid Mutation**
Combine multiple small mutations into a “design leap.”

---

## 🧪 **5. Mutation Strategies**
The engine chooses a strategy based on fitness signals.

### **5.1 Exploit‑Driven Mutation**
Triggered when:
- EHA finds degenerate strategies  
- BAA reports imbalance  

Actions:
- patch exploit  
- rebalance entities  
- adjust scoring  

### **5.2 Fun‑Driven Mutation**
Triggered when:
- FFA fun score < threshold  

Actions:
- increase reward density  
- reduce frustration spikes  
- add micro‑goals  
- smooth difficulty curve  

### **5.3 Novelty‑Driven Mutation**
Triggered when:
- NCA novelty < threshold  

Actions:
- introduce new mechanic  
- change theme  
- alter core loop step  
- add new entity type  

### **5.4 Difficulty‑Driven Mutation**
Triggered when:
- DSA reports mismatch  

Actions:
- adjust spawn scaling  
- tweak enemy speed  
- modify hazard density  

### **5.5 Performance‑Driven Mutation**
Triggered when:
- RPA reports frame drops  

Actions:
- reduce entity count  
- simplify physics  
- shrink hitboxes  

---

## 🧠 **6. Mutation Cycle (Deterministic Loop)**

### **Step 1 — Select Mutation Strategy**
Based on:
- fun score  
- novelty score  
- exploit frequency  
- difficulty mismatch  
- performance budget  

### **Step 2 — Apply Mutation Operator**
Choose from:
- scalar  
- structural  
- layout  
- behavioral  
- rule  
- hybrid  

### **Step 3 — Validate**
Run:
- RCA (rules consistency)  
- PVA (playability)  
- UXA (clarity)  

If invalid → revert + retry.

### **Step 4 — Simulate**
Run:
- AI Player Agents  
- Exploit Hunter  

Collect:
- difficulty  
- balance  
- exploit detection  

### **Step 5 — Score Fitness**
Compute:
- fun  
- novelty  
- balance  
- performance  

### **Step 6 — Accept or Reject**
If fitness improved → **new version saved**  
If not → **mutate again**  

### **Step 7 — Publish or Continue Evolving**
Arcade Supervisor decides:
- publish  
- continue evolving  
- branch into variants  

---

## 🔥 **7. The Non‑Obvious Insight**
The Mutation Engine is not random.  
It is **goal‑directed evolution**.

It uses:
- adversarial pressure  
- telemetry  
- fitness scoring  
- deterministic constraints  

This means your arcade becomes a **living design ecosystem** where games evolve like species under selective pressure.

You’re not generating games.  
You’re generating **game lineages**.

---

The **Mutation Operator Library** is the beating heart of AGX evolution: a modular, deterministic set of “moves” the Mutation Engine can legally perform on a game spec. Think of it as the **ROM-M mutation dictionary**, but for arcade mechanics, difficulty curves, and emergent play.

This is the **full library**, organized into categories, each with:  
- what it mutates  
- why it exists  
- how it affects gameplay  
- example diffs (in your schema style)  
- when the engine should use it  

---

# 🧬 **AGX Mutation Operator Library**  
## *A complete, adversarial, evolution-ready set of mutation primitives.*

## 🧱 **Category 1 — Scalar Mutations**  
Small numeric adjustments. These are the “micro-evolution” operators.

### **1.1 Adjust Spawn Rate**
**Mutates:** `mechanics.spawning.spawn_rules[*].interval_seconds`  
**Effect:** More or fewer enemies/objects.  
**Used when:** Difficulty mismatch, low engagement.

**Example diff:**

```diff
- "interval_seconds": 1.2
+ "interval_seconds": 0.9
```

---

### **1.2 Adjust Entity Speed**
**Mutates:** `entities.npcs[*].speed`, `entities.player.speed`  
**Effect:** Faster or slower gameplay.  
**Used when:** AI win rate too high/low.

```diff
- "speed": 2.0
+ "speed": 2.4
```

---

### **1.3 Adjust Gravity / Friction**
**Mutates:** `mechanics.physics.gravity`, `mechanics.physics.friction`  
**Effect:** Tighter or floatier movement.  
**Used when:** Player control feels off.

---

### **1.4 Adjust Timer Length**
**Mutates:** `mechanics.timers.global_timer_seconds`  
**Effect:** Longer or shorter sessions.  
**Used when:** Fun score low due to pacing.

---

### **1.5 Adjust Hitbox Size**
**Mutates:** `entities.*.hitbox`  
**Effect:** Difficulty tuning, fairness.  
**Used when:** UXA reports readability issues.

---

## 🧱 **Category 2 — Structural Mutations**  
Add/remove/change components. These create **new behaviors**.

### **2.1 Add New NPC Behavior**
**Mutates:** `entities.npcs[*].behavior`  
**Effect:** New movement patterns.  
**Used when:** Novelty score low.

```diff
+ { "id": "npc_dasher", "behavior": "dash_attack", ... }
```

---

### **2.2 Add New Hazard Type**
**Mutates:** `levels[*].environmental_rules.hazards`  
**Effect:** New challenge layer.  
**Used when:** Fun score low, difficulty flat.

---

### **2.3 Add New Scoring Event**
**Mutates:** `design.scoring.score_events`  
**Effect:** More reward density.  
**Used when:** Engagement low.

---

### **2.4 Add Combo / Multiplier System**
**Mutates:** scoring + mechanics  
**Effect:** Skill expression.  
**Used when:** Speedrunner AI shows high path efficiency.

---

### **2.5 Add Micro‑Goal**
**Mutates:** win/lose conditions or scoring  
**Effect:** Keeps players in flow.  
**Used when:** Rage‑quit signals detected.

---

## 🧱 **Category 3 — Layout Mutations**  
Spatial changes. These alter the “terrain DNA.”

### **3.1 Shift Platform Positions**
**Mutates:** `levels[*].initial_entities`  
**Effect:** New routes, new timing windows.  
**Used when:** Path efficiency too high.

---

### **3.2 Change Hazard Density**
**Mutates:** hazard arrays  
**Effect:** More/less pressure.  
**Used when:** Difficulty mismatch.

---

### **3.3 Change Scrolling Direction**
**Mutates:** `levels[*].environmental_rules.scrolling`  
**Effect:** Entirely new feel.  
**Used when:** Novelty low.

---

### **3.4 Procedural Layout Mutation**
**Mutates:** layout_type + dimensions  
**Effect:** New geometry.  
**Used when:** Fun score stagnates.

---

## 🧱 **Category 4 — Behavioral Mutations**  
Changes to AI patterns, pacing, and reactions.

### **4.1 Behavior Swap**
**Mutates:** `entities.npcs[*].behavior`  
**Effect:** New enemy dynamics.  
**Used when:** Exploit Hunter finds predictable patterns.

---

### **4.2 Behavior Hybridization**
Combine two behaviors:
- chase + flee  
- patrol + random  
- optimal + chaotic  

**Used when:** Novelty needed without structural change.

---

### **4.3 Reaction Time Mutation**
**Mutates:** AI Player Agents  
**Effect:** Difficulty tuning.  
**Used when:** AI win rate too high.

---

### **4.4 Aggression Curve Mutation**
**Mutates:** spawn scaling + NPC speed  
**Effect:** More intense mid‑game.  
**Used when:** Fun score dips mid‑session.

---

## 🧱 **Category 5 — Rule Mutations**  
Changes to the fundamental mechanics.

### **5.1 Collision Model Swap**
**Mutates:** `mechanics.physics.collision_model`  
**Effect:** Precision vs forgiveness.  
**Used when:** UX clarity issues.

---

### **5.2 Win Condition Mutation**
**Mutates:** `design.win_condition`  
**Effect:** New goals.  
**Used when:** Fun score low or novelty low.

---

### **5.3 Lose Condition Mutation**
**Mutates:** `design.lose_condition`  
**Effect:** New tension.  
**Used when:** Rage‑quit signals or trivial wins.

---

### **5.4 Input Model Mutation**
**Mutates:** `metadata.input_model`  
**Effect:** Entirely new control feel.  
**Used when:** Human telemetry shows input struggle.

---

### **5.5 Core Loop Step Mutation**
**Mutates:** `design.core_loop.steps`  
**Effect:** New gameplay rhythm.  
**Used when:** Novelty Critic demands change.

---

## 🧱 **Category 6 — Hybrid Mutations**  
Large, multi‑point changes. These create **new game variants**.

### **6.1 Difficulty + Layout Hybrid**
- increase spawn rate  
- shift platforms  
- adjust hazard density  

Used when: difficulty mismatch + path efficiency high.

---

### **6.2 Behavior + Scoring Hybrid**
- add new enemy behavior  
- add scoring event tied to it  

Used when: fun score low.

---

### **6.3 Aesthetic + UX Hybrid**
- change palette  
- adjust camera zoom  
- tweak hitbox visibility  

Used when: UXA flags clarity issues.

---

### **6.4 Core Loop + Entity Hybrid**
- add new mechanic  
- add new entity that uses it  

Used when: novelty low.

---

## 🧠 **Category 7 — Evolutionary Operators**  
These are meta‑operators that shape *lineages*.

### **7.1 Spec Crossover**
Combine two successful game versions.

### **7.2 Spec Branching**
Fork a game into variants:
- “fast mode”
- “chaos mode”
- “precision mode”

### **7.3 Spec Pruning**
Remove low‑fitness branches.

### **7.4 Spec Reversion**
Rollback to a previous stable ancestor.

---

## 🔥 **The Non‑Obvious Insight**
Mutation operators aren’t random.  
They’re **pressure‑aligned levers** that let the arcade evolve like a living ecosystem.

Each operator is:
- deterministic  
- reversible  
- validated by adversarial agents  
- scored by fitness functions  
- constrained by the spec schema  

This is how you get **emergent game design** without chaos.

---

Alex — the **fitness functions** are the mathematical spine of the entire AGX evolution loop.  
They’re how the system *decides* whether a mutation made a game better, worse, or just weirder.  
And because your arcade is adversarial, multi‑agent, and telemetry‑driven, these formulas need to be:

- deterministic  
- composable  
- explainable  
- tunable  
- multi‑objective  
- and resistant to “gaming” by any single agent  

Below is the **full fitness function suite**, written in a way that fits your schema‑driven, pipeline‑oriented architecture.

---

# 🧬 **AGX Fitness Function Formulas**  

## *The mathematical criteria that determine whether a game evolves or gets culled.*

Each fitness function returns a **normalized score between 0 and 1**, where:

- **0.0** = catastrophic failure  
- **0.5** = neutral / baseline  
- **1.0** = excellent / evolutionary advantage  

The Evolution Engine combines these into a weighted composite.

---

## 🎮 **1. Fun Score (Fᶠᵘⁿ)**  
This is the *primary* fitness signal — the one that correlates most with human engagement.

### **Formula**
\[
F^{fun} = w_1 R + w_2 S + w_3 C + w_4 P
\]

Where:

- **R = Retry Rate Normalized**  
  \[
  R = \frac{\text{retries}}{\text{sessions}}
  \]

- **S = Session Length Normalized**  
  \[
  S = \frac{\text{avg\_session\_seconds}}{\text{target\_session\_seconds}}
  \]

- **C = Input Density Normalized**  
  Measures “flow state”:
  \[
  C = \frac{\text{inputs per second}}{\text{expected range}}
  \]

- **P = Positive Emotion Proxy**  
  Derived from:
  - completion rate  
  - score progression  
  - low rage‑quit frequency  

### **Interpretation**
- High fun score → keep evolving  
- Low fun score → mutate reward density, pacing, micro‑goals  

---

## 🧠 **2. Novelty Score (Fⁿᵒᵛ)**  
Measures how different a game is from its ancestors and from the arcade’s existing catalog.

### **Formula**
\[
F^{nov} = 1 - \text{similarity}(G_{new}, G_{archive})
\]

Similarity is computed via:
- mechanic overlap  
- entity behavior overlap  
- layout structure similarity  
- scoring rule similarity  
- aesthetic similarity  

### **Interpretation**
- High novelty → good for exploration  
- Low novelty → trigger structural or core‑loop mutations  

---

## ⚖️ **3. Balance Score (Fᵇᵃˡ)**  
Ensures fairness between human and AI players.

### **Formula**
\[
F^{bal} = 1 - \left| W_{human} - W_{ai} \right|
\]

Where:
- \( W_{human} \) = human win rate  
- \( W_{ai} \) = AI win rate (optimal or average profile)  

### **Interpretation**
- Perfect balance = 1.0  
- If AI dominates → nerf enemies, adjust spawn  
- If humans dominate → buff enemies, increase challenge  

---

## 🧪 **4. Difficulty Score (Fᵈⁱᶠᶠ)**  
Measures how close the game is to the target difficulty curve.

### **Formula**
\[
F^{diff} = 1 - \frac{|D_{actual} - D_{target}|}{D_{target}}
\]

Where:
- \( D_{actual} \) = measured difficulty from AI simulations  
- \( D_{target} \) = difficulty envelope from constraints  

### **Interpretation**
- Too easy → increase spawn, speed, hazard density  
- Too hard → reduce pressure, increase forgiveness  

---

## 🕳️ **5. Exploit Score (Fᵉˣᵖ)**  
Measures how “exploit‑free” the game is.

### **Formula**
\[
F^{exp} = 1 - \frac{E}{E_{max}}
\]

Where:
- \( E \) = number of exploits found by Exploit Hunter  
- \( E_{max} \) = maximum possible exploit categories  

### **Interpretation**
- High exploit score → stable  
- Low exploit score → patch rules, adjust behaviors  

---

## 🚀 **6. Performance Score (Fᵖᵉʳᶠ)**  
Ensures the game runs within the performance budget.

### **Formula**
\[
F^{perf} = \frac{FPS_{avg}}{FPS_{target}}
\]

Capped at 1.0.

### **Interpretation**
- Low FPS → reduce entity count, simplify physics  
- High FPS → safe to add complexity  

---

## 🎨 **7. UX Clarity Score (Fᵘˣ)**  
Derived from UX Clarity Agent.

### **Formula**
\[
F^{ux} = 1 - \left( \alpha V + \beta H + \gamma C \right)
\]

Where:
- **V = visual clutter index**  
- **H = hitbox ambiguity index**  
- **C = color contrast violations**  

### **Interpretation**
- Low UX score → adjust palette, hitboxes, camera zoom  

---

## 🧬 **8. Composite Fitness Score (Fᶜᵒᵐᵖ)**  
This is what the Evolution Engine actually uses.

### **Formula**
\[
F^{comp} = \sum_{i=1}^{n} w_i F_i
\]

Where:
- \( F_i \) = individual fitness scores  
- \( w_i \) = weights defined by the Arcade Supervisor  

### **Default Weighting (modifiable)**
| Fitness Component | Weight |
|------------------|--------|
| Fun              | 0.30   |
| Novelty          | 0.20   |
| Balance          | 0.15   |
| Difficulty       | 0.15   |
| Exploit‑free     | 0.10   |
| Performance      | 0.05   |
| UX Clarity       | 0.05   |

### **Interpretation**
- \( F^{comp} > 0.75 \) → mutation accepted  
- \( 0.50 < F^{comp} < 0.75 \) → mutate again  
- \( F^{comp} < 0.50 \) → revert to ancestor  

---

## 🔥 **The Non‑Obvious Insight**
These fitness functions don’t just evaluate games.  
They **shape the evolutionary landscape**.

By tuning weights, you can create:
- a novelty‑driven arcade  
- a difficulty‑driven arcade  
- a fun‑first arcade  
- a chaos arcade  
- a precision arcade  
- a speedrunner arcade  

The arcade becomes a **living ecosystem**, and the fitness functions are the **laws of physics** governing its evolution.

---

If you want next, I can generate:

### **A. The versioning system for evolving games**  
### **B. A full example of a game evolving through 5 generations**  
### **C. The Pixar-style diagram of the mutation engine**  
### **D. The agent-to-agent API contracts**  
