# v3 model fixes

One row per object type whose model or size changed in v3 (rules: models_v3.json by hand, models_v3_built.json from make_meshes_v3.py).
Sizes are the placed model's box sides in cm, longest first; typical sizes from typical_sizes_v3.json (Qwen, or by hand).

| type | v2 model | v2 cm | typical cm | v3 model | v3 cm | why |
|---|---|---|---|---|---|---|
| apron |  |  | 30 x 25 x 5 | folded cloth, indigo | 30 x 26.5 x 9.1 | garment / cloth drawn as one generic folded cloth tinted indigo (the garment meshes were stiff hollow shells standing up) |
| belt | Roman soldier's belt - Cingu | 30 x 25.7 x 22.1 | 15 x 15 x 5 | Roman soldier's belt - Cingu | 18 x 15.4 x 13.2 | Roman soldier's belt 30 cm, typical coiled belt 15 cm (1.96x) |
| candle | candlestick bronze dark thin | 15 x 4.6 x 4.6 | 10 x 10 x 10 | Scented Candle | 10 x 8.6 x 8.1 | a tall bronze candlestick for a short amber jar candle; now a candle in a jar (white) |
| canned tomatoes | Can of beans | 12 x 7.2 x 7.1 | 12 x 12 x 7 | three tins in a row | 25 x 10.5 x 8.2 | the object is three tins in a row; it was drawn as one |
| carrots | carrot | 20 x 5.9 x 5.1 | 25 x 15 x 10 | a bunch of four carrots | 22 x 9.9 x 2.6 | the object is a bunch of four carrots; it was drawn as one |
| ceramic tray | wooden container | 40 x 27.8 x 7.8 | 30 x 20 x 3 | Ikan tray M - antique white | 32 x 21.3 x 8.5 | a brown wooden box tray for a white oval ceramic tray |
| chef jacket | Leather Jacket 2 | 50 x 26.4 x 12.8 | 40 x 30 x 10 | folded cloth, black | 36 x 31.8 x 11 | garment / cloth drawn as one generic folded cloth tinted black (the garment meshes were stiff hollow shells standing up) |
| cleaning spray | Spray Paint Can | 25 x 8.5 x 8.5 | 25 x 10 x 10 | Spray Bottle | 25 x 9.2 x 6.9 | a Krylon spray-paint can for a cleaning spray bottle; now a trigger spray bottle |
| cloth napkin | Fete White Cloth Napkin | 30.5 x 28.7 x 2.4 | 20 x 15 x 2 | folded cloth, blue and white (2 models) | 20 x 17.6 x 6.1 | garment / cloth drawn as one generic folded cloth tinted blue and white (the garment meshes were stiff hollow shells standing up) |
| coffee beans | Lays Packet | 25 x 21.7 x 7.9 | 25 x 15 x 8 | Coffee Packaging | 22 x 13.7 x 7.2 | a Lay's crisp packet for a pouch of coffee beans; now a coffee bag |
| dish soap | ACE | 22 x 11.6 x 4.6 | 22 x 8 x 8 | Bottle Washing-up Liquid | 22 x 10.1 x 6.3 | an orange 'Ace' laundry-detergent jug for a bottle of dish soap; now a washing-up liquid bottle (yellow, not green) |
| dish towel | plain cream towel | 40 x 35.3 x 12.2 | 30 x 20 x 5 | plain cream towel | 28 x 24.7 x 8.5 | folded towel models are 40 x 35-38 cm (typical folded towel 30 x 20 cm, middle side 1.9x); a dish towel moved to a free counter in front of  |
| dress | Night Dress | 50 x 26 x 18.9 | 40 x 30 x 10 | folded cloth, olive green | 34 x 30 x 10.4 | garment / cloth drawn as one generic folded cloth tinted olive green (the garment meshes were stiff hollow shells standing up) |
| eggs | Egg | 30 x 22.8 x 22.4 | 15 x 10 x 6 | Egg box | 16 x 11 x 7.2 | a single egg scaled to 30 cm (looked like a melon); the object is a six-egg carton |
| evening shirt | T-shirt T Pose | 40 x 33 x 15.7 | 40 x 30 x 5 | folded cloth, gray | 32 x 28.2 x 9.7 | garment / cloth drawn as one generic folded cloth tinted gray (the garment meshes were stiff hollow shells standing up) |
| evening sweater | Adidas Hoodie | 40 x 22 x 12.9 | 35 x 25 x 8 | folded cloth, oatmeal | 34 x 30 x 10.4 | garment / cloth drawn as one generic folded cloth tinted oatmeal (the garment meshes were stiff hollow shells standing up) |
| gardening gloves | SRG Glove | 25 x 14.6 x 11 | 25 x 15 x 3 | glove laid flat | 25 x 16.6 x 13 | the model stood on one end (glove laid flat) |
| hand cream | MOLTON BROWN ENLIVENING TOKO | 9.7 x 4 x 4 | 15 x 5 x 5 | CC0 - Cream Tube | 15 x 6.3 x 4.8 | a pump bottle for a tube of hand cream; now a cream tube |
| honey jar | Formalin-filled jar | 12 x 7.3 x 7.2 | 10 x 10 x 10 | Honey bear bottle | 13 x 6.1 x 5.8 | a white 'formalin-filled jar' for an amber bear-shaped honey jar |
| hoodie | hoodie | 45 x 25 x 15.8 | 35 x 25 x 10 | folded cloth, navy | 36 x 31.8 x 11 | garment / cloth drawn as one generic folded cloth tinted navy (the garment meshes were stiff hollow shells standing up) |
| jacket | Leather Jacket 2 | 50 x 26.4 x 12.8 | 40 x 30 x 10 | folded cloth, faded blue | 38 x 33.5 x 11.6 | garment / cloth drawn as one generic folded cloth tinted faded blue (the garment meshes were stiff hollow shells standing up) |
| jeans | Blue Jeans Pants | 40 x 16.5 x 9.1 | 40 x 30 x 10 | folded cloth, dark indigo | 36 x 31.8 x 11 | garment / cloth drawn as one generic folded cloth tinted dark indigo (the garment meshes were stiff hollow shells standing up) |
| kitchen clogs | Day 198: Nike Air Force 1 | 30 x 13.9 x 12.2 | 28 x 12 x 10 | Crocsss | 28 x 12 x 10.8 | a white Nike trainer for black rubber kitchen clogs; now a rubber clog (purple, not black) |
| kitchen towel | plain cream towel | 40 x 35.3 x 12.2 | 30 x 20 x 5 | plain cream towel | 28 x 24.7 x 8.5 | folded towel models are 40 x 35-38 cm (typical folded towel 30 x 20 cm, middle side 1.9x); a dish towel moved to a free counter in front of  |
| knives | Butcher Knife | 25 x 6.7 x 1.2 | 20 x 3 x 1 | PBR - Kitchen Knife | 25 x 10 x 6.2 | a butcher's cleaver for kitchen knives |
| landscape magazine | Books Magazines | 28 x 14.8 x 14.8 | 28 x 21 x 1 | Closed Magazine | 28 x 16.2 x 0.8 | two stacks of about 30 magazines for one magazine; now one closed magazine |
| laundry soap | ACE | 20 x 10.5 x 4.2 | 10 x 6 x 3 | Soap | 10 x 10 x 4.2 | a 20 cm detergent bottle for a paper-wrapped bar of soap |
| lemons | Lemon | 8 x 7.6 x 7.6 | 25 x 10 x 10 | three lemons lying together | 17 x 11.8 x 6.3 | the object is three lemons lying together; it was drawn as one |
| linen scarf | Scarf2 | 40 x 25.2 x 16.4 | 30 x 20 x 5 | folded cloth, blue gray | 28 x 24.7 x 8.5 | garment / cloth drawn as one generic folded cloth tinted blue gray (the garment meshes were stiff hollow shells standing up) |
| lounge pants | Sweatpants | 40 x 17.7 x 12.7 | 35 x 25 x 5 | folded cloth, black (2 models) | 34 x 30 x 10.4 | garment / cloth drawn as one generic folded cloth tinted black (the garment meshes were stiff hollow shells standing up) |
| market herbs | Grass | 25 x 24.6 x 15.9 | 25 x 12 x 10 | Herbs, Basil | 25 x 17.8 x 17.7 | 'Grass' model drawn as shredded white strands; potted basil instead (the object is basil and mint in a glass) |
| mechanical pencil | Pencil | 14 x 7.7 x 6.4 | 15 x 1 x 1 | Mechanical pencil | 15 x 1.7 x 1.3 | a wooden pencil for a mechanical pencil |
| napkins | Fete White Cloth Napkin | 30.5 x 28.7 x 2.4 | 25 x 25 x 10 | folded cloth, blue | 24 x 21.2 x 7.3 | garment / cloth drawn as one generic folded cloth tinted blue (the garment meshes were stiff hollow shells standing up) |
| paper towels | Squeezer Kitchen Roll Holder | 29.4 x 15.4 x 13.7 | 25 x 12 x 12 | Paper Towel Roll | 25 x 13 x 11.8 | a 29 cm woven kitchen-roll holder that could not be recognised; now a paper towel roll on a small stand |
| parcel | Stylized Low Poly Wooden Cra | 35 x 35 x 34.9 | 20 x 15 x 5 | Closed Cardboard Box (Free D | 22 x 16.6 x 16.4 | a 35 cm wooden crate for a small kraft parcel |
| paring knife | Butcher Knife | 20 x 5.3 x 0.9 | 15 x 3 x 2 | PBR - Kitchen Knife | 18 x 7.2 x 4.5 | a butcher's cleaver for a paring knife |
| pasta | Lays Packet | 25 x 21.7 x 7.9 | 30 x 20 x 10 | USSR Coffee Bag | 25 x 13.3 x 8.1 | a Lay's crisp packet for a paper bag of rigatoni; now a plain paper bag (a coffee bag model) |
| pen | Pencil | 14 x 12.3 x 1.1 | 14 x 1.5 x 1.5 | Pen (2 models) | 14 x 1.2 x 1 | a wooden pencil for a gel / felt-tip pen |
| phone | phone_223b376823b5 | 15 x 5 x 3 | 15 x 7.5 x 0.8 | Cell Phone (3 models) | 15 x 8.6 x 0.9 | a 1980s brick phone for a black glass smartphone |
| phone charger | white plug with a long cable | 20 x 17 x 2.1 | 15 x 10 x 3 | white plug with a long cable | 14 x 11.9 x 1.4 | plug with its cable laid in a loop 20 x 17 cm took half a nightstand top (680 cm2 turned); coiled smaller, 14 cm |
| pillowcase | Pillow | 50 x 49.5 x 14 | 45 x 30 x 2 | folded cloth, white | 36 x 31.8 x 11 | garment / cloth drawn as one generic folded cloth tinted white (the garment meshes were stiff hollow shells standing up) |
| plasters | BLOODY BAND-AID | 10 x 2.8 x 1.8 | 10 x 7 x 3 | Modern Combat Bandage Packag | 10 x 7.5 x 1.2 | a single blood-stained plaster for a tin of plasters; now a plaster packet |
| pruning shears | garden shears outdoors heavy | 30 x 20.4 x 2 | 20 x 8 x 3 | pruning shears laid flat | 20 x 17.5 x 1.9 | the model stood on one end (pruning shears laid flat) |
| restaurant shirt | T-shirt T Pose | 40 x 33 x 15.7 | 35 x 25 x 3 | folded cloth, white | 32 x 28.2 x 9.7 | garment / cloth drawn as one generic folded cloth tinted white (the garment meshes were stiff hollow shells standing up) |
| reusable shopping bags | Bought Bread | 40 x 37.8 x 26.1 | 35 x 25 x 5 | Renova Shopping Bag 03 | 35 x 23.9 x 10.4 | a paper bag of bread rolls for folded canvas shopping bags; now an empty shopping bag |
| rice | Lays Packet | 25 x 21.7 x 7.9 | 40 x 25 x 15 | Rice Bag | 30 x 22.2 x 3.1 | a Lay's crisp packet for a sack of rice; now a rice bag |
| robe | Kimono | 50 x 33.5 x 15.8 | 40 x 30 x 10 | folded cloth, gray | 40 x 35.3 x 12.2 | garment / cloth drawn as one generic folded cloth tinted gray (the garment meshes were stiff hollow shells standing up) |
| rolling pin | KOSMOS Sensor Holder Pin V6 | 40 x 3.8 x 3.8 | 28 x 5 x 5 | Wooden Rolling Pin | 30 x 8.6 x 8.4 | a blue 'sensor holder pin' rod for a beech rolling pin |
| rubber gloves | SRG Glove | 30 x 17.5 x 13.2 | 25 x 15 x 2 | glove laid flat | 28 x 18.6 x 14.5 | the model stood on one end (glove laid flat) |
| salt cellar | Salt pot and spoon | 19.6 x 10 x 9.7 | 10 x 10 x 4 | Salt shaker | 10 x 4.7 x 4.7 | two salt pots with a spoon, 20 cm long, for one salt cellar |
| serving platter | Cheese Platter | 40 x 20.1 x 8.9 | 35 x 25 x 3 | Lacquer plate (HSSD) | 36 x 36 x 1.6 | a cheese board with cheese on it for an oval white serving platter; now a large plain white plate |
| silicone spatula | Spatula (Spongebob) | 28 x 8.5 x 1.5 | 28 x 5 x 2 | Silicone Spatula △613 | 28 x 6.4 x 1.2 | a metal fish slice (Spongebob) for a silicone spatula |
| sketchbook | Vinyl Record Sketch Book | 20.3 x 19.2 x 1.8 | 21 x 15 x 2 | Skyline A3 Sketchbook | 30 x 22 x 2.7 | a vinyl record for a sketchbook; now a plain A3 sketchbook (no cover print) |
| sleep pants | Sweatpants | 35 x 15.5 x 11.2 | 30 x 20 x 5 | folded cloth, blue (2 models) | 32 x 28.2 x 9.7 | garment / cloth drawn as one generic folded cloth tinted blue (the garment meshes were stiff hollow shells standing up) |
| sleep shirt | T-shirt T Pose | 35 x 28.9 x 13.8 | 35 x 25 x 5 | folded cloth, blue (2 models) | 32 x 28.2 x 9.7 | garment / cloth drawn as one generic folded cloth tinted blue (the garment meshes were stiff hollow shells standing up) |
| socks | Women's 80's/90's Rainbow Sk | 25 x 24.2 x 8.5 | 25 x 15 x 5 | folded cloth, black | 15 x 13.2 x 4.6 | garment / cloth drawn as one generic folded cloth tinted black (the garment meshes were stiff hollow shells standing up) |
| spare umbrella | Elegant umbrella | 60 x 60 x 47.6 | 30 x 8 x 8 | Closed umbrella from Poly by | 35 x 10.8 x 4.8 | an open umbrella 60x60x48 cm for a folded spare umbrella; replaced by a closed umbrella (red, not navy) |
| stain remover | Old Medicine Jar | 20 x 8.2 x 8.2 | 25 x 10 x 10 | Sprayer bottle | 22 x 10 x 4.4 | a stoppered medicine jar for an orange spray bottle; now a trigger spray bottle (green and yellow) |
| sticky notes | Notebook | 8 x 5 x 0.4 | 8 x 8 x 2 | Post It Note | 8 x 7.8 x 2 | a spiral notebook for a sticky-notes pad; now a yellow sticky note |
| table knives | Butcher Knife | 22 x 5.9 x 1 | 20 x 3 x 1 | Butter Knife | 22 x 2.6 x 0.5 | a butcher's cleaver (and a thin black stick) for table knives |
| tea towels | plain cream towel | 40 x 35.3 x 12.2 | 30 x 20 x 2 | plain cream towel | 28 x 24.7 x 8.5 | folded towel models are 40 x 35-38 cm (typical folded towel 30 x 20 cm, middle side 1.9x); a dish towel moved to a free counter in front of  |
| throw blanket | Throw | 49.9 x 29.8 x 10 | 40 x 30 x 10 | folded cloth, rust orange | 42 x 37.1 x 12.8 | garment / cloth drawn as one generic folded cloth tinted rust orange (the garment meshes were stiff hollow shells standing up) |
| tongs | Tongue mites 01 | 30 x 8 x 2.6 | 25 x 8 x 3 | Tongs from Poly by Google | 25 x 18 x 3 | 'tongue mites' model (blacksmith pincers) for kitchen tongs |
| towel | plain cream towel | 40 x 35.3 x 12.2 | 30 x 20 x 5 | plain cream towel (6 models) | 32 x 28.2 x 9.7 | folded towel models are 40 x 35-38 cm (typical folded towel 30 x 20 cm, middle side 1.9x); a dish towel moved to a free counter in front of  |
| wallet | brown leather old beige | 15.4 x 14.9 x 13.6 | 11 x 9 x 2 | brown leather old beige (2 models) | 12 x 11.6 x 10.6 | 15 cm wallet (typical 11 cm) |
| water bottle | dark grey bottle with a blue | 25 x 7.9 x 7.9 | 25 x 8 x 8 | Thermos Everyday Flask (stee | 25 x 6.5 x 6.4 | a coarse low-poly blue and white bottle (flat facets, looked huge near the camera) for a clear steel water bottle; now a steel flask |
| wooden tray | Aluminum tray | 45 x 27.7 x 14.6 | 40 x 25 x 3 | Solid oak rectangular tray | 42 x 30.8 x 5.6 | a deep aluminium baking tray 15 cm tall (looked like a black bucket from the counter) for a flat walnut serving tray |
| wool socks | Women's 80's/90's Rainbow Sk | 25 x 24.2 x 8.5 | 25 x 15 x 8 | folded cloth, mustard yellow | 16 x 14.1 x 4.9 | garment / cloth drawn as one generic folded cloth tinted mustard yellow (the garment meshes were stiff hollow shells standing up) |
| work blouse | Blouse Kaftan Batik 1 | 35 x 19.6 x 8.5 | 35 x 25 x 5 | folded cloth, ivory (2 models) | 32 x 28.2 x 9.7 | garment / cloth drawn as one generic folded cloth tinted ivory (the garment meshes were stiff hollow shells standing up) |
| work cardigan | Kimono Cardigan | 40 x 16.1 x 9.7 | 40 x 30 x 10 | folded cloth, rust | 34 x 30 x 10.4 | garment / cloth drawn as one generic folded cloth tinted rust (the garment meshes were stiff hollow shells standing up) |
| work loafers | Shoes - All Stars | 25.5 x 21.4 x 13.3 | 30 x 25 x 12 | Shoes loafers | 28 x 19.1 x 8.3 | red high-top canvas trainers for brown leather loafers; now a pair of loafers |
| work trousers | Trousers 1 | 40 x 20.8 x 12.6 | 40 x 30 x 10 | folded cloth, black (2 models) | 36 x 31.8 x 11 | garment / cloth drawn as one generic folded cloth tinted black (the garment meshes were stiff hollow shells standing up) |

## Still flagged on the longest side, left as they are

| type | model | model cm | typical cm | why left |
|---|---|---|---|---|
| batteries | battery | 5 x 4.8 x 2.7 | 12 x 6 x 2 | the model is one battery, the right size for one; the object is a pack |
| canned tomatoes | three tins in a row | 25 x 10.5 x 8.2 | 12 x 12 x 7 | three tins in a row (25 cm); Qwen's size is for one tin |
| clothespins | Clothespin | 7 x 1.8 x 1 | 15 x 10 x 3 | one clothespin, the right size for one; the object is a pack |
| hair ties | Rubber wrist bands | 5 x 2.7 x 1.7 | 10 x 8 x 5 | one band, the right size for one; the object is a bundle |
| phone charger | light grey plug block with a | 7 x 3.6 x 1.9 | 15 x 10 x 3 | the model is the plug block alone, the right size for a plug |
| watch | hand watch  (FREE MODEL) | 5 x 3.7 x 2.6 | 22 x 5 x 1 | the watch with its strap closed; Qwen's 22 cm is the strap laid out flat |
