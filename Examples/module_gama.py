'''
Created on Jun 26, 2017

@author: jupiparmar1
'''
import tam2


N = tam2.Direction.North
S = tam2.Direction.South
E = tam2.Direction.East
W = tam2.Direction.West

#Transition to Port Tile Templates
msbTrans = tam2.TileTemplate(name="msbTrans")
interiorTrans = tam2.TileTemplate(name="interiorTrans")
lsbTrans = tam2.TileTemplate(name="lsbTrans")
def addTileTemplatesToModule(tileTempList, module):
    for tile in tileTempList:
        module.add(tile)
def createBottomLogGrowMod(name,tst):
    bottomLogGrowMod = tam2.Module(name)
    #seed tile templates
    seed1 = tam2.TileTemplate(name="Seed1")
    seed2 = tam2.TileTemplate(name="Seed2")
    seed3 = tam2.TileTemplate(name="Seed3")
    seed4 = tam2.TileTemplate(name="Seed4")
    seed5 = tam2.TileTemplate(name="Seed5")
    seed6 = tam2.TileTemplate(name="Seed6")

    #tile templates to grow the bottom left module -- growth using binary
    lsbCp = tam2.TileTemplate(name="lsbCp")
    lsbInc = tam2.TileTemplate(name="lsbInc")
    msbCp = tam2.TileTemplate(name="msbCp")
    msbInc = tam2.TileTemplate(name="msbInc")
    interiorCp = tam2.TileTemplate(name="intCp")
    interiorInc = tam2.TileTemplate(name="intInc")
    tiles = [seed1,seed2,seed3,seed4,seed5,seed6,lsbCp,lsbInc,msbCp,msbInc,interiorCp,interiorInc,msbTrans,interiorTrans,lsbTrans]
    addTileTemplatesToModule(tiles, bottomLogGrowMod)

    bottomLogGrowMod.join(2, W, seed1, seed2, tst, seed1 = "s1")
    bottomLogGrowMod.join(2, W, seed2, seed3, tst, seed2 = "s2")
    bottomLogGrowMod.join(2, W, seed3, seed4, tst, seed3 = "s3")
    bottomLogGrowMod.join(2, W, seed4, seed5, tst, seed4 = "s4")
    bottomLogGrowMod.join(2, W, seed5, seed6, tst, seed5 = "s5")
    bottomLogGrowMod.join(2, N, seed1, lsbInc, tst, lsbIncBit = "0*")
    bottomLogGrowMod.join(1, N, seed2, interiorInc, tst, intBit = "0")
    bottomLogGrowMod.join(1, N, seed3, interiorInc, tst, intBit = "0")
    bottomLogGrowMod.join(1, N, seed4, interiorInc, tst, intBit = "0")
    bottomLogGrowMod.join(1, N, seed5, interiorInc, tst, intBit = "0")
    bottomLogGrowMod.join(1, N, seed6, msbInc, tst, msbIncBit = "*0")

    #Joins For the copy
    bottomLogGrowMod.join(1, N, lsbInc, lsbCp, tst, lsbCpBit = ("0*","1*"))
    bottomLogGrowMod.join(1, E, interiorCp, lsbCp, tst, cpSig = "x")
    bottomLogGrowMod.join(2, N, lsbCp, lsbInc, tst, lsbIncBit = ("0*","1*"))
    bottomLogGrowMod.join(1, N, interiorInc, interiorCp, tst, intBit = ("0","1"))
    bottomLogGrowMod.join(1, E, msbCp, interiorCp, tst, cpSig = "x")
    bottomLogGrowMod.join(1, E, interiorCp, interiorCp, tst, cpSig = "x")
    bottomLogGrowMod.join(1, N, interiorCp, interiorInc, tst, intBit = ("0","1"))
    bottomLogGrowMod.join(2, N, msbInc, msbCp,tst, msbCpBit = ("*1","*0"))
    bottomLogGrowMod.join(1, N, msbCp, msbInc, tst, msbIncBit = ("*0","*1"))

    #Joins for the Inc
    bottomLogGrowMod.join(1, W, lsbInc, interiorInc, tst, incSig = ("n","c"))
    bottomLogGrowMod.join(1, W, interiorInc, interiorInc, tst, incSig =  ("n","c"))
    bottomLogGrowMod.join(1, W, interiorInc, msbInc, tst, incSig = ("n","c"))

    #Joins to Transition to Port Tile Templates
    bottomLogGrowMod.join(2, N, msbInc, msbTrans, tst, msbCpBit = ("A*"))
    bottomLogGrowMod.join(1, N, interiorInc, interiorTrans, tst, intBit = "0")
    bottomLogGrowMod.join(1, N, lsbInc, lsbTrans, tst, lsbCpBit = "0*")
    bottomLogGrowMod.join(1, E, msbTrans, interiorTrans, tst, intFill = "f")
    bottomLogGrowMod.join(1, E, interiorTrans, interiorTrans, tst, intFill = "f")
    bottomLogGrowMod.join(1, E, interiorTrans, lsbTrans, tst, intFill = "f")

    lsbCp.addTransition(inputs=("lsbCpBit","cpSig"), outputs=("lsbIncBit"),table={("0*","x"):("0*"), ("1*","x"):("1*")})
    lsbInc.addTransition(inputs=("lsbIncBit"), outputs=("lsbCpBit","incSig"), table={("1*",) : ("0*","c"), ("0*",):("1*","n")})
    msbCp.addTransition(inputs=("msbCpBit"), outputs=("msbIncBit","cpSig"), table={("*1",):("*1","x"), ("*0",):("*0","x")})
    msbInc.addTransition(inputs=("msbIncBit","incSig"), outputs=("msbCpBit"), table={("*1","c"):("A*"),("*0","c"):("*1"), ("*1","n"):("*1"),("*0","n"):("*0")})
    interiorCp.addTransition(inputs=("cpSig","intBit"), outputs=("cpSig","intBit"),table={("x","1"):("x","1"),("x","0"):("x","0")})
    interiorInc.addTransition(inputs=("intBit","incSig"), outputs=("intBit","incSig"), table={("1","c"):("0","c"),("1","n"):("1","n"),("0","c"):("1","n"),("0","n"):("0","n")})


    return bottomLogGrowMod
# Beginning tile templates for left transition Module
msbTransSeed = tam2.TileTemplate("msbTransSeed")
interiorTransSeed = tam2.TileTemplate("interiorTransSeed")
lsbTransSeed = tam2.TileTemplate("lsbTransSeed")
interiorFlipperSeed = tam2.TileTemplate("interiorFlipperSeed")
msbFlipperSeed = tam2.TileTemplate("msbFlipperSeed")
def createLeftTransitionMod(name,tst):
    leftTransitionMod = tam2.Module(name)
    #Tile Templates For Left Transition Module
    topA = tam2.TileTemplate(name="topA")
    topB = tam2.TileTemplate(name="topB")
    topFillerA = tam2.TileTemplate(name="topFillerA")
    topFillerB = tam2.TileTemplate(name="topFillerB")
    tiles = [msbTransSeed, interiorTransSeed, lsbTransSeed, interiorFlipperSeed, msbFlipperSeed, topA, topB, topFillerA, topFillerB]
    addTileTemplatesToModule(tiles, leftTransitionMod)

    #Joins for beginning seeds of left transition module
    leftTransitionMod.join(1, E, msbTransSeed, interiorTransSeed, tst, leftTransSeed = 0)
    leftTransitionMod.join(1, E, interiorTransSeed, interiorTransSeed, tst, leftTransSeed = 0)
    leftTransitionMod.join(1, E, interiorTransSeed, lsbTransSeed, tst, leftTransSeed = 0)

    #Joins for tile templates in left transition module
    leftTransitionMod.join(2, N, msbTransSeed, topA, tst, aSig = "A")
    leftTransitionMod.join(1, N, interiorTransSeed, topB, tst, bFill = "b")
    leftTransitionMod.join(1, N, interiorTransSeed, topFillerB, tst, bFill = "b")
    leftTransitionMod.join(1, N, lsbTransSeed, interiorFlipperSeed, tst, intFlip = "iF")
    leftTransitionMod.join(1, N, interiorFlipperSeed, msbFlipperSeed, tst, intFlip = "iF")
    leftTransitionMod.join(1, N, interiorFlipperSeed, interiorFlipperSeed, tst, intFlip = "iF")
    leftTransitionMod.join(1, E, topA, topB, tst, cSig = "c")
    leftTransitionMod.join(2, N, topB, topA, tst, aSig = "A")
    leftTransitionMod.join(1, N, topA, topFillerA, tst, aFill = "a")
    leftTransitionMod.join(1, W, topA, topFillerA, tst, aFillHoriz = "a")
    leftTransitionMod.join(1, N, topFillerB, topB, tst, bFill = "b")
    leftTransitionMod.join(1, N, topFillerA, topFillerA, tst, aFill = "a")
    leftTransitionMod.join(1, W, topFillerA, topFillerA, tst, aFillHoriz = "a")
    leftTransitionMod.join(1, E, topFillerB, topFillerB, tst, bFillHoriz = "b")
    leftTransitionMod.join(1, E, topB, topFillerB, tst, bFillHoriz = "b")
    leftTransitionMod.join(1, N, topFillerB, topFillerB, tst, bFill = "b")
    leftTransitionMod.join(1, E, topFillerB, interiorFlipperSeed, tst, bFillHoriz = "b")
    leftTransitionMod.join(1, E, topA, msbFlipperSeed, tst, cSig = "c")


    return leftTransitionMod
#Beginning tile templates for top Grow module
lsbPortTop = tam2.TileTemplate(name="lsbPortTop")
msbPortTop = tam2.TileTemplate(name="msbportTop")
interiorPortTop = tam2.TileTemplate(name="intPortTop")
msbTransTop = tam2.TileTemplate("msbTransTop")
intTransTop = tam2.TileTemplate("intTransTop")
lsbTransTop = tam2.TileTemplate("lsbTransTop")
def createTopGrowMod(name,tst):
    topGrowMod = tam2.Module(name)
    #tile templates for Top Grow Module
    lsbIncTop = tam2.TileTemplate(name="lsbIncTop")
    msbIncTop = tam2.TileTemplate(name="msbIncTop")
    interiorIncTop = tam2.TileTemplate(name="intIncTop")
    lsbCpTop = tam2.TileTemplate(name="lsbCpTop")
    msbCpTop = tam2.TileTemplate(name="msbCpTop")
    interiorCpTop = tam2.TileTemplate("interiorCpTop")
    tiles = [lsbPortTop,msbPortTop,interiorPortTop,msbTransTop,intTransTop,lsbTransTop,lsbIncTop,msbIncTop,interiorIncTop,lsbCpTop,msbCpTop,interiorCpTop]
    addTileTemplatesToModule(tiles, topGrowMod)
    topGrowMod.join(1, N, lsbPortTop, interiorPortTop, tst, portFill = "pF")
    topGrowMod.join(1, N, interiorPortTop, interiorPortTop, tst, portFill = "pF")
    topGrowMod.join(1, N, interiorPortTop, msbPortTop, tst, portFill = "pF")
    topGrowMod.join(2, E, lsbPortTop, lsbIncTop, tst,  lsbIncBitTop = "0*")
    topGrowMod.join(1, E, msbPortTop, msbIncTop, tst, msbIncBitTop = "*0")
    topGrowMod.join(1, E, interiorPortTop, interiorIncTop, tst, intBitTop = "0")

    #joins For copy tile templates in top grow module
    topGrowMod.join(1, E, lsbIncTop, lsbCpTop, tst, lsbCpBitTop = ("0*","1*"))
    topGrowMod.join(1, S, interiorCpTop, lsbCpTop, tst, cpSigTop = "x")
    topGrowMod.join(2, E, lsbCpTop, lsbIncTop, tst, lsbIncBitTop = ("0*","1*"))
    topGrowMod.join(1, E, interiorIncTop, interiorCpTop, tst, intBitTop = ("0","1"))
    topGrowMod.join(1, S, msbCpTop, interiorCpTop, tst, cpSigTop = "x")
    topGrowMod.join(1, S, interiorCpTop, interiorCpTop, tst, cpSigTop = "x")
    topGrowMod.join(1, E, interiorCpTop, interiorIncTop, tst, intBitTop = ("0","1"))
    topGrowMod.join(2, E, msbIncTop, msbCpTop, tst, msbCpBitTop = ("*1","*0"))
    topGrowMod.join(2, E, msbIncTop, msbTransTop , tst, msbCpBitTop = ("A*"))
    topGrowMod.join(1, E, msbCpTop, msbIncTop, tst, msbIncBitTop = ("*0","*1"))


    #Joins for Inc tile templates in top grow module
    topGrowMod.join(1, N, lsbIncTop, interiorIncTop, tst, incSigTop = ("n","c"))
    topGrowMod.join(1, N, interiorIncTop, interiorIncTop, tst, incSigTop =  ("n","c"))
    topGrowMod.join(1, N, interiorIncTop, msbIncTop, tst, incSigTop = ("n","c"))
    topGrowMod.join(1, E, interiorIncTop, intTransTop, tst, intBitTop = "0")
    topGrowMod.join(1, E, lsbIncTop, lsbTransTop, tst, lsbCpBitTop = "0*")

    #Joins for Transition Top Tiles in top grow module
    topGrowMod.join(1, S, msbTransTop, intTransTop, tst, transTop = "tTop")
    topGrowMod.join(1, S, intTransTop, intTransTop, tst, transTop = "tTop")
    topGrowMod.join(1, S, intTransTop, lsbTransTop, tst, transTop = "tTop")

    lsbCpTop.addTransition(inputs=("lsbCpBitTop","cpSigTop"), outputs=("lsbIncBitTop"),table={("0*","x"):("0*"), ("1*","x"):("1*")})
    lsbIncTop.addTransition(inputs=("lsbIncBitTop"), outputs=("lsbCpBitTop","incSigTop"), table={("1*",) : ("0*","c"), ("0*",):("1*","n")})
    msbCpTop.addTransition(inputs=("msbCpBitTop"), outputs=("msbIncBitTop","cpSigTop"), table={("*1",):("*1","x"), ("*0",):("*0","x")})
    msbIncTop.addTransition(inputs=("msbIncBitTop","incSigTop"), outputs=("msbCpBitTop"), table={("*1","c"):("A*"),("*0","c"):("*1"), ("*1","n"):("*1"),("*0","n"):("*0")})
    interiorCpTop.addTransition(inputs=("cpSigTop","intBitTop"), outputs=("cpSigTop","intBitTop"),table={("x","1"):("x","1"),("x","0"):("x","0")})
    interiorIncTop.addTransition(inputs=("intBitTop","incSigTop"), outputs=("intBitTop","incSigTop"), table={("1","c"):("0","c"),("1","n"):("1","n"),("0","c"):("1","n"),("0","n"):("0","n")})



    return topGrowMod
msbStartSeed = tam2.TileTemplate("msbStartSeed")
intStartSeed = tam2.TileTemplate("intStartSeed")
lsbStartSeed = tam2.TileTemplate("lsbStartSeed")
intFlipStartSeed = tam2.TileTemplate("intFlipStartSeed")
msbFlipStartSeed = tam2.TileTemplate("msbFlipStartSeed")
def createRightTransitionMod(name,tst):
    rightTransitionMod = tam2.Module(name)
    #Right Transition Module Tile Templates
    fillerE = tam2.TileTemplate(name="fillerE")
    fillerD = tam2.TileTemplate(name="fillerD")
    topE = tam2.TileTemplate(name="topE")
    topD = tam2.TileTemplate(name="topD")
    tiles = [msbStartSeed, intStartSeed, lsbStartSeed, intFlipStartSeed, msbFlipStartSeed, fillerE, fillerD, topE,topD]
    addTileTemplatesToModule(tiles, rightTransitionMod)

    rightTransitionMod.join(1, S, msbStartSeed, intStartSeed, tst, transStartTop = "tSTop")
    rightTransitionMod.join(1, S, intStartSeed, intStartSeed, tst, transStartTop = "tSTop")
    rightTransitionMod.join(1, S, intStartSeed, lsbStartSeed, tst, transStartTop = "tSTop")

    #Joins For Tile Templates in Right Transition Module
    rightTransitionMod.join(2, E, msbStartSeed, topD, tst, dSig = "D")
    rightTransitionMod.join(1, E, intStartSeed, topE,tst, eFill = "e")
    rightTransitionMod.join(1, E, intStartSeed, fillerE,tst, eFill = "e")
    rightTransitionMod.join(1, S, topD, topE,tst, tSig = "t")
    rightTransitionMod.join(1, E, topD, fillerD,tst, dFill = "d")
    rightTransitionMod.join(1, N, topD, fillerD,tst, dFillerVert = "d")
    rightTransitionMod.join(1, E, fillerD, fillerD,tst, dFill = "d")
    rightTransitionMod.join(1, N, fillerD, fillerD,tst, dFillerVert = "d")
    rightTransitionMod.join(1, E, fillerE, topE,tst, eFill = "e")
    rightTransitionMod.join(1, S, topE, fillerE,tst, eFillVert = "e")
    rightTransitionMod.join(2, E, topE, topD,tst, dSig = "D")
    rightTransitionMod.join(1, E, fillerE, fillerE,tst, eFill = "e")
    rightTransitionMod.join(1, S, fillerE, fillerE,tst, eFillVert = "e")
    rightTransitionMod.join(1, S, fillerE, intFlipStartSeed,tst, eFillVert = "e")
    rightTransitionMod.join(1, S, topE, intFlipStartSeed, tst,eFillVert = "e")
    rightTransitionMod.join(1, S, topD, msbFlipStartSeed,tst, tSig = "t")
    rightTransitionMod.join(1, E, lsbStartSeed, intFlipStartSeed, tst, fSS = 0)
    rightTransitionMod.join(1, E, intFlipStartSeed, intFlipStartSeed, tst, fSS = 0)
    rightTransitionMod.join(1, E, intFlipStartSeed, msbFlipStartSeed, tst, fSS = 0)


    return rightTransitionMod
msbBotRight = tam2.TileTemplate("msbBotRight")
lsbBotRight = tam2.TileTemplate("lsbBotRight")
intBotRight = tam2.TileTemplate("intBotRight")
def createBottomRightSquareMod(name,tst):
    bottomRightSquareMod = tam2.Module(name)
    #Bottom Right Square Module Tile Template
    fillerH = tam2.TileTemplate(name="fillerH")
    fillerG = tam2.TileTemplate(name="fillerG")
    topH = tam2.TileTemplate(name="topH")
    topG = tam2.TileTemplate(name="topG")
    intBotRightFill = tam2.TileTemplate(name="intBotRightFill")
    msbBotRightFill = tam2.TileTemplate(name="msbBotRightFill")
    tiles = [msbBotRight,lsbBotRight,intBotRight,fillerG,fillerH,topG,topH,intBotRightFill,msbBotRightFill]
    addTileTemplatesToModule(tiles, bottomRightSquareMod)

    bottomRightSquareMod.join(1, W, msbBotRight, intBotRight, tst, bRFill = 0)
    bottomRightSquareMod.join(1, W, intBotRight, intBotRight, tst, bRFill = 0)
    bottomRightSquareMod.join(1, W, intBotRight, lsbBotRight, tst, bRFill = 0)

    #Tile Templates Bottom Right Square
    bottomRightSquareMod.join(2, S, msbBotRight, topG, tst, gSig = "G")
    bottomRightSquareMod.join(1, S, intBotRight, topH,tst, hFill = "h")
    bottomRightSquareMod.join(1, S, intBotRight, fillerH,tst, hFill = "h")
    bottomRightSquareMod.join(2, S, topH, topG,tst, gSig = "G")
    bottomRightSquareMod.join(1, W, topG, topH,tst, iSig = "i")
    bottomRightSquareMod.join(1, S, topG, fillerG,tst, gFill = "g")
    bottomRightSquareMod.join(1, E, topG, fillerG,tst, gFillHoriz = "g")
    bottomRightSquareMod.join(1, S, fillerG, fillerG, tst, gFill = "g")
    bottomRightSquareMod.join(1, E, fillerG, fillerG,tst, gFillHoriz = "g")
    bottomRightSquareMod.join(1, S, fillerH, topH,tst, hFill = "h")
    bottomRightSquareMod.join(1, W, topH, fillerH,tst, hFillHoriz = "h")
    bottomRightSquareMod.join(1, S, fillerH, fillerH,tst, hFill = "h")
    bottomRightSquareMod.join(1, W, fillerH, fillerH,tst, hFillHoriz = "h")
    bottomRightSquareMod.join(1, W, fillerH, intBotRightFill,tst, hFillHoriz = "h")
    bottomRightSquareMod.join(1, W, topH, intBotRightFill,tst, hFillHoriz = "h")
    bottomRightSquareMod.join(1, W, topG, msbBotRightFill,tst, iSig = "i")
    bottomRightSquareMod.join(1, S, lsbBotRight, intBotRightFill, tst, lMS = 0)
    bottomRightSquareMod.join(1, S, intBotRightFill, intBotRightFill, tst, lMS = 0)
    bottomRightSquareMod.join(1, S, intBotRightFill, msbBotRightFill, tst, lMS = 0)

    return bottomRightSquareMod

#From Ports for bottom left module
msbPortFrom = tam2.initiatorPort("msbPortFrom", 2, False)
interiorPortFrom = tam2.Port("interorPortFrom")
lsbPortFrom = tam2.Port("lsbPortFrom")

#To Ports for left transition Module
msbPortTo = tam2.initiatorPort("msbPortTo", 2, True)
interiorPortTo = tam2.Port("interorPortTo")
lsbPortTo = tam2.Port("lsbPortTo")
def bottomLogToLeftTransPortJoins(mod1,root,mod2,tst):
    mod1.add_port(msbPortFrom, N)
    mod1.add_port(interiorPortFrom, N)
    mod1.add_port(lsbPortFrom, N)

    mod2.add_port(msbPortTo, N)
    mod2.add_port(interiorPortTo, N)
    mod2.add_port(lsbPortTo, N)

    #Joins for Ports on Bottom Left Module
    mod1.join(2, N, msbTrans, msbPortFrom, tst, transToPortMsb = 0)
    mod1.join(1, N, interiorTrans, interiorPortFrom, tst, transToPortInt = 0)
    mod1.join(1, N, lsbTrans, lsbPortFrom, tst, transToPortLsb = 0)

    # Joins for Ports in between bottom left module and left transition module
    root.join(2, N, msbPortFrom, msbPortTo, tst, transToPortMsb = 0)
    root.join(1, N, interiorPortFrom, interiorPortTo, tst, transToPortInt = 0)
    root.join(1, N, lsbPortFrom, lsbPortTo, tst, transToPortLsb = 0)

    # Joins for Ports to beginning tiles of left transition module
    mod2.join(2, N, msbPortTo, msbTransSeed, tst, transToPortMsb = 0)
    mod2.join(1, N, interiorPortTo, interiorTransSeed, tst, transToPortInt = 0 )
    mod2.join(1, N, lsbPortTo, lsbTransSeed, tst, transToPortLsb = 0)


#From Ports for Left Transition Module
lsbFlipPortFrom = tam2.initiatorPort("lsbFlipPortFrom", 2, False)
interiorFlipPortFrom = tam2.Port("interiorFlipPortFrom")
msbFlipPortFrom = tam2.Port("msbFlipPortFrom")

#To Ports for Top Grow Module
lsbFlipPortTo = tam2.initiatorPort("lsbFlipPortTo", 2, True)
interiorFlipPortTo = tam2.Port("interiorFlipPortTo")
msbFlipPortTo = tam2.Port("msbFlipPortTo")
def leftTransToTopGrowPortJoins(mod1,root,mod2,tst):

    mod1.add_port(msbFlipPortFrom, E)
    mod1.add_port(interiorFlipPortFrom, E)
    mod1.add_port(lsbFlipPortFrom, E)

    #top grow module
    mod2.add_port(msbFlipPortTo, E)
    mod2.add_port(interiorFlipPortTo, E)
    mod2.add_port(lsbFlipPortTo, E)

     #Joins for From Ports for Left Transition Module
    mod1.join(2, E, lsbTransSeed, lsbFlipPortFrom, tst, lsbPortTop = 0)
    mod1.join(1, E, interiorFlipperSeed, interiorFlipPortFrom, tst, intPortTop = 0)
    mod1.join(1, E, msbFlipperSeed, msbFlipPortFrom, tst, msbPortTop = 0)

    #Joins between From and To Ports between left transition and top grow modules
    root.join(2, E, lsbFlipPortFrom, lsbFlipPortTo, tst, lsbPortTop = 0)
    root.join(1, E, interiorFlipPortFrom, interiorFlipPortTo, tst, intPortTop = 0)
    root.join(1, E, msbFlipPortFrom, msbFlipPortTo, tst, msbPortTop = 0)

    #Joins between To Ports and beginning tile Templates of Top Grow Module
    mod2.join(2, E, lsbFlipPortTo, lsbPortTop, tst, lsbPortTop = 0)
    mod2.join(1, E, msbFlipPortTo, msbPortTop, tst, msbPortTop = 0)
    mod2.join(1, E, interiorFlipPortTo, interiorPortTop, tst, intPortTop = 0)

#From Ports for Top Grow Module
msbTopPortFrom = tam2.initiatorPort("msbTopPortFrom", 2, False)
interiorTopPortFrom = tam2.Port("interiorTopPortFrom")
lsbTopPortFrom = tam2.Port("lsbTopPortFrom")

#To Ports for Right Transition Module
msbTopPortTo = tam2.initiatorPort("msbTopPortTo", 2, True)
interiorTopPortTo = tam2.Port("interiorTopPortTo")
lsbTopPortTo = tam2.Port("lsbTopPortTo")
def topGrowToRightTransPortJoins(mod1,root,mod2,tst):
    mod1.add_port(msbTopPortFrom, E)
    mod1.add_port(lsbTopPortFrom, E)
    mod1.add_port(interiorTopPortFrom, E)

    #Right Transition Module
    mod2.add_port(msbTopPortTo, E)
    mod2.add_port(interiorTopPortTo, E)
    mod2.add_port(lsbTopPortTo, E)

    #Joins for the From Ports in Top Grow Module
    mod1.join(2, E, msbTransTop, msbTopPortFrom, tst, msbTopPort = "mTP")
    mod1.join(1, E, intTransTop, interiorTopPortFrom, tst, intTopPort = "iTP")
    mod1.join(1, E, lsbTransTop, lsbTopPortFrom, tst, lsbTopPort = "lTP")

    #Joins between Ports for Top Grow and Right Transition Modules
    root.join(2, E, msbTopPortFrom, msbTopPortTo, tst, msbTopPort = "mTP")
    root.join(1, E, interiorTopPortFrom, interiorTopPortTo, tst, intTopPort = "iTP")
    root.join(1, E, lsbTopPortFrom, lsbTopPortTo, tst, lsbTopPort = "lTP")

    #Joins for To Ports in Right Transition Module
    mod2.join(2, E, msbTopPortTo, msbStartSeed, tst, msbTopPort = "mTP")
    mod2.join(1, E, interiorTopPortTo, intStartSeed, tst, intTopPort = "iTP")
    mod2.join(1, E, lsbTopPortTo, lsbStartSeed, tst, lsbTopPort = "lTP")

#Right Transition Module From Ports
msbRightTransPort = tam2.initiatorPort("msbRightTransPort", 2, False)
intRightTransPort = tam2.Port("intRightTransPort")
lsbRightTransPort = tam2.Port("lsbRightTransPort")

#Bottom Right Square Module To Ports
msbBotRightPort = tam2.initiatorPort("msbBotRightPort", 2, True)
intBotRightPort = tam2.Port("intBotRightPort")
lsbBotRightPort = tam2.Port("lsbBotRightPort")
def rightTransToBottomRightPortJoins(mod1,root,mod2,tst):
    mod1.add_port(msbRightTransPort, S)
    mod1.add_port(lsbRightTransPort, S)
    mod1.add_port(intRightTransPort, S)

    #Bottom Right Square Module
    mod2.add_port(msbBotRightPort, S)
    mod2.add_port(lsbBotRightPort, S)
    mod2.add_port(intBotRightPort, S)

    #From Ports Right Transition Module
    mod1.join(2, S, msbFlipStartSeed, msbRightTransPort, tst, mrTP = 0)
    mod1.join(1, S, intFlipStartSeed, intRightTransPort, tst, irTP = 0)
    mod1.join(1, S, lsbStartSeed, lsbRightTransPort, tst, lrTP = 0)

    #From to To Ports
    root.join(2, S, msbRightTransPort, msbBotRightPort, tst, mrTP = 0)
    root.join(1, S, intRightTransPort, intBotRightPort, tst, irTP = 0)
    root.join(1, S, lsbRightTransPort, lsbBotRightPort, tst, lrTP = 0)

    #To Ports Bottom Right Square
    mod2.join(2, S, msbBotRightPort, msbBotRight, tst, mrTP = 0)
    mod2.join(1, S, intBotRightPort, intBotRight, tst, irTP = 0)
    mod2.join(1, S, lsbBotRightPort, lsbBotRight, tst, lrTP = 0)

def createTiles(module,tileSetTemplate, filename):
    tiles = module.createTiles(tst)
    tileSystem = tam2.TileSystem(filename,tiles)
    tileSystem.writeToFiles(filename)


if __name__ == '__main__':
    #create mandatory tile set template
    tst = tam2.TileSetTemplate()

    #create root module
    rootMod = tam2.Module("rootMod")

    #function for each module to initialize them as well as there joins and tile templates
    bottomLogGrowMod = createBottomLogGrowMod("bottomLogGrowMod", tst)
    leftTransitionMod = createLeftTransitionMod("leftTransitionMod", tst)
    topGrowMod = createTopGrowMod("topGrowMod", tst)
    rightTransitionMod = createRightTransitionMod("rightTRansitionMod",tst )
    bottomRightSquareMod = createBottomRightSquareMod("bottomRightSquareMod",tst)

    #add modules to root module
    rootMod.add(bottomLogGrowMod)
    rootMod.add(leftTransitionMod)
    rootMod.add(topGrowMod)
    rootMod.add(rightTransitionMod)
    rootMod.add(bottomRightSquareMod)

    #function to create port joins for modules
    bottomLogToLeftTransPortJoins(bottomLogGrowMod,rootMod,leftTransitionMod,tst)
    leftTransToTopGrowPortJoins(leftTransitionMod, rootMod,topGrowMod,tst)
    topGrowToRightTransPortJoins(topGrowMod, rootMod, rightTransitionMod,tst)
    rightTransToBottomRightPortJoins(rightTransitionMod, rootMod, bottomRightSquareMod,tst)

    #function to create tiles - simply pass it in each module
    createTiles(bottomLogGrowMod, tst, "gamma1")
    createTiles(leftTransitionMod, tst, "gamma2")
    createTiles(topGrowMod, tst, "gamma3")
    createTiles(rightTransitionMod, tst, "gamma4")
    createTiles(bottomRightSquareMod, tst, "gamma5")
