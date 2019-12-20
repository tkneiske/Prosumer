# Prosumer
MILP/ModelPredictiveControl for a single family home
(you need Inputfiles in addition to the code, which are unfortunatlely too big for github)


I have included different energy systems
CHP - combined heat and power plant
WP - Heatpump
Eheater - Eheater
TES - Thermal energy storage
PV - Photovoltaic
Batt - Battery

And I optimized for different cost funtions
costs - operational costs
Co2 - Co2 emission
self-consumption
minimal grid interaction

for more information read my papers in Applied Energy

AdHoc - means a two level combined control ist used: (1) MPC (every 10 min) + (2) rule-based (within the 10 min)

AdHocV - means a variable, two level combined control ist used: (1) MPC (every X min until the set-values of the SOCs are 10% off from the real values) + (2) rule-based (within the time period)
