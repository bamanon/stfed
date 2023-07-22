import enum



class TerrainType(enum.Enum):
    UNDEFINED = 0
    BRAMBLES = 1
    CHASM = 2
    FLAME_SPOUT = 3
    FOLIAGE = 4
    ROUGH_LAND = 5
    HOTBED = 6
    MARSH = 7
    MINE = 8
    BROKEN_LAND = 9
    ROAD = 10
    OPEN_LAND = 11
    PORTAL = 12
    RUINS = 13
    SWAMP = 14
    WATER = 15
    WHIRLPOOL = 16
    HIGH_FOLIAGE = 17
    OBSTRUCTION = 18
    FOG_TERR = 19
    ROC_NEST = 20
    TERR21 = 21
    TERR22 = 22
    TERR23 = 23
    TERR24 = 24
    TERR25 = 25
    TERR26 = 26
    TERR27 = 27
    TERR28 = 28
    TERR29 = 29
    ARBOR_LODGE = 30
    BARRACKS = 31
    CAMP = 32
    CRYPT = 33
    GATE = 34
    KEEP = 35
    RUNESTONE = 36
    TEMPLE = 37
    STRUCTURE = 38
    WALL = 39
    MONUMENT = 40
    BRIDGE = 41
    STOCKPILE = 42
    GREAT_WALL = 43
    FOUND_ARBORLODGE = 44
    FOUND_BARRACKS = 45
    FOUND_CRYPT = 46
    FOUND_RUNESTONE = 47
    FOUND_TEMPLE = 48
    CAULDRON = 49
    ATLANTEAN_RUIN = 50
    AQUEDUCT = 51
    TERR52 = 52
    TERR53 = 53
    TERR54 = 54
    TRIP_SWITCH = 55
    PRESSURE_PLATE = 56
    WIND_WALL = 57
    GUARDIAN_PORTAL = 58
    GOLEM_PORTAL = 59
    TURRET = 60
    TURRET1 = 61
    TURRET2 = 62
    TURRET3 = 63
    TURRET4 = 64
    TURRET5 = 65
    TURRET6 = 66
    TURRET7 = 67
    TURRET8 = 68
    TURRET9 = 69
    TURRET10 = 70
    TURRET11 = 71
    TURRET12 = 72
    TURRET13 = 73
    TURRET14 = 74
    TURRET15 = 75
    PALADIN_PORTAL = 76
    WARRIOR_PORTAL = 77
    WELL_OF_IMMORTALS = 78
    PLATFORM = 79
    FOUND_GENERIC = 80
    BRIDGE2 = 81
    BANISH_STONE = 82
    PRISON_PIT = 83
#    TERRAINMAXTYPES
    ANY = 1001
    ALL = 1002

walkable = [
    TerrainType.BRAMBLES,
    TerrainType.FLAME_SPOUT,
    TerrainType.FOLIAGE,
    TerrainType.ROUGH_LAND,
    TerrainType.HOTBED, 
    TerrainType.MARSH,
    TerrainType.BROKEN_LAND,
    TerrainType.ROAD,
    TerrainType.OPEN_LAND,
    TerrainType.PORTAL,
    TerrainType.RUINS,
    TerrainType.SWAMP,
    TerrainType.BRIDGE2,
    TerrainType.ROC_NEST
    #TODO
]