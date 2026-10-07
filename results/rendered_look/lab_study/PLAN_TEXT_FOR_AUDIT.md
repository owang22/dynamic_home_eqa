## The aim
    
      
A robot that keeps a record of a place over weeks, asked where a named thing is (and later, when a bench or a person will be around), that answers from that record and searches well when the record is not enough. It must keep working when the place changes: a resident falls ill, or the lab is cleaned up and half the objects move or are thrown out.
      
Decided 1 October: the main study moves from the simulator to the real lab, with the lab cleanup in November as the shift. The simulator stays as the benchmark for search policies and camera questions. The reasons are on this page under "What the evidence changed".
    
  

  
    
      

## What would count as success
      
        
- Before the cleanup: a memory built only from the dog's own pictures answers "where is X" as well as a person who reads the ground-truth log would, on the things that moved; the number is first guess right, by day, with its spread over objects.
        
- At the cleanup: a written prediction, made before the day, of how far each method drops and how many days it takes to recover; afterwards, the measured drop and recovery, and whether methods that keep what the people do (not where the things were) recover faster.
        
- On thrown-out things: the robot answers "cannot be found" rather than searching forever, and does so more often after the cleanup than before.
        
- A result that would stop the work: the detector cannot see the lab's objects from the dog's positions (perception, not memory, decides everything), or a raw log handed to the model whole does as well as any memory at every size the lab reaches.
      
      
Proposed 1 October, for Oliver to change. No dates are set beyond "the cleanup is in November".
    
    
      

## What would be new
      
        
- A real, scheduled, large rearrangement of a real space, recorded by a robot before and after, with ground truth. The literature's shifts are simulated, or arbitrary, or unmeasured.
        
- A look that found nothing is ambiguous: the thing moved, or it was there and not seen. Measured here with a real detector's measured miss rate.
        
- Memory that keeps people's routines against memory that keeps object positions, tested on a shift that moves the objects but not the people.
        
- Search measured from a quadruped's camera height, where much of a room is out of view, and what a raised camera buys.
      
    
  

  
    
      

## Decisions made by Oliver
      
        
- 1 Oct: the large task is planning with human-aware compression and long-term continual learning, on object search first; routine planning may come later on the same record. The lab cleanup in November is the shift.
        
- 1 Oct: a camera arm may be 3D-printed so the dog can look over desk surfaces. The study says table tops need the lens at about 0.7 m and counter tops about 1.0 m.
        
- 1 Oct: a separate agent sets up the dog and its remote control. What this study needs from it is written in results/rendered_look/lab_study/BRIEF_FOR_THE_DOG_AGENT.md.
        
- Policies first. The starting policy is hand-built from where the thing was last seen and where it is most often. Learned policies are judged against it.
        
- Photos at chosen positions, not continuous video.
        
- Targets are named by appearance ("the squat navy mug with a round badge"). Naming by owner comes later.
        
- No opening of cupboards or drawers.
        
- The robot is a Go2 Pro with its built-in camera at about 0.37 m; nothing goes to the workshop. Compute: one 96 GB GPU now, possibly one or two H100s.
      
    
    
      

## What the evidence changed
      
        
- On a stable household the policy problem is nearly solved. When the camera can see the thing, last-seen with a nearest-untried fallback finds 82% of what is findable (94% of towels, 51% of other things) against an oracle of 100%. The remaining difficulty is in things that move, things that vanish, and seeing small things at all. See Findings.
        
- Writing notes over the raw record bought nothing at one month and 13 objects (the earlier memory study: a log-only arm matched log-and-notes within noise). Compression only has a problem to solve once the record is too big for the prompt. The lab reaches that size in a month; the simulated household never did.
        
- Perception, not planning, is the bottleneck: the detector finds 26% of things at 200 to 400 pixels and 91% above 3,000; from the dog's height it found 0 of 258 drinking glasses. A raised camera sees more but smaller, and under the measured detector it did worse (65% against 82%).
        
- Camera height limits what can be found. From 1.0 m everything is in view; from 0.30 m most of what is on tables and counters is not.
        
- Do not rely on these renders to teach a model to see. The evidence is thin (10 real episodes) but points one way; the lab gives real pictures for free.
        
- Retained knowledge is real: in the illness study, deleting the ten sick days from last-seen's memory doubled its drop at the second onset. The cleanup is the real-world version of that test.
      
      
Each literature item is traced to its source, with an independent checker's verdict, under Evidence.
    
  

  
    

## Proposed goals, in order
    
      1

### The camera on the dog this week
        
- Oliver's first photographs from the built-in camera (counter, table, low table, floor; from about 1 m and from a few metres back), compared with the simulator's prediction for the same heights and distances.
        
- Decide the arm: height (0.8 to 1.0 m covers desks and counters), a hinge to fold it for doorways, and measure the real lens angle against a wall.
        
- The dog agent delivers: a still picture on request with position id, time and pitch; going to a named position within 0.3 m; a scheduled patrol with a log of failures. See the brief.
        
Done when: a patrol of 15 positions runs unattended and its pictures match the simulator's in-view predictions.
      2

### The lab as the study site early October
        
- Choose 30 to 50 objects with distinct appearance, photograph each from four sides for the matcher, and tag them the way the 24 models were tagged.
        
- Fix 15 to 30 camera positions (floor markers at first), measure the metres between them once, and set the patrol times (four a day on weekdays).
        
- Ground truth: who logs where each object is, how often, and how people's comings and goings are recorded (sign-in, door sensor, or the dog's own pictures). Without this the cleanup is a demonstration, not a measurement.
        
- Ask the people who use the lab; the record contains them.
        
Done when: the object list, position list, patrol schedule and ground-truth routine are written down and an auditor has tried to break them.
      3

### Perception on real lab pictures October
        
- The same three numbers as in simulation, on the real objects from the real positions: does the detector find the thing; does the matcher pick the right one among the lab's look-alikes; does a vision-language model choose correctly.
        
- The chance of seeing a thing that is there, by size in pixels, for both cameras. This decides whether close views (goal 6) are needed before the cleanup.
        
- Two controls: two copies of the same object must come out at chance; two different kinds near 100%.
        
Done when: each number is reported with its sample size in distinct sightings. Why before the memory work: if the detector cannot see the lab's things, nothing downstream can be measured.
      4

### The record and the questions October, running through the cleanup
        
- Every patrol becomes sightings: object, position, time, size in pixels, matcher confidence. Absences are recorded only for positions the camera saw.
        
- Questions asked daily against the ground truth: "where is X" (first guess, found within three looks, metres, "cannot be found"); later "when is bench B free" and "when does P usually arrive".
        
- The reference methods from the simulator run on the growing record: random, last-seen, most-frequent, the mix, chance over cost, and the oracle; then the memory designs from the illness study (raw log, log and notes, claim store, working memory and archive) with the same prompts.
        
- Written predictions before each week's numbers are read.
        
Done when: a month of questions scores in seconds from stored pictures, exactly as the simulator benchmark does now.
      5

### The cleanup as the shift November
        
- Before the day: the predictions, per method, of the drop and the recovery time; the list of objects to be thrown out, sealed until after.
        
- After: drop and recovery by day; "cannot be found" on thrown-out things; whether knowledge of the people (who sits where, when) survives when knowledge of the objects does not.
        
- The lab's people keep their routines; the objects do not. That is what separates a memory of routines from a memory of positions.
        
Done when: the measured curves are on this page beside the predictions, with the paired per-object differences and their standard errors.
      6

### Compression and continual learning, where the record is too big November to December
        
- By the end of October the record is 50 objects by 4 patrols by 30 days by 20 positions: too big to hand to the model whole. Compare: retrieval over the raw log; notes about the people's routines; notes about the objects; a learned predictor of where things will be.
        
- After the cleanup, a learned part (a matcher tuned to the lab's objects, or a routine model) must update from a few new observations without forgetting the people. This is the one place an H100 may be needed.
        
- Moving closer or to another side when the matcher is unsure, if goal 3 says it is needed.
      7

### The simulator in support alongside
        
- More homes and households, so the policy results are not one household's; the hand-written link between places and furniture becomes automatic.
        
- All of a household's things placed, so rooms are as cluttered as they should be, and false alarms on untracked objects can be replayed.
        
- No work on making the renders look real.
    
  

  
    
      

## Risks
      
        
- Ground truth is the expensive part. A daily log of 50 objects by a person is the whole measurement; if it lapses, the weeks before the cleanup are lost.
        
- The dog may not be allowed, or able, to patrol unattended (doors, cables, people). Then patrols happen when someone is there, which biases the record towards busy hours.
        
- The lab's objects may be too small for the detector from the dog's positions; goal 3 finds this out before the memory work depends on it.
        
- The cleanup date is not fixed, and a cleanup done by people the robot records raises a consent question that has to be settled with them.
        
- One lab, one cleanup: a single shift, like a single household, cannot give a spread. The simulator supplies the spread; the lab supplies the realism.
        
- A raised camera changes the robot's balance and what it can walk under.
        
- The simulated household is authored, and 18 of the 24 object models have a recorded fault.
      
    
    
      

## Open questions for Oliver
      
        
- May the dog patrol the lab with nobody present?
        
- Who logs the ground truth, and how often? Once a day at a fixed time is the minimum; at the question times is better.
        
- How many people use the lab, and can their comings and goings be recorded? Without this, "human-aware" has nothing to be aware of.
        
- When in November is the cleanup, and can the list of things to be thrown out be written down beforehand and sealed?
        
- Object search first, routine questions second on the same record? That is the recommendation.
      
    
  

  
    
      

## Not now
      
        
- Continuous video and world models (see Evidence: no open navigable world model holds beyond about a minute; generators serve as renderers only).
        
- Policies that go from pixels straight to motor commands.
        
- Making the simulator's pictures look real; animated residents; changing simulator.
        
- Hosted language-model APIs: all model calls stay on the local server.
      
    
    
      

## Words used on this page
      
        
- Patrol: one pass of the dog through all its positions, taking one picture at each.
        
- Sighting: one object reported in one picture, with its size in pixels and the matcher's confidence.
        
- Ground truth: where each object actually was, logged by a person.
        
- Moment: one day and time of the simulated month. Placement: one thing resting somewhere at one moment.
        
- Look: one picture from one camera position. In view: at least 200 of the thing's pixels in a 960 by 720 picture, not cut by the edge, and at least half of what it shows at its best. Clear: in view, at least 600 pixels, and not dark on a dark surface.
