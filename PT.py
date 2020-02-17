'''
Script to Download and convert Technic launcher modpacks to be more Multimc compatible*
by RedstoneLP2
'''

import sys

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

PT=["","Hydrogen","Helium","Lithium","Berylium","Boron","Carbon","Nitrogen","Oxygen","Flourine","Neon","Sodium","Magnesium","Aluminium","Silicon","Phosphorus","Sulfur","Chlorine","Argon","Potassium","Calcium","Scandium","Titanium","Vanadium","Chromium","Manganese","Iron", "Cobalt","Nickel","Copper","Zinc","Gallium","Germanium","Arsenic","Selenium","Bromine","Krypton","Rubidium","Strontium","Yttrium","Zirconium","Niobium","Molybdenum","Technetium","Ruthenium","Rhodium","Paladium","Silver","Cadmium","Indium","Tin","Antimony","Tellurium","Iodine","Xenon","Caesium","Barium","Lanthanum","Cerium","Praseodymium","Neodymium","Promethium","Samarium","Europium","Gadolinium","Terbium","Dysprosium","Holmium","Erbium","Thulium","Ytterbium","Lutetium","Hafnium","Tantalum","Tungsten","Rhenium","Osmium","Iridium","Platinum","Gold","Mercury","Thallium","Lead","Bismuth","Polonium","Astatine","Radon","Francium","Radium","Actinium","Throium","Protactinium","Uranium","Neptunium","Plutonium","Americium","Curium","Berkelium","Californium","Einsteinium","Fermium","Mendelevium","Nobelium","Lawrencium","Rutherfordium","Dubnium","Seaborgium","Bohrium","Hassium","Meitnerium","Darmstadtium","Roentgenium","Copernicum","Flerovium","Moscovium","Livermorium","Tennessine","Oganesson"]


userinput=int(input("Number of wanted Element: "))
half=userinput//2
print(half)
for i in range(1,half+1):
	print(PT[i])
	print(PT[userinput-i])
	print("------")