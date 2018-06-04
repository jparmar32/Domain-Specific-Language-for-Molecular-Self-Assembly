'''
Created on Jul 7, 2017

@author: jupiparmar1
'''
import tam3

N = tam3.Direction.North
S = tam3.Direction.South
E = tam3.Direction.East
W = tam3.Direction.West

def addTileTemplatesToModule(tileTempList, module):
    for tile in tileTempList:
        module.add(tile)
def createTiles(module,tileSetTemplate, filename):
    tiles = module.createTiles(tst)
    tileSystem = tam3.TileSystem(filename,tiles)
    tileSystem.writeToFiles(filename)

leftSeedTuringCont = tam3.TileTemplate("leftSeedTuringCont")
middleSeedTuringCont = tam3.TileTemplate("middleSeedTuringCont")
rightSeedTuringCont = tam3.TileTemplate("rightSeedTuringCont")

seedLeft = tam3.TileTemplate("seedLeft")
seedMiddle = tam3.TileTemplate("seedMiddle")
seedRight = tam3.TileTemplate("seedRight")

transToPortLeft = tam3.TileTemplate("transToPortLeft")
transToPortMiddle = tam3.TileTemplate("transToPortMiddle")
transToPortRight = tam3.TileTemplate("transToPortRight")
leftFillerSignificant = tam3.TileTemplate("leftFillerSignificant")
def createTuringMod(name,tst):
    turingMod = tam3.Module(name)


    mainTM = tam3.TileTemplate("mainTM")
    transTM = tam3.TileTemplate("transTM")
    rightFiller = tam3.TileTemplate("rightFiller")

    leftFiller = tam3.TileTemplate("leftFiller")
    endMainTM = tam3.TileTemplate("endMainTM")
    extendLine = tam3.TileTemplate("extendLine")
    tiles = [mainTM,transTM,rightFiller,leftFiller,leftFillerSignificant,endMainTM,extendLine,leftSeedTuringCont,middleSeedTuringCont,rightSeedTuringCont,seedLeft,seedMiddle,seedRight,transToPortLeft,transToPortMiddle,transToPortRight]
    addTileTemplatesToModule(tiles, turingMod)

    extendToBotTran = tam3.TileTemplate("extendToBotTran")
    toBotFill = tam3.TileTemplate("toBotFill")
    toBotSkipModPre = tam3.TileTemplate("toBotSkipModPre")
    toBotSkipMod = tam3.TileTemplate("toBotSkipMod")
    toBotSkipBottomModPre = tam3.TileTemplate("toBotSkipModPre")
    toBotSkipBottomMod = tam3.TileTemplate("toBotSkipMod")

    turingMod.add(extendToBotTran)
    turingMod.add(toBotFill)
    turingMod.add(toBotSkipModPre)
    turingMod.add(toBotSkipMod)
    turingMod.add(toBotSkipBottomModPre)
    turingMod.add(toBotSkipBottomMod)

    turingMod.join(1, E, seedLeft, seedMiddle, tst, seed = "seed1")
    turingMod.join(1, E, seedMiddle, seedRight, tst, seed2 = "seed2")


    turingMod.join(2, N, seedLeft, mainTM, tst, tmSig = "q10*")
    turingMod.join(1, N, seedMiddle, transTM, tst, nextSig = "0")
    turingMod.join(1, N, seedMiddle, rightFiller, tst, nextSig = "0")
    turingMod.join(1, N, seedRight, rightFiller, tst, nextSig = "-")

    turingMod.join(1, E, leftSeedTuringCont, middleSeedTuringCont, tst, midCont = "midCont")
    turingMod.join(1, E, middleSeedTuringCont, middleSeedTuringCont, tst, midCont = "midCont")
    turingMod.join(1, E, middleSeedTuringCont, rightSeedTuringCont, tst, midCont = "midCont")


    turingMod.join(2, N, leftSeedTuringCont, mainTM, tst, tmSig = "q10*")
    turingMod.join(1, N, middleSeedTuringCont, transTM, tst, nextSig = "0")
    turingMod.join(1, N, middleSeedTuringCont, rightFiller, tst, nextSig = "0")
    turingMod.join(1, N, rightSeedTuringCont, rightFiller, tst, nextSig = "-")

    #Joins for TM
    turingMod.join(1, E, mainTM, transTM, tst, nextState = ("q1","q2"))
    turingMod.join(1, N, mainTM, leftFillerSignificant, tst, lSigUp = "F*")
    turingMod.join(1, N, mainTM, leftFiller, tst, lSigUp = "F")
    turingMod.join(1, W, mainTM, leftFillerSignificant, tst, lSigWest = "L")
    turingMod.join(1, W, mainTM, leftFiller, tst, lSigWest = "L")

    turingMod.join(1, N, rightFiller, transTM, tst, nextSig = ("0","-"))
    turingMod.join(2, N, transTM, mainTM, tst, tmSig = ("q20","q10"))
    turingMod.join(2, N, transTM, endMainTM, tst, tmSig = ("q1-","q2-"))
    turingMod.join(1, E, transTM, rightFiller, tst, rSigEast = "R")

    #Joins For Right Filler
    turingMod.join(1, E, rightFiller, rightFiller, tst, rSigEast = "R")
    turingMod.join(1, N, rightFiller, rightFiller, tst, nextSig = ("0","-"))

    #Joins For Left Filler
    turingMod.join(1, W, leftFiller, leftFiller, tst, lSigWest = "L")
    turingMod.join(1, W, leftFiller, leftFillerSignificant, tst, lSigWest = "L")
    turingMod.join(1, N, leftFiller, leftFiller, tst, lSigUp = "F")
    turingMod.join(1, N, leftFiller, transToPortMiddle, tst, lSigUp = "F")

    #Joins For Left Filler Significant
    turingMod.join(1, N, leftFillerSignificant, leftFillerSignificant, tst, lSigUp = "F*")
    turingMod.join(1, N, leftFillerSignificant, transToPortLeft, tst, lSigUp = "F*")

    #Joins for End TM Main
    turingMod.join(1, W, endMainTM, leftFiller, tst, lSigWest = "L")
    turingMod.join(2, E, endMainTM, extendLine, tst, extendSig = ("R","A"))
    turingMod.join(1, N, endMainTM, transToPortMiddle, tst, lSigUp = "F")

    #Joins for trans to port tiles
    turingMod.join(2, N, extendLine, transToPortRight, tst, endSig = ("R-","A-"))
    turingMod.join(1, W, transToPortRight, transToPortMiddle, tst, transHorizSig = "L1")
    turingMod.join(1, W, transToPortMiddle, transToPortMiddle, tst, transHorizSig = "L1")
    turingMod.join(1, W, transToPortMiddle, transToPortLeft, tst, transHorizSig = "L1")

    turingMod.join(2, S, extendLine, extendToBotTran, tst, extToBot = ("tbA","tbR"))
    turingMod.join(1, S, extendToBotTran, toBotFill, tst, extToBotF = ("tbA","tbR"))
    turingMod.join(1, S, toBotFill, toBotFill, tst, extToBotF = ("tbA","tbR"))
    turingMod.join(1, E, rightFiller, toBotFill, tst, rSigEast = "R")
    turingMod.join(1, E, transToPortRight, toBotFill, tst, rSigEast = "R")
    turingMod.join(1, E, extendLine, toBotFill, tst, rSigEast = "R")
    turingMod.join(1, E, extendToBotTran, toBotFill, tst, rSigEast = "R")
    turingMod.join(1, E, toBotFill, toBotFill, tst, rSigEast = "R")
    turingMod.join(1, E, toBotSkipMod, toBotFill, tst, rSigEast = "R")
    turingMod.join(1, E, toBotSkipModPre, toBotFill, tst, rSigEast = "R")
    turingMod.join(1, S, toBotFill, toBotSkipModPre, tst, extToBotF = ("tbA","tbR"))
    turingMod.join(1, E, rightSeedTuringCont, toBotSkipModPre, tst, skipSig = "sS")
    turingMod.join(2, S, toBotSkipModPre, toBotSkipMod, tst, extToBotSkip = ("tbA","tbR"))
    turingMod.join(1, S, toBotSkipMod, toBotFill, tst, extToBotF = ("tbA","tbR"))
    turingMod.join(1, E, seedRight, toBotSkipBottomModPre, tst, botSkip = "bS")
    turingMod.join(1, S, toBotFill, toBotSkipBottomModPre, tst, extToBotF = ("tbA","tbR"))
    turingMod.join(2, S, toBotSkipBottomModPre, toBotSkipBottomMod, tst, extToBotSkipBottom = ("A","R"))
    turingMod.join(1, E, toBotSkipBottomModPre, toBotSkipBottomModPre, tst, botSkip = "bS")


    mainTM.addTransition(inputs=("tmSig"), outputs=("nextState","lSigUp","lSigWest"),table={("q10*",):("q2","F*","L"), ("q10",):("q2","F","L"), ("q20",):("q1","F","L")})
    transTM.addTransition(inputs=("nextState","nextSig"), outputs=("tmSig", "rSigEast"),table={("q1","0"):("q10","R"), ("q2","0"):("q20","R"), ("q2","-"):("q2-","R"), ("q1","-"):("q1-","R")})
    rightFiller.addTransition(inputs=("rSigEast","nextSig"), outputs=("rSigEast", "nextSig"),table={("R","0"):("R","0"), ("R","-"):("R","-")})
    endMainTM.addTransition(inputs=("tmSig"), outputs=("extendSig","lSigUp","lSigWest"),table={("q1-",):("A","F","L"), ("q2-",):("R","F","L")})
    extendLine.addTransition(inputs=("extendSig"), outputs=("endSig","extToBot","rSigEast"),table={("R",):("R-","tbR",'R'), ("A",):("A-","tbA","R")})
    transToPortRight.addTransition(inputs=("endSig"), outputs=("portContRight"),table={("R-",):("R-"), ("A-",):("A-")})
    extendToBotTran.addTransition(inputs=("extToBot"), outputs=("extToBotF","rSigEast"),table={("tbA",):("tbA","R"), ("tbR",):("tbR","R")})
    toBotFill.addTransition(inputs=("extToBotF","rSigEast"), outputs=("extToBotF","rSigEast"),table={("tbA","R"):("tbA","R"), ("tbR","R"):("tbR","R")})
    toBotSkipModPre.addTransition(inputs=("extToBotF","skipSig"), outputs=("extToBotSkip","rSigEast"),table={("tbA","sS"):("tbA","R"), ("tbR","sS"):("tbR","R")})
    toBotSkipMod.addTransition(inputs=("extToBotSkip"), outputs=("extToBotF","rSigEast"),table={("tbA",):("tbA","R"), ("tbR",):("tbR","R")})
    toBotSkipBottomModPre.addTransition(inputs=("extToBotF", "botSkip"), outputs=("extToBotSkipBottom","botSkip"),table={("tbA","bS"):("A","bS"), ("tbR","bS"):("R","bS")})




    return turingMod

leftBeg = tam3.TileTemplate("leftBeg")
middleBeg = tam3.TileTemplate("middleBeg")
rightBeg = tam3.TileTemplate("rightBeg")

leftCont = tam3.TileTemplate("leftCont")
middleCont = tam3.TileTemplate("middleCont")
rightCont = tam3.TileTemplate("rightCont")
def createTransTuringMod(name,tst):
    transTuringMod = tam3.Module(name)
    tiles = [leftBeg,middleBeg,rightBeg,leftCont,middleCont,rightCont]
    addTileTemplatesToModule(tiles, transTuringMod)

    transTuringMod.join(2, E, leftBeg, middleBeg, tst, begSig = "b")
    transTuringMod.join(2, E, middleBeg, rightBeg, tst, rbegSig = "rb")

    transTuringMod.join(1, E, leftCont, middleCont, tst, contSigM = "cSM")
    transTuringMod.join(1, E, middleCont, middleCont, tst, contSigM = "cSM")
    transTuringMod.join(1, E, middleCont, rightCont, tst, contSigM = "cSM")

    return transTuringMod


botFillTile = tam3.TileTemplate("botFill")
topPreSkip = tam3.TileTemplate("topPreSkip")
rightFillLeft = tam3.TileTemplate("rightFillLeft")
contLeftStart = tam3.TileTemplate("contLeftStart")
contLeftStartTwo = tam3.TileTemplate("contLeftStartTwo")
initialTile = tam3.TileTemplate("initialTile")
def createLeftCounterMod(name,tst):
    leftCounterMod = tam3.Module(name)

    skipTile = tam3.TileTemplate("skipTile")



    extendTileLeft = tam3.TileTemplate("extendTileLeft")
    leftFillLeft = tam3.TileTemplate("leftFillLeft")
    middleFillLeft = tam3.TileTemplate("middleFillLeft")

    shiftToExtend = tam3.TileTemplate("shiftToExtend")
    topFillLine = tam3.TileTemplate("topFillLine")
    topSkip = tam3.TileTemplate("TopSkip")

    tiles = [botFillTile,topPreSkip,rightFillLeft,contLeftStart,contLeftStartTwo,initialTile, skipTile, extendTileLeft, leftFillLeft, middleFillLeft, shiftToExtend, topFillLine, topSkip]
    addTileTemplatesToModule(tiles, leftCounterMod)

    leftCounterMod.join(2, N, initialTile, skipTile, tst, skipBotSig = "sBS")
    leftCounterMod.join(1, N, skipTile, botFillTile, tst, skipBotSigFill = "sBSF")
    leftCounterMod.join(1, N, botFillTile, botFillTile, tst, skipBotSigFill = "sBSF")
    leftCounterMod.join(1, N, botFillTile, contLeftStart, tst, skipBotSigFill = "sBSF")
    leftCounterMod.join(2, W, contLeftStart, extendTileLeft, tst, extendSig = "eS")
    leftCounterMod.join(1, N, contLeftStart, topPreSkip, tst, toTopPreSkip = "tTPS")
    leftCounterMod.join(1, N, contLeftStartTwo, topPreSkip, tst, toTopPreSkip = "tTPS")
    leftCounterMod.join(2, N, topPreSkip,topSkip , tst, topSkipSigSKip = "tSSS")
    leftCounterMod.join(1, N, topFillLine,middleFillLeft , tst, topSkipSig = "tSS")
    leftCounterMod.join(1, N, shiftToExtend,middleFillLeft , tst, topSkipSig = "tSS")
    leftCounterMod.join(1, N, extendTileLeft,leftFillLeft , tst, leftMostSig = "lMS")
    leftCounterMod.join(1, N, leftFillLeft,leftFillLeft , tst, leftMostSig = "lMS")
    leftCounterMod.join(1, W, topSkip, leftFillLeft , tst, horizFill = "hF")
    leftCounterMod.join(1, W, rightFillLeft, leftFillLeft , tst, horizFill = "hF")
    leftCounterMod.join(1, N, topSkip,rightFillLeft , tst, topSkipSig = "tSS")
    leftCounterMod.join(1, N, rightFillLeft,rightFillLeft , tst, topSkipSig = "tSS")
    leftCounterMod.join(1, W, rightFillLeft, middleFillLeft , tst, horizFill = "hF")
    leftCounterMod.join(1, W, middleFillLeft, middleFillLeft , tst, horizFill = "hF")
    leftCounterMod.join(1, W, topPreSkip, middleFillLeft , tst, horizFill = "hF")
    leftCounterMod.join(1, W, topPreSkip, leftFillLeft , tst, horizFill = "hF")
    leftCounterMod.join(1, W, middleFillLeft, leftFillLeft , tst, horizFill = "hF")
    leftCounterMod.join(1, N, rightFillLeft,contLeftStartTwo , tst, topSkipSig = "tSS")
    leftCounterMod.join(1, N, middleFillLeft,middleFillLeft , tst, topSkipSig = "tSS")
    leftCounterMod.join(1, N, middleFillLeft,topFillLine , tst, topSkipSig = "tSS")
    leftCounterMod.join(1, N, leftFillLeft,shiftToExtend , tst, leftMostSig = "lMS" )
    leftCounterMod.join(1, W, contLeftStartTwo,topFillLine , tst, topFillSig = "tFS")
    leftCounterMod.join(1, W, topFillLine,topFillLine , tst, topFillSig = "tFS")
    leftCounterMod.join(1, W, topFillLine,shiftToExtend , tst, topFillSig = "tFS")
    leftCounterMod.join(2, W, shiftToExtend, extendTileLeft, tst, extendSig = "eS")

    return leftCounterMod


def createBringResultMod(name,tst):
    pass
def createBottomMod(name,tst):
    pass
portToContLeft = tam3.Port("portToContLeft")
portToContMid = tam3.Port("portToContMid")
portToContRight = tam3.Port("portToContRight")

portFromContLeft = tam3.Port("portFormContLeft")
portFromContMid = tam3.Port("portFromContMid")
portFromContRight = tam3.Port("portFromContRight")
def fromTuringToTransPorts(mod1, root, mod2, tst):
    mod1.add_port(portToContLeft, N)
    mod1.add_port(portToContMid, N)
    mod1.add_port(portToContRight, N)


    mod2.add_port(portFromContLeft, N)
    mod2.add_port(portFromContMid, N)
    mod2.add_port(portFromContRight, N)

    mod1.join(2, N, transToPortLeft, portToContLeft, tst, portContLeft = "0*")
    mod1.join(1, N, transToPortMiddle, portToContMid, tst, portContMid = "0")
    mod1.join(1, N, transToPortRight, portToContRight, tst, portContRight = ("R-","A-"))

    root.join(2, N, portToContLeft, portFromContLeft, tst, portContLeft = "0*")
    root.join(1, N, portToContMid, portFromContMid, tst, portContMid = "0")
    root.join(1, N, portToContRight, portFromContRight, tst, portContRight = ("R-","A-"))

    mod2.join(2, N, portFromContLeft, leftCont, tst, portContLeft = "0*")
    mod2.join(1, N, portFromContMid, middleCont, tst, portContMid = "0")
    mod2.join(1, N, portFromContRight, rightCont, tst, portContRight = ("R-","A-"))

portToContTuringLeft = tam3.Port("portToContTuringLeft")
portToContTuringMid = tam3.Port("portToContTuringMid")
portToContTuringRight = tam3.Port("portToContTuringRight")

portFromContTuringLeft = tam3.Port("portFormContTuringLeft")
portFromContTuringMid = tam3.Port("portFromContTuringMid")
portFromContTuringRight = tam3.Port("portFromContTuringRight")
def fromTransToTuringPorts(mod1, root, mod2, tst):
    mod1.add_port(portToContTuringLeft, N)
    mod1.add_port(portToContTuringMid, N)
    mod1.add_port(portToContTuringRight, N)


    mod2.add_port(portFromContTuringLeft, N)
    mod2.add_port(portFromContTuringMid, N)
    mod2.add_port(portFromContTuringRight, N)

    mod1.join(2, N, leftCont, portToContTuringLeft, tst, portContTuringLeft = "0*")
    mod1.join(1, N, middleCont, portToContTuringMid, tst, portContTuringMid = "0")
    mod1.join(1, N, rightCont, portToContTuringRight, tst, portContTuringRight = "-")

    root.join(2, N, portToContTuringLeft, portFromContTuringLeft, tst, portContTuringLeft = "0*")
    root.join(1, N, portToContTuringMid, portFromContTuringMid, tst, portContTuringMid = "0")
    root.join(1, N, portToContTuringRight, portFromContTuringRight, tst,portContTuringRight = "-")

    mod2.join(2, N, portFromContTuringLeft, leftSeedTuringCont, tst, portContTuringLeft = "0*")
    mod2.join(1, N, portFromContTuringMid, middleSeedTuringCont, tst, portContTuringMid = "0")
    mod2.join(1, N, portFromContTuringRight, rightSeedTuringCont, tst, portContTuringRight = "-")


portToLeftMost = tam3.Port("portToLeftMost")
portToMiddleMost = tam3.Port("portToMiddleMost")
portToRightMost = tam3.Port("portToRightMost")

portFromLeftMost = tam3.Port("portFromLeftMost")
portFromMiddleMost = tam3.Port("portFromMiddleMost")
portFromRightMost = tam3.Port("portFromRightMost")
def fromTransToTuringInitialPorts(mod1, root, mod2, tst):
    mod1.add_port(portToLeftMost, N)
    mod1.add_port(portToMiddleMost, N)
    mod1.add_port(portToRightMost, N)


    mod2.add_port(portFromLeftMost, N)
    mod2.add_port(portFromMiddleMost, N)
    mod2.add_port(portFromRightMost, N)

    mod1.join(2, N, leftBeg, portToLeftMost, tst, portToLeft = "pTL")
    mod1.join(1, N, middleBeg, portToMiddleMost, tst, portToMiddle = "pTM")
    mod1.join(1, N, rightBeg, portToRightMost, tst, portToRight = "pTR")

    root.join(2, N, portToLeftMost, portFromLeftMost, tst, portToLeft = "pTL")
    root.join(1, N,  portToMiddleMost, portFromMiddleMost, tst, portToMiddle = "pTM")
    root.join(1, N, portToRightMost, portFromRightMost, tst, portToRight = "pTR")

    mod2.join(2, N, portFromLeftMost, seedLeft, tst, portToLeft = "pTL")
    mod2.join(1, N,  portFromMiddleMost, seedMiddle, tst, portToMiddle = "pTM")
    mod2.join(1, N, portFromRightMost, seedRight, tst, portToRight = "pTR")

portFromContLeftTuringToLeft = tam3.Port("portFromContLeftTuringToLeft")
portToContLeftTuringToLeft = tam3.Port("portToContLeftToLeft")
def fromTransTuringToLeftCounterPorts(mod1, root, mod2, tst):
    mod1.add_port(portFromContLeftTuringToLeft, W)
    mod2.add_port(portToContLeftTuringToLeft, W)

    mod1.join(1, W, leftCont, portFromContLeftTuringToLeft, tst, toContLeft = "tCL")


    root.join(1, W, portFromContLeftTuringToLeft, portToContLeftTuringToLeft, tst, toContLeft = "tCL")


    mod2.join(1, W, portToContLeftTuringToLeft, contLeftStart, tst, toContLeft = "tCL")
    mod2.join(1, W, portToContLeftTuringToLeft, contLeftStartTwo, tst, toContLeft = "tCL")

portFromSeedLeft = tam3.Port("portFromSeedLeft")
portToInitTile = tam3.Port("portToInitTile")

portFromTuringFill = tam3.Port("portFromTuringFill")
portToLeftFill = tam3.Port("portToLeftFill")
def fromTuringToLeftCounterPorts(mod1, root, mod2, tst):
    mod1.add_port(portFromSeedLeft, W)
    mod1.add_port(portFromTuringFill, W)

    mod2.add_port(portToInitTile, W)
    mod2.add_port(portToLeftFill, W)

    mod1.join(2, W, seedLeft, portFromSeedLeft, tst, toInitLeft = "tIL")

    root.join(2, W, portFromSeedLeft, portToInitTile, tst, toInitLeft = "tIL")

    mod2.join(2, W, portToInitTile, initialTile, tst, toInitLeft = "tIL")

    mod1.join(1, W, transToPortLeft, portFromTuringFill, tst, toBotLeftFill = "tBLF")
    mod1.join(1, W, leftFillerSignificant, portFromTuringFill, tst, toBotLeftFill = "tBLF")
    mod1.join(1, W, leftSeedTuringCont, portFromTuringFill, tst, toBotLeftFill = "tBLF")

    root.join(1, W, portFromTuringFill, portToLeftFill, tst, toBotLeftFill = "tBLF")

    mod2.join(1, W, portToLeftFill, botFillTile, tst, toBotLeftFill = "tBLF")
    mod2.join(1, W, portToLeftFill, rightFillLeft, tst, toBotLeftFill = "tBLF")
    mod2.join(1, W, portToLeftFill, topPreSkip, tst, toBotLeftFill = "tBLF")
if __name__ == '__main__':
    #create mandatory tile set template
    tst = tam3.TileSetTemplate()

    #create root module
    rootMod = tam3.Module("rootMod")

    alphabet = ['0','1','_']

    # The list of state names of the TM
    states = [ 'q1', 'q2', 'qA', 'qR']

    startState  = 'q1'  # The state in which the machine starts
    acceptState = 'qA'  # The state into which the machine moves in order to halt and accept
    rejectState = 'qR'  # The state into which the machine moves in order to halt and reject

    # A full transition table mapping every input in every state to an output symbol, direction, and state
    transitions =  {('q1', '0'):("q2","0","R"),
                    ("q2","0"):("q1","0","R"),
                    ("q1","*0"):("q2","*0","R"),
                    ("q2","*0"):("q1","*0","R"),
                    ("q1","-"):("qA","qA","S"),
                    ("q2","-"):("qR", "qR","S")}

    #function for each module to initialize them as well as there joins and tile templates
    turingMod = createTuringMod("turingMod", tst)
    transTuringMod = createTransTuringMod("transTuringMod", tst)
    leftCounterMod = createLeftCounterMod("leftCounterMod", tst)
    bringResultMod = createBringResultMod("bringResultMod",tst)
    bottomMod = createBottomMod("bottomMod", tst)

    #add modules to root module
    rootMod.add(turingMod)
    rootMod.add(transTuringMod)
    rootMod.add(leftCounterMod)

    #function to create port joins for modules
    fromTuringToTransPorts(turingMod, rootMod, transTuringMod, tst)
    fromTransToTuringPorts(transTuringMod, rootMod, turingMod, tst)
    fromTransToTuringInitialPorts(transTuringMod, rootMod, turingMod, tst)
    fromTuringToLeftCounterPorts(turingMod, rootMod, leftCounterMod, tst)
    fromTransTuringToLeftCounterPorts(transTuringMod, rootMod, leftCounterMod, tst)

    #function to create tiles - simply pass it in each module
    createTiles(turingMod, tst, "module_Infinite_Turing1")
    createTiles(transTuringMod, tst, "module_Infinite_Turing2")
    createTiles(leftCounterMod, tst, "module_Infinite_Turing3")
