"""Which room and which piece of furniture stands for each place of household hh_s151.

Written by hand for one home, HSSD 106878960_174887073, after listing its
furniture. Where the home has no furniture of the right kind, the nearest
usable piece is named and `stand_in` says so; the page shows that to the reader.

kind:
  surface   objects rest on the furniture; `band` is the range of heights (m)
            in which the resting surface is looked for
  floor     objects rest on the floor of the room, near `near` (x, z)
  enclosed  the place is closed; what is in it is never drawn
  missing   nothing in the home can stand for it
"""
HOME = "106878960_174887073"
HOUSEHOLD = "hh_s151_t03"

ROOMS = {
    "kitchen": "kitchen", "living": "living room", "dining": "dining room",
    "office": "office", "entry": "entryway", "bathroom": "bathroom",
    "bedroom_1": "bedroom", "bedroom_2": "bedroom.001",
}

S, F, E = "surface", "floor", "enclosed"
PLACES = {
    # living
    "couch_l1":        dict(kind=S, furniture="c3c56c69", band=(0.30, 0.60), tolerance=0.05, called="black sofa"),
    "armchair_l1":     dict(kind=S, furniture="2088726c", instance=0, band=(0.30, 0.60), tolerance=0.05, called="armchair"),
    "coffee_table_l1": dict(kind=S, furniture="24948d65", band=(0.35, 0.50), called="coffee table"),
    "side_table_l1":   dict(kind=S, furniture="590cfd59", band=(0.60, 0.80), tolerance=0.05, called="round side table"),
    "tv_stand_l1":     dict(kind=S, furniture="18907e17", band=(0.55, 0.75), called="small box on a stand",
                            stand_in="the living room has no television stand"),
    "bookshelf_l1":    dict(kind=S, furniture="4e03b1ae", band=(1.10, 1.35), called="top of the fireplace",
                            stand_in="the living room has no bookshelf"),
    "floor_l_l1":      dict(kind=F, near=(0.2, -4.6), called="living room floor"),
    # dining
    "dining_table_d1": dict(kind=S, furniture="125fb349", band=(0.65, 0.85), called="dining table"),
    "sideboard_d1":    dict(kind=S, furniture="51c3494e", band=(0.80, 1.00), called="sideboard"),
    "chair_d_d1":      dict(kind="missing", called="dining chair",
                            stand_in="the dining chairs are pushed under the table, leaving no seat to put things on"),
    # kitchen
    "counter_k1":      dict(kind=S, furniture="997cff30", instance=0, band=(0.80, 1.00), called="kitchen counter"),
    "sink_k1":         dict(kind=S, furniture="87ef4b11", band=(0.60, 1.00), called="counter around the kitchen sink"),
    "dish_rack_k1":    dict(kind=S, furniture="f401c614", instance=0, band=(0.80, 1.00),
                            called="counter beside the sink", stand_in="there is no dish rack"),
    "kitchen_table_k1": dict(kind=S, furniture="f401c614", instance=3, band=(0.80, 1.00),
                             called="counter on the far side of the kitchen",
                             stand_in="the kitchen has no table"),
    "pantry_shelf_k1": dict(kind=S, furniture="f401c614", instance=1, band=(0.80, 1.00),
                            called="counter beside the fridge", stand_in="there is no pantry shelf"),
    "cupboard_k1":     dict(kind=E, called="kitchen cupboard"),
    "drawer_k_k1":     dict(kind=E, called="kitchen drawer"),
    "floor_k_k1":      dict(kind=F, near=(-2.4, 0.2), called="kitchen floor"),
    "chair_k1":        dict(kind="missing", called="kitchen chair"),
    # office
    "desk_o1":         dict(kind=S, furniture="215e08aa", band=(0.65, 0.85), called="desk"),
    "office_chair_o1": dict(kind=S, furniture="8e4f48a4", band=(0.35, 0.60), tolerance=0.05, called="desk chair"),
    "office_shelf_o1": dict(kind=S, furniture="2ad85bce", band=(0.60, 1.15), camera_height=1.22, called="bookcase"),
    "floor_o_o1":      dict(kind=F, near=(0.6, -7.3), called="office floor"),
    # entry
    "entry_table_e1":  dict(kind=S, furniture="d015e61b", band=(0.75, 0.95), called="chest of drawers by the door"),
    "entry_hook_e1":   dict(kind=S, furniture="2bd2ca4a", band=(0.36, 0.53), tolerance=0.05, called="bench",
                            stand_in="the entry has no hooks"),
    "shoe_rack_e1":    dict(kind=F, near=(-2.0, -6.4), called="floor by the bench",
                            stand_in="the entry has no shoe rack"),
    "entry_floor_e1":  dict(kind=F, near=(-2.4, -4.4), called="entry floor"),
    # bathroom
    "sink_ba_ba1":     dict(kind=S, furniture="8bd816e8", band=(0.75, 1.00), called="washstand"),
    "bathroom_shelf_ba1": dict(kind=S, furniture="652536fa", band=(0.55, 0.85), called="edge of the bath",
                               stand_in="the bathroom has no shelf"),
    "towel_rack_ba1":  dict(kind=S, furniture="bd7fd53f", band=(0.30, 0.65), tolerance=0.05,
                            called="closed lid of the toilet",
                            stand_in="the bathroom has no towel rack"),
    "medicine_cabinet_ba1": dict(kind=E, called="medicine cabinet"),
    # bedroom 1 (Dana)
    "bed_b1":          dict(kind=S, furniture="510d13dd", band=(0.35, 0.80), camera_height=1.45, head_toward=(0, -1), tolerance=0.05, called="bed"),
    "nightstand_b1":   dict(kind=S, furniture="9299cfd1", instance=0, band=(0.50, 0.62), called="bedside table"),
    "desk_b1":         dict(kind=S, furniture="9299cfd1", instance=1, band=(0.50, 0.62),
                            called="second bedside table", stand_in="this bedroom has no desk"),
    "dresser_b1":      dict(kind=S, furniture="6c80f089", band=(0.95, 1.15), called="long chest of drawers"),
    "wardrobe_b1":     dict(kind=E, called="wardrobe"),
    "bedroom_floor_b1": dict(kind=F, near=(-7.6, -6.4), called="bedroom floor"),
    # bedroom 2 (Felix)
    "bed_b2":          dict(kind=S, furniture="df47353f", band=(0.35, 0.90), camera_height=1.5, head_toward=(-1, 0), tolerance=0.05, called="bed"),
    "nightstand_b2":   dict(kind=S, furniture="9e5a036b", instance=0, band=(0.50, 0.65), called="bedside table"),
    "desk_b2":         dict(kind=S, furniture="9e5a036b", instance=1, band=(0.50, 0.65),
                            called="second bedside table", stand_in="this bedroom has no desk"),
    "dresser_b2":      dict(kind=S, furniture="a093a534", band=(0.75, 0.95), called="chest of drawers"),
    "wardrobe_b2":     dict(kind=E, called="wardrobe"),
    "bedroom_floor_b2": dict(kind=F, near=(-6.2, 2.2), called="bedroom floor"),
}

# One figure per resident, several poses of the same figure (HSSD "person" models).
PEOPLE = {
    "resident_1": dict(name="Dana", looks_like="woman in a dark red dress", poses={
        "standing": "People Tatiana still", "walking": "People Tatiana walking",
        "lying": "People Tatiana still"}, lying_is="standing figure laid on its back",
        # her hair and heels reach further back than her back does, so resting the box leaves her hovering
        lying_sinks=0.12),
    "resident_2": dict(name="Felix", looks_like="man in a yellow T-shirt and jeans", poses={
        "standing": "Alberto Phone", "walking": "Alberto Phone",   # "Alberto Pointing" holds one arm straight out
        "lying": "Alberto Laid on"}, lying_is="lying figure", lying_sinks=0.07),
}
