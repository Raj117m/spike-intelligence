from demand.validation.mechanism_learning import MechanismLearning

m = MechanismLearning()

m.initialize()

m.update(

    "FLOOD_SUPPLY_CHAIN",

    True,

)

m.update(

    "FLOOD_SUPPLY_CHAIN",

    True,

)

m.update(

    "FLOOD_SUPPLY_CHAIN",

    False,

)

m.update(

    "HEALTH_PROTECTION",

    True,

)

print()

print(m.report())
