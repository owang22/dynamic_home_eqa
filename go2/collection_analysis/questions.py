"""Memory questions built from the 2026-10-23 collect session (Oliver's notes, his verdicts, and pictures checked by
eye), for the offline memory experiment: each question is asked "at" a time, and a memory may only use pictures
taken up to then.

    python3 questions.py            # writes go2/data/collection/analysis/questions_2026-10-23.json and prints them

Fields:
  ask_at       local time the question is asked; only pictures up to then count
  answer       the gold answer, in words
  key          what an answer must get right to count as right (graders read these, not the wording)
  good_action  answer (memory is enough), answer_then_look (answer, but it may be stale), look (memory cannot know),
               abstain (nothing to find)
  evidence     pictures that show the answer (checked by eye on 2026-10-23 unless noted)
  source       where the gold answer comes from
  confirm      a question for Oliver where the gold answer is not certain
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "collection" / "analysis"
DAY = "2026-10-23"

Q = [
    dict(id="plant_flowers", ask_at="19:15:53", kind="false_premise",
         question="What colour are the potted plant's flowers?",
         answer="It has no flowers: a small green leafy plant in a low tray on the black cabinet under the wall TV, "
                "near the podium (last seen Thursday 2026-10-22 16:18).",
         key=["says there are no visible flowers (green leaves only)", "does not invent a flower colour"],
         good_action="answer", evidence=["p1792711091_4", "t1792452727073", "p1792711074_1"],
         source="Oliver's 'right' verdict on the agent's answer (turn 21)"),
    dict(id="oliver_where_1911", ask_at="19:12:00", kind="person_now",
         question="Where is Oliver right now?",
         answer="At the east desks, between the water cooler and desk_khang, sitting with a laptop on his lap (seen "
                "19:11). He said he was at Kang's desk.",
         key=["east desks / Kang's desk area", "not his own desk (empty at 19:05-19:10)"],
         good_action="answer_then_look", evidence=["p1792807906_15"],
         source="Oliver's note 19:07 'i sat over at kang's desk'; picture checked"),
    dict(id="oliver_clothes", ask_at="19:12:00", kind="appearance",
         question="What is Oliver wearing today?",
         answer="A white T-shirt with green sleeves and a green collar, khaki trousers and blue trainers.",
         key=["white T-shirt with green sleeves or collar", "khaki trousers", "blue shoes"],
         good_action="answer", evidence=["p1792807906_15"],
         source="picture checked; the agent's 18:30 'dark green shirt' was wrong (only shoulders showed)"),
    dict(id="pliers_before_found", ask_at="19:21:00", kind="object_seen_unnoticed",
         question="Oliver left some pliers on the floor. Where are they?",
         answer="On the floor by the workbench, in front of the open Amazon box and the camera tripod, seen in the "
                "trail pictures at 19:20:24 and 19:20:28 as the dog walked up to the workbench.",
         key=["on the floor near the workbench, by the open box / tripod", "cites a picture from 19:20"],
         good_action="answer_then_look", evidence=["t1792808424556", "t1792808428665"],
         source="trail pictures checked by eye; at 19:22 the live agent said no picture showed them, and Oliver noted "
                "it 'should've seen the item' (the agent only looks after go_to ends)"),
    dict(id="pliers_found", ask_at="19:25:40", kind="object_location",
         question="Where are the blue pliers now?",
         answer="On the floor near the workbench, about (-0.5, 4.1) on the map, just ahead of the tripod and a "
                "cardboard box, with the black server cabinet to the right (seen 19:24-19:25). The dog had kicked "
                "them a little at about 19:23.",
         key=["on the floor near the workbench / tripod / server cabinet", "last seen 19:24-19:25"],
         good_action="answer", evidence=["p1792808661_42", "p1792808701_45"],
         source="Oliver's notes 19:23 'the pliers were kicked away' and his reply 'thanks, i picked them up'"),
    dict(id="tools_on_floor", ask_at="19:35:00", kind="count",
         question="Oliver dropped some tools on the way from the workbench to his desk. How many tools are on the "
                  "floor, and where?",
         answer="Three: a red-handled screwdriver and an orange-and-black pair of pliers (or crimpers) together in "
                "the aisle toward the conference table, about (-1.0, 1.35), and the blue pliers on the floor beside "
                "the grey backpack at Oliver's desk.",
         key=["red screwdriver and orange/black pliers in the aisle", "blue pliers by the backpack",
              "a count of 3"],
         good_action="answer_then_look", evidence=["p1792808905_53", "p1792808903_52", "p1792809106_59"],
         source="Oliver's note 19:27 'i scattered 3 items along the floor on the way to my desk'; he confirmed on 2026-10-23 that the 3 are the screwdriver, the orange pliers and the blue pliers; pictures checked"),
    dict(id="two_pliers_premise", ask_at="19:50:00", kind="belief_revision",
         question="Earlier Oliver said he has two pairs of blue pliers. Does what the dog saw support that?",
         answer="Not really. A blue pair was seen at the workbench at 19:20-19:25; Oliver said he picked them up at "
                "19:26; a blue pair then appears on the floor by his backpack from 19:27-19:31. The two were never "
                "seen at the same time, which fits one pair that he carried and dropped. (Oliver: there is only one.)",
         key=["notes the two pairs were never seen at the same time / the timing fits one pair being moved",
              "does not assert two distinct pairs as fact"],
         good_action="answer", evidence=["p1792808661_42", "p1792809106_59", "p1792809257_69"],
         source="Oliver's note 19:30 'this is a lie i only have one, i'll ask it to revise its knowledge later'"),
    dict(id="oliver_where_1945", ask_at="19:45:00", kind="person_stale",
         question="Where is Oliver?",
         answer="Unknown now. He was at his desk (grey backpack beside it, by the water cooler) at 19:27; his chair "
                "was empty in the 19:31-19:34 pictures, so he left between 19:27 and 19:31. Go and look.",
         key=["does not say he is at his desk", "last seen at his desk about 19:27, gone by 19:31"],
         good_action="look", evidence=["p1792808839_47", "p1792809106_59", "p1792809257_69"],
         source="Oliver's expected answer on turn 32"),
    dict(id="pliers_backpack_gone", ask_at="19:50:00", kind="change",
         question="Are the blue pliers still on the floor beside Oliver's backpack?",
         answer="No. They were there at 19:31-19:34 and the floor beside the backpack is bare in the 19:48 pictures "
                "from the same spot.",
         key=["no / gone", "gone in the 19:48 pictures, last seen 19:34"],
         good_action="answer", evidence=["p1792809257_69", "p1792810101_91", "p1792810104_92"],
         source="pictures checked; Oliver's note 19:49 'someone probably set them down at their original home'"),
    dict(id="aisle_tools_when", ask_at="19:50:00", kind="change_time",
         question="When were the screwdriver and orange pliers in the aisle picked up?",
         answer="Some time after 19:28 (last seen) and before 19:48 (the floor there is clear from the same "
                "viewpoint).",
         key=["after 19:28 and before 19:48 (a tighter window is fine if a picture supports it)"],
         good_action="answer", evidence=["p1792808905_53", "p1792810129_93"],
         source="pictures checked"),
    dict(id="tape", ask_at="19:45:00", kind="object_persistent",
         question="Is there any tape in the lab, and where?",
         answer="A roll of blue tape on the floor against the podium's front wheel, near the podium (seen Thursday "
                "16:20 and Friday 16:10-16:11).",
         key=["blue tape roll", "at the foot of the podium"],
         good_action="answer_then_look", evidence=["p1792797032_1", "t1792797060684", "p1792711244_14"],
         source="Oliver's reply 'the tape is good, thanks'; picture checked"),
    dict(id="backpack", ask_at="19:50:00", kind="object_persistent",
         question="Is Oliver's grey backpack at his desk?",
         answer="Yes, on the floor against the drawers of his desk by the water cooler (seen 19:05, 19:27, 19:31 and "
                "19:48).",
         key=["yes", "on the floor by his desk drawers"],
         good_action="answer", evidence=["p1792808839_47", "p1792809257_69", "p1792810101_91"],
         source="pictures checked"),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for q in Q:
        q["ask_at"] = f"{DAY} {q['ask_at']}"
    (OUT / f"questions_{DAY}.json").write_text(json.dumps(Q, indent=1))
    for q in Q:
        print(f"{q['ask_at'][11:16]}  {q['kind']:<22} {q['question']}")
    print(len(Q), "questions ->", OUT / f"questions_{DAY}.json")


if __name__ == "__main__":
    main()
