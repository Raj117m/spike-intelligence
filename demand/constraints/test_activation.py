from demand.constraints.activator import ConstraintActivator

engine = ConstraintActivator()

events = [

    "Major Storm hits Florida",

    "Inflation reaches new highs",

    "Severe drought across Europe",

    "Large earthquake reported",

    "Heat wave continues",

]

for event in events:

    print()

    print(event)

    print(engine.activate(event))
